from utils.get_jobs.get_us_jobs import get_jobs_from_us
from utils.get_jobs.get_ca_jobs import get_jobs_from_ca
from utils.get_shifts.get_shifts import get_schedules_for_job
import json
from utils.imports.constants import COMMON_HEADERS as headers
from utils.imports.check_token import is_token_valid
import time
import requests

if(not is_token_valid(headers.get('authorization'))):
    #send notification to user to replace the AUTH_TOKEN in constants.py
    pass

# API endpoint
url = 'https://e5mquma77feepi2bdn4d6h3mpu.appsync-api.us-east-1.amazonaws.com/graphql'

result = get_jobs_from_us(url)

#full job reponse here
# with open("./logs/job_response.txt", "w", encoding="utf-8") as f:
#     f.write(f"Status Code: {result.get('statusCode')}\n")
#     f.write("Response:\n")
#     f.write(json.dumps(result, indent=2))
    
job_cards = result["data"]["searchJobCardsByLocation"]["jobCards"]

# Create a list to store extracted job info
extracted_jobs = []

for job in job_cards:
    job_info = {
        "jobId": job.get("jobId"),
        "jobTitle": job.get("jobTitle"),
        "jobType": job.get("jobType"),
        "employmentType": job.get("employmentType"),
        "city": job.get("city"),
        "state": job.get("state"),
        "postalCode": job.get("postalCode"),
        "locationName": job.get("locationName")
    }

    # job_id = "JOB-US-0000011548"
    if job_info["jobType"] == "FLEX_TIME;FULL_TIME" or job_info["jobType"] == "FULL_TIME" or job_info["jobType"] == "FLEX_TIME":
        schedules = get_schedules_for_job(job_info["jobId"])
        if schedules:
            job_info["schedules"] = schedules
        else:
            job_info["schedules"] = []
        
    extracted_jobs.append(job_info)
    

# Optional: Save to a file
with open("logs/extracted_jobs.txt", "w", encoding="utf-8") as f:
    for job in extracted_jobs:
        f.write(json.dumps(job, indent=2))
        f.write("\n")
