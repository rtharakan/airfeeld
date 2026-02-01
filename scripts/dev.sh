#!/bin/bash

# Development script for Airfeeld
# Starts both backend and frontend servers

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}✈️  Starting Airfeeld Development Servers${NC}"
echo ""

# Check if ports are available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}Error: Port $1 is already in use${NC}"
        exit 1
    fi
}

check_port 8000
check_port 5173

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${GREEN}Starting backend on http://localhost:8000${NC}"
cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# Run migrations if needed
if [ -d "migrations" ]; then
    echo -e "${YELLOW}Running database migrations...${NC}"
    alembic upgrade head 2>/dev/null || true
fi

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo -e "${GREEN}Starting frontend on http://localhost:5173${NC}"
cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm dependencies...${NC}"
    npm install --silent
fi
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}🚀 Airfeeld is running!${NC}"
echo ""
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID
