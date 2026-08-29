#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Building React Frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== Collecting Static Files ==="
python manage.py collectstatic --no-input

echo "=== Running Database Migrations ==="
python manage.py migrate
