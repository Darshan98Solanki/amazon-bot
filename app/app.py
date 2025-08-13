from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import json

app = FastAPI()

# Set up templates directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
SESSIONS_FILE = os.path.join(BASE_DIR, "user-session.json")


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
	locations = []
	locations_file = os.path.join(BASE_DIR, "locations.json")
	if os.path.exists(locations_file):
		try:
			with open(locations_file, "r", encoding="utf-8") as f:
				locations = json.load(f)
		except Exception:
			locations = []
	return templates.TemplateResponse("form.html", {"request": request, "locations": locations})


# Route to show user sessions table
@app.get("/sessions", response_class=HTMLResponse)
async def show_sessions(request: Request):
	sessions = []
	if os.path.exists(SESSIONS_FILE):
		try:
			with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
				sessions = json.load(f)
		except Exception:
			sessions = []
	return templates.TemplateResponse("chalchhaiyachhaiya.html", {"request": request, "sessions": sessions})

# Route to add location
@app.post("/add-location", response_class=HTMLResponse)
async def add_location(request: Request, loc_name: str = Form(...), loc_code: str = Form(...)):
	locations_file = os.path.join(BASE_DIR, "locations.json")
	locations = []
	if os.path.exists(locations_file):
		try:
			with open(locations_file, "r", encoding="utf-8") as f:
				locations = json.load(f)
		except Exception:
			locations = []
	# Check for duplicates
	duplicate = any(l["name"].strip().lower() == loc_name.strip().lower() or l["code"].strip().lower() == loc_code.strip().lower() for l in locations)
	if duplicate:
		return RedirectResponse(url="/sessions?error=location_exists", status_code=303)
	# Add new location
	locations.append({"name": loc_name, "code": loc_code})
	with open(locations_file, "w", encoding="utf-8") as f:
		json.dump(locations, f, indent=2)
	# Load sessions for table
	return RedirectResponse(url="/sessions", status_code=303)

# Remove user from sessions
@app.post("/remove-user", response_class=HTMLResponse)
async def remove_user(request: Request, username: str = Form(...)):
	sessions = []
	if os.path.exists(SESSIONS_FILE):
		try:
			with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
				sessions = json.load(f)
		except Exception:
			sessions = []
	sessions = [s for s in sessions if s.get("username") != username]
	with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
		json.dump(sessions, f, indent=2)
	return templates.TemplateResponse("chalchhaiyachhaiya.html", {"request": request, "sessions": sessions})

# Start user (just return started in JSON for now)
@app.post("/start-user", response_class=HTMLResponse)
async def start_user(request: Request, username: str = Form(...)):
	sessions = []
	if os.path.exists(SESSIONS_FILE):
		try:
			with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
				sessions = json.load(f)
		except Exception:
			sessions = []
	return templates.TemplateResponse("chalchhaiyachhaiya.html", {"request": request, "sessions": sessions, "success": f"Started '{username}' successfully!"})

@app.post("/submit", response_class=HTMLResponse)
async def submit_form(request: Request, username: str = Form(...), token: str = Form(...), location: str = Form(...)):
	# Load locations
	locations = []
	locations_file = os.path.join(BASE_DIR, "locations.json")
	if os.path.exists(locations_file):
		try:
			with open(locations_file, "r", encoding="utf-8") as f:
				locations = json.load(f)
		except Exception:
			locations = []
	# Load existing sessions
	sessions = []
	if os.path.exists(SESSIONS_FILE):
		try:
			with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
				sessions = json.load(f)
		except Exception:
			sessions = []
	# Check if username already exists
	if any(s.get("username") == username for s in sessions):
		error = f"Username '{username}' already exists."
		return templates.TemplateResponse("form.html", {"request": request, "error": error, "locations": locations})
	# Find location name
	location_name = next((loc["name"] for loc in locations if loc["code"] == location), location)
	# Add new session with location
	sessions.append({"username": username, "token": token, "location": location_name, "location_code": location})
	# Save back to file
	with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
		json.dump(sessions, f, indent=2)
	# Show success notification
	return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
	import uvicorn
	uvicorn.run("app:app", host="0.0.0.0", port=8000, log_level="info")
