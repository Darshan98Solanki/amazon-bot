
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
	return templates.TemplateResponse("form.html", {"request": request})

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
async def submit_form(request: Request, username: str = Form(...), token: str = Form(...)):
	
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
		return templates.TemplateResponse("form.html", {"request": request, "error": error})
	
    # Add new session
	sessions.append({"username": username, "token": token})
	
    # Save back to file
	with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
		json.dump(sessions, f, indent=2)
	return templates.TemplateResponse("form.html", {"request": request, "success": "Submitted successfully!"})

if __name__ == "__main__":
	import uvicorn
	uvicorn.run("app:app", host="0.0.0.0", port=8000, log_level="info")
