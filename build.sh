#!/bin/bash
# Vercel build script for Django

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
cd errandexpress
python manage.py collectstatic --noinput

echo "Build completed successfully!"
