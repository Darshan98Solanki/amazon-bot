# headers.py

AUTH_TOKEN = "Bearer Status|logged-in|Session|eyJhbGciOiJLTVMiLCJ0eXAiOiJKV1QifQ.eyJpYXQiOjE3NTM2MDEwMDgsImV4cCI6MTc1MzYwNDYwOH0.AQICAHidzPmCkg52ERUUfDIMwcDZBDzd+C71CJf6w0t6dq2uqwGWUbA7ea6NgGsBxdmoBp02AAAAtDCBsQYJKoZIhvcNAQcGoIGjMIGgAgEAMIGaBgkqhkiG9w0BBwEwHgYJYIZIAWUDBAEuMBEEDGYdM2dyQV8QkERyHQIBEIBtCCg65J5C4wGY0y6Tw6Vr9BkLMMoP3IwcGzq4m3sz0x4i92eZiHJ1HPQGiFezra6rL61OWSUv/pGfocKAn7/ccfoKAC0xzupoCaQ080t1i2j47LlecGywKHVA8jNy/+QLMypdx2r3vBOXFiU2kw=="

# us headers
COMMON_HEADERS = {
    "accept": "*/*",
    "authorization": f"Bearer {AUTH_TOKEN}",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "country": "United States",
    "iscanary": "false",
    "origin": "https://hiring.amazon.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://hiring.amazon.com/",
    "sec-ch-ua": '"Opera";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"
}

# ca headers
# COMMON_HEADERS = {
#     'accept': '*/*',
#     'authorization': 'Bearer {AUTH_TOKEN}',
#     'cache-control': 'no-cache',
#     'content-type': 'application/json',
#     'country': 'Canada',
#     'iscanary': 'false',
#     'origin': 'https://hiring.amazon.ca',
#     'pragma': 'no-cache',
#     'priority': 'u=1, i',
#     'referer': 'https://hiring.amazon.ca/',
#     'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Opera";v="119"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'cross-site',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0'
# }
