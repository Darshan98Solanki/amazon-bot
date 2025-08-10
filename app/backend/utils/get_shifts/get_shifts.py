import requests
import json
from datetime import datetime
from utils.imports.constants import COMMON_HEADERS as headers

def get_schedules_for_job(job_id: str):
    url = "https://e5mquma77feepi2bdn4d6h3mpu.appsync-api.us-east-1.amazonaws.com/graphql"
    
    graphql_query = """
    query searchScheduleCards($searchScheduleRequest: SearchScheduleRequest!) {
      searchScheduleCards(searchScheduleRequest: $searchScheduleRequest) {
        nextToken
        scheduleCards {
          scheduleId
          jobId
          externalJobTitle
          hireStartDate
          hoursPerWeek
          city
          state
          postalCode
          basePayL10N
          signOnBonusL10N
          totalPayRateL10N
          firstDayOnSiteL10N
        }
      }
    }
    """

    today = datetime.today().strftime("%Y-%m-%d")

    variables = {
        "searchScheduleRequest": {
            "locale": "en-US",
            "country": "United States",
            "keyWords": "",
            "equalFilters": [],
            "containFilters": [{"key": "isPrivateSchedule", "val": ["false"]}],
            "rangeFilters": [{"key": "hoursPerWeek", "range": {"minimum": 0, "maximum": 80}}],
            "orFilters": [],
            "dateFilters": [{"key": "firstDayOnSite", "range": {"startDate": today}}],
            "sorters": [{"fieldName": "totalPayRateMax", "ascending": "false"}],
            "pageSize": 1000,
            "jobId": job_id,
            "consolidateSchedule": True
        }
    }

    response = requests.post(url, headers=headers, json={"query": graphql_query, "variables": variables})

    if response.status_code == 200:
        data = response.json()
        return data["data"]["searchScheduleCards"]["scheduleCards"]
    else:
        print("Request failed:", response.status_code)
        return None
