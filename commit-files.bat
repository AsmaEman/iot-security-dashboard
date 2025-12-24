@echo off
echo ========================================
echo Git Commit Script - Individual Files
echo ========================================
echo.

REM Add .gitignore first
echo [1] Adding .gitignore...
git add .gitignore
git commit -m "Add comprehensive .gitignore file"

REM Backend files
echo [2] Committing backend structure...
git add backend/requirements.txt
git commit -m "Update backend requirements with simplified dependencies"

git add backend/src/__init__.py backend/src/api/__init__.py backend/src/database/__init__.py backend/src/detection_engine/__init__.py backend/src/utils/__init__.py backend/src/tasks/__init__.py backend/src/api/routes/__init__.py
git commit -m "Add backend module init files"

git add backend/src/api/main.py
git commit -m "Implement FastAPI main application with WebSocket support"

git add backend/src/api/models.py
git commit -m "Add Pydantic models for API requests and responses"

git add backend/src/api/middleware.py
git commit -m "Add rate limiting and metrics middleware"

git add backend/src/api/routes/devices.py
git commit -m "Implement device management API endpoints with mock data"

git add backend/src/database/models.py
git commit -m "Add SQLAlchemy database models for devices, alerts, vulnerabilities"

git add backend/src/database/session.py
git commit -m "Add database session management with mock support"

git add backend/src/detection_engine/fingerprinter.py
git commit -m "Implement mock device fingerprinting engine"

git add backend/src/utils/logger.py
git commit -m "Add structured logging utility"

git add backend/src/utils/metrics.py
git commit -m "Add metrics collection system"

git add backend/src/tasks/device_tasks.py
git commit -m "Add mock background task system"

REM Frontend files
echo [3] Committing frontend structure...
git add frontend/package.json
git commit -m "Simplify frontend dependencies for faster builds"

git add frontend/src/App.jsx
git commit -m "Create simplified React dashboard with device listing"

git add frontend/src/App.css
git commit -m "Add modern gradient styling for dashboard"

git add frontend/test.html
git commit -m "Add standalone HTML test interface for API testing"

REM Configuration files
echo [4] Committing configuration...
git add docker-compose.yml
git commit -m "Update Docker Compose configuration"

git add start-dev.bat
git commit -m "Update development startup script"

git add README.md
git commit -m "Update README with simplified setup instructions"

git add commit-files.bat
git commit -m "Add git commit automation script"

echo.
echo ========================================
echo All files committed successfully!
echo ========================================
echo.
echo To push to remote repository:
echo git push origin main
echo.
pause