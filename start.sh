#!/bin/bash

# Water Management System - Start Script
# This script starts both the Flask API and React frontend

echo ""
echo "========================================"
echo "Water Management System - Starting Up"
echo "========================================"
echo ""

# Check if running from correct directory
if [ ! -f "api.py" ]; then
    echo "ERROR: Please run this from the project root directory"
    echo "where api.py is located."
    exit 1
fi

# Start Flask Backend
echo "Starting Flask Backend on port 5000..."
python api.py &
FLASK_PID=$!

# Wait for backend to start
sleep 3

# Start React Frontend
echo "Starting React Frontend on port 3000..."
cd frontend
npm start &
REACT_PID=$!

cd ..

echo ""
echo "========================================"
echo "Services Starting:"
echo ""
echo "Flask API: http://localhost:5000/api"
echo "React App: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"
echo "========================================"
echo ""

# Wait for both processes
wait $FLASK_PID $REACT_PID
