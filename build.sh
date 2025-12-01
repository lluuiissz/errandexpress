#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Navigate to Django project
cd errandexpress

# Collect static files
python manage.py collectstatic --noinput

echo "Build completed successfully!"
