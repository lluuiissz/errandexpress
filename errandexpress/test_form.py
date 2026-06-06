import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "errandexpress.settings")
django.setup()

from core.forms import TaskForm
form = TaskForm()
print("Category field HTML:", form['category'])
print("Tags field HTML:", form['tags'])
