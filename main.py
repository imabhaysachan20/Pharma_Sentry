"""
PharmaSentry Backend Entry Point.
Redirects to backend.app.main:app for modular application execution.
"""
from backend.app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)