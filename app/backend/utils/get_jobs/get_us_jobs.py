import requests
import json
from utils.imports.constants import COMMON_HEADERS as headers

def get_jobs_from_us(url):

    # Request payload
    data = {
        "query": """query searchJobCardsByLocation($searchJobRequest: SearchJobRequest!) {
    searchJobCardsByLocation(searchJobRequest: $searchJobRequest) {
        nextToken
        jobCards {
        jobId
        language
        dataSource
        requisitionType
        jobTitle
        jobType
        employmentType
        city
        state
        postalCode
        locationName
        totalPayRateMin
        totalPayRateMax
        tagLine
        bannerText
        image
        jobPreviewVideo
        distance
        featuredJob
        bonusJob
        bonusPay
        scheduleCount
        currencyCode
        geoClusterDescription
        surgePay
        jobTypeL10N
        employmentTypeL10N
        bonusPayL10N
        surgePayL10N
        totalPayRateMinL10N
        totalPayRateMaxL10N
        distanceL10N
        monthlyBasePayMin
        monthlyBasePayMinL10N
        monthlyBasePayMax
        monthlyBasePayMaxL10N
        jobContainerJobMetaL1
        virtualLocation
        poolingEnabled
        __typename
        }
        __typename
    }
    }""",
        "variables": {
            "searchJobRequest": {
                "locale": "en-US",
                "country": "United States",
                "keyWords": "",
                "equalFilters": [
                    {
                        "key": "scheduleRequiredLanguage",
                        "val": "en-US"
                    }
                ],
                "containFilters": [
                    {
                        "key": "isPrivateSchedule",
                        "val": ["false"]
                    }
                ],
                "rangeFilters": [
                    {
                        "key": "hoursPerWeek",
                        "range": {
                            "minimum": 0,
                            "maximum": 80
                        }
                    }
                ],
                "orFilters": [],
                "dateFilters": [
                    {
                        "key": "firstDayOnSite",
                        "range": {
                            "startDate": "2025-07-16"
                        }
                    }
                ],
                "sorters": [
                    {
                        "fieldName": "totalPayRateMax",
                        "ascending": "false"
                    }
                ],
                "pageSize": 100,
                "consolidateSchedule": True
            }
        }
    }

    try:
        # Send the POST request
        response = requests.post(url, headers=headers, json=data)

        # Check if request was successful
        response.raise_for_status()

        # Parse JSON response
        result = response.json()
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print("Response content:", response.text)
