## Overview
Amazon Bot is a FastAPI-based web application designed to monitor and extract job postings from Amazon's hiring platform. It provides a user-friendly interface for managing user sessions and automates the process of fetching job and shift data using Amazon's GraphQL APIs.

## Features
- User session management (add, start, remove users)
- Automated job and shift extraction from Amazon
- Token validation for secure API access
- Web interface for session and job management
- Modular backend utilities for jobs and shifts

## Directory Structure
```
amazon-bot/
├── abc.txt
├── amazon_bot.py
├── amazon-job-list.txt
├── README.md
├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── user-session.json
│   ├── backend/
│   │   ├── main.py
│   │   ├── logs/
│   │   │   └── extracted_jobs.txt
│   │   └── utils/
│   │       ├── get_jobs/
│   │       │   ├── get_ca_jobs.py
│   │       │   └── get_us_jobs.py
│   │       ├── get_shifts/
│   │       │   └── get_shifts.py
│   │       └── imports/
│   │           ├── check_token.py
│   │           └── constants.py
│   └── templates/
│       ├── chalchhaiyachhaiya.html
│       └── form.html
```

## Installation
1. Clone the repository:
	```
	git clone <repo-url>
	cd amazon-bot/app
	```
2. Install dependencies:
	```
	pip install -r requirements.txt
	```
3. Run the application:
	```
	uvicorn app:app --host 0.0.0.0 --port 8000
	```

## API Endpoints
### 1. `/` (GET)
- **Description:** Renders the user form for adding a new session.
- **Response:** HTML page (`form.html`)

### 2. `/submit` (POST)
- **Description:** Submits a new user session with username and token.
- **Request:**
  - `username` (str)
  - `token` (str)
- **Response:** Success or error message in `form.html`.

### 3. `/sessions` (GET)
- **Description:** Displays all user sessions.
- **Response:** HTML page (`chalchhaiyachhaiya.html`) with session table.

### 4. `/remove-user` (POST)
- **Description:** Removes a user session by username.
- **Request:**
  - `username` (str)
- **Response:** Updated session table.

### 5. `/start-user` (POST)
- **Description:** Starts a user session (currently returns a success message).
- **Request:**
  - `username` (str)
- **Response:** Success message in session table.

## Backend Workflow
1. **User Management:**
	- Users are added via the web form and stored in `user-session.json`.
	- Sessions can be started or removed via the web interface.

2. **Job Extraction:**
	- The backend (`main.py`) runs a loop to fetch job cards from Amazon's GraphQL API using the token and headers defined in `constants.py`.
	- New jobs are appended to `extracted_jobs.json` and logged.
	- For jobs with specific types, available shifts are fetched and attached.

3. **Token Validation:**
	- Before making API requests, the token is validated using `check_token.py` to ensure it is active and not expired.

4. **Utilities:**
	- `get_us_jobs.py` and `get_shifts.py` handle API requests and data extraction for jobs and shifts, respectively.

## Example Workflow
1. User accesses `/` and submits their username and token.
2. The session is stored and can be viewed at `/sessions`.
3. The backend starts monitoring jobs and shifts, updating the logs.
4. Users can remove or start sessions as needed.

## Requirements
- Python 3.9+
- All dependencies listed in `requirements.txt`

## Notes
- Ensure your token is valid and up-to-date in `constants.py`.
- The backend job extraction loop runs every 60 seconds.
- All API requests use secure headers and handle errors gracefully.

## License
MIT License

## Contact
For issues or contributions, please open a GitHub issue or contact the repository owner.
>>>>>>> 69d5436 (Updated project with latest changes)
