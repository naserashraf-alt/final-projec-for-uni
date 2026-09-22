import requests
import json
import re
import os
import sys
import time

# Ensure UTF-8 output encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def clean_html(text: str) -> str:
    """Removes HTML tags and normalizes whitespace."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def fetch_remotive_jobs() -> list:
    """Fetch live jobs across multiple tech categories from Remotive API."""
    categories = ["software-dev", "data", "devops-sysadmin", "qa", "design", "product"]
    all_jobs = []
    seen_ids = set()
    
    print("[1/2] Fetching live jobs from Remotive API across all tech categories...")
    
    for category in categories:
        url = f"https://remotive.com/api/remote-jobs?category={category}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("jobs", [])
                
                added = 0
                for job in jobs:
                    job_id = f"remotive_{job.get('id')}"
                    if job_id not in seen_ids:
                        seen_ids.add(job_id)
                        raw_desc = job.get("description", "")
                        
                        all_jobs.append({
                            "job_id": job_id,
                            "title": job.get("title", "").strip(),
                            "company": job.get("company_name", "").strip(),
                            "location": job.get("candidate_required_location", "Remote"),
                            "category": category,
                            "original_description": raw_desc,
                            "cleaned_description": clean_html(raw_desc),
                            "job_type": job.get("job_type", "Full-time"),
                            "source_url": job.get("url", ""),
                            "source_api": "Remotive",
                            "posted_at": job.get("publication_date", "")
                        })
                        added += 1
                print(f"  └ Category '{category}': fetched {added} new jobs.")
            time.sleep(0.5)  # Respectful delay
        except Exception as e:
            print(f"  └ [WARNING] Could not fetch category '{category}': {e}")
            
    print(f"✅ Total jobs fetched from Remotive: {len(all_jobs)}")
    return all_jobs

def fetch_arbeitnow_jobs(pages: int = 3) -> list:
    """Fetch live tech jobs from Arbeitnow Public Jobs API."""
    all_jobs = []
    seen_ids = set()
    
    print("\n[2/2] Fetching live tech jobs from Arbeitnow Global API...")
    
    for page in range(1, pages + 1):
        url = f"https://www.arbeitnow.com/api/job-board-api?page={page}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("data", [])
                
                added = 0
                for job in jobs:
                    job_slug = job.get("slug", "")
                    job_id = f"arbeitnow_{job_slug}"
                    if job_id not in seen_ids and job_slug:
                        seen_ids.add(job_id)
                        raw_desc = job.get("description", "")
                        tags = ", ".join(job.get("tags", []))
                        
                        full_desc = f"{raw_desc} Key Skills & Tags: {tags}" if tags else raw_desc
                        
                        all_jobs.append({
                            "job_id": job_id,
                            "title": job.get("title", "").strip(),
                            "company": job.get("company_name", "").strip(),
                            "location": "Remote" if job.get("remote") else job.get("location", "Global"),
                            "category": "tech",
                            "original_description": raw_desc,
                            "cleaned_description": clean_html(full_desc),
                            "job_type": ", ".join(job.get("job_types", [])) or "Full-time",
                            "source_url": job.get("url", ""),
                            "source_api": "Arbeitnow",
                            "posted_at": job.get("created_at", "")
                        })
                        added += 1
                print(f"  └ Page {page}: fetched {added} new jobs.")
            time.sleep(0.5)
        except Exception as e:
            print(f"  └ [WARNING] Could not fetch page {page} from Arbeitnow: {e}")
            
    print(f"✅ Total jobs fetched from Arbeitnow: {len(all_jobs)}")
    return all_jobs

def deduplicate_jobs(jobs_list: list) -> list:
    """Deduplicates jobs based on normalized Title + Company."""
    unique_jobs = []
    seen = set()
    
    for job in jobs_list:
        key = f"{job['title'].lower()}|{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
            
    return unique_jobs

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Multi-Source Live Job Data Collection")
    print("=" * 60)
    
    # 1. Fetch from Remotive API (Multi-category)
    remotive_jobs = fetch_remotive_jobs()
    
    # 2. Fetch from Arbeitnow API
    arbeitnow_jobs = fetch_arbeitnow_jobs(pages=3)
    
    # Combined & Deduplicate
    combined = remotive_jobs + arbeitnow_jobs
    final_jobs = deduplicate_jobs(combined)
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: Collected {len(combined)} raw jobs -> {len(final_jobs)} unique jobs.")
    print("=" * 60)
    
    # Save output
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "jobs_dataset.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_jobs, f, ensure_ascii=False, indent=4)
        
    print(f"[SUCCESS] Dataset saved to: {output_file}")
