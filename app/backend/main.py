
import asyncio
import os
import json
from utils.get_jobs.get_us_jobs import get_jobs_from_us
from utils.get_shifts.get_shifts import get_schedules_for_job
from utils.imports.constants import COMMON_HEADERS as headers
from utils.imports.check_token import is_token_valid

url = 'https://e5mquma77feepi2bdn4d6h3mpu.appsync-api.us-east-1.amazonaws.com/graphql'
EXTRACTED_JOBS_PATH = r"amazon-bot\app\backend\logs\extracted_jobs.json"

def load_extracted_jobs():
    if os.path.exists(EXTRACTED_JOBS_PATH):
        with open(EXTRACTED_JOBS_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_extracted_jobs(jobs):
    with open(EXTRACTED_JOBS_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

def job_info_from_card(job):
    info = {
        "jobId": job.get("jobId"),
        "jobTitle": job.get("jobTitle"),
        "jobType": job.get("jobType"),
        "employmentType": job.get("employmentType"),
        "city": job.get("city"),
        "state": job.get("state"),
        "postalCode": job.get("postalCode"),
        "locationName": job.get("locationName")
    }
    if info["jobType"] in ["FLEX_TIME;FULL_TIME", "FULL_TIME", "FLEX_TIME"]:
        schedules = get_schedules_for_job(info["jobId"])
        info["schedules"] = schedules if schedules else []
    return info

async def main_loop():
    # if not is_token_valid(headers.get('authorization')):
    #     print("Invalid token. Please update AUTH_TOKEN in constants.py.")
    #     return

    print("Starting job monitoring loop...")
    extracted_jobs = load_extracted_jobs()
    known_job_ids = {job["jobId"] for job in extracted_jobs}

    while True:
        try:
            result = get_jobs_from_us(url)
            job_cards = result["data"]["searchJobCardsByLocation"]["jobCards"]
            new_jobs = []
            for job in job_cards:
                job_id = job.get("jobId")
                if job_id and job_id not in known_job_ids:
                    info = job_info_from_card(job)
                    extracted_jobs.append(info)
                    known_job_ids.add(job_id)
                    new_jobs.append(info)
            if new_jobs:
                save_extracted_jobs(extracted_jobs)
                print(f"Added {len(new_jobs)} new jobs to extracted_jobs.json")
            else:
                print("No new jobs found.")
        except Exception as e:
            print(f"Error during job fetch: {e}")
        await asyncio.sleep(60)  # check every 60 seconds

if __name__ == "__main__":
    asyncio.run(main_loop())
