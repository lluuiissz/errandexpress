import os
import sys
import django
from django.urls import resolve, reverse

sys.path.append(os.path.abspath('errandexpress'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

print("Debugging URL Resolution:")
print("-" * 30)

path = '/admin/'
try:
    match = resolve(path)
    print(f"Path '{path}' resolves to:")
    print(f"  View Name: {match.view_name}")
    print(f"  Func Name: {match.func.__name__}")
    print(f"  Module:    {match.func.__module__}")
except Exception as e:
    print(f"Error resolving '{path}': {e}")

print("-" * 30)

path2 = '/admin/database/'
try:
    match2 = resolve(path2)
    print(f"Path '{path2}' resolves to:")
    print(f"  View Name: {match2.view_name}")
    print(f"  Func:      {match2.func}")
except Exception as e:
    print(f"Error resolving '{path2}': {e}")
