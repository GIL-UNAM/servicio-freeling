#!/bin/bash
set -e

echo "Starting FreeLing daemons..."

# Start 3 Spanish FreeLing server instances in the background
analyzer --server -p 9999 --outlv tagged -f /app/analyzer.cfg &
analyzer --server -p 9998 --outlv parsed -f /app/analyzer.cfg &
analyzer --server -p 9997 --outlv dep    -f /app/analyzer.cfg &

# Give FreeLing a moment to bind its ports
sleep 2

echo "FreeLing daemons started on ports 9997-9999"
echo "Starting gunicorn..."

# Run gunicorn as the main (PID 1) process
exec gunicorn -w 4 -b 0.0.0.0:5000 app:app
