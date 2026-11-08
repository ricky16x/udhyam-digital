#!/usr/bin/env bash
set -e

# Change to project root directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Verify virtual environment
if [ ! -f ".venv/bin/uvicorn" ]; then
    echo "Virtual environment not found or missing uvicorn. Setting up .venv..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

echo "Starting Udyam Digital server at http://localhost:8000..."
echo "Customer Journey: http://localhost:8000"
echo "Sales Back Office: http://localhost:8000/backoffice"
echo ""

cd backend
exec "$ROOT_DIR/.venv/bin/uvicorn" app:app --reload --port 8000
