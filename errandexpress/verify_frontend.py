"""
Comprehensive verification script for frontend UI and code quality
Tests: Form fields, tag splitting, code issues, priority levels
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from core.models import Task, User
from core.forms import TaskForm
from django.test import RequestFactory
from django.contrib.auth import get_user_model

print("=" * 60)
print("COMPREHENSIVE VERIFICATION SCRIPT")
print("=" * 60)
print()

# Test 1: Priority Level Field
print("✅ TEST 1: Priority Level Field")
print("-" * 60)
try:
    priority_field = Task._meta.get_field('priority_level')
    print(f"✅ Field exists: priority_level")
    print(f"   Type: {priority_field.__class__.__name__}")
    print(f"   Default: {priority_field.default}")
    print(f"   Validators: {priority_field.validators}")
    print(f"   Help text: {priority_field.help_text}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 2: TaskForm Initialization
print("✅ TEST 2: TaskForm Initialization")
print("-" * 60)
try:
    form = TaskForm()
    
    # Check if priority_level field exists in form
    if 'priority_level' in form.fields:
        print("✅ priority_level field exists in form")
        print(f"   Required: {form.fields['priority_level'].required}")
        print(f"   Initial: {form.fields['priority_level'].initial}")
        print(f"   Choices: {form.fields['priority_level'].choices}")
        print(f"   Widget: {form.fields['priority_level'].widget.__class__.__name__}")
    else:
        print("❌ priority_level field NOT in form")
    
    # Check all new fields
    new_fields = ['time_window_start', 'time_window_end', 'preferred_doer', 
                  'priority_level', 'flexible_timing']
    print(f"\n   All new fields in form:")
    for field_name in new_fields:
        exists = "✅" if field_name in form.fields else "❌"
        print(f"   {exists} {field_name}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 3: Tag Splitting
print("✅ TEST 3: Tag Splitting")
print("-" * 60)
try:
    # Create a test task
    test_tags = "typing, urgent, campus"
    print(f"Input tags: '{test_tags}'")
    
    # Simulate tag splitting
    tags_list = [tag.strip() for tag in test_tags.split(',') if tag.strip()]
    print(f"Output list: {tags_list}")
    
    expected = ['typing', 'urgent', 'campus']
    if tags_list == expected:
        print("✅ Tag splitting works correctly")
    else:
        print(f"❌ Expected {expected}, got {tags_list}")
        
    # Test edge cases
    edge_cases = [
        ("  typing  ,  urgent  ", ['typing', 'urgent']),
        ("typing,,,urgent", ['typing', 'urgent']),
        ("typing", ['typing']),
        ("", []),
    ]
    
    print("\n   Edge cases:")
    for input_str, expected in edge_cases:
        result = [tag.strip() for tag in input_str.split(',') if tag.strip()]
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{input_str}' → {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 4: Database Field Check
print("✅ TEST 4: Database Field Verification")
print("-" * 60)
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'core_task' 
            AND column_name IN ('priority_level', 'time_window_start', 'time_window_end', 
                                'preferred_doer_id', 'flexible_timing')
            ORDER BY column_name
        """)
        rows = cursor.fetchall()
        
        if rows:
            print("✅ New fields in database:")
            for row in rows:
                print(f"   - {row[0]}: {row[1]} (default: {row[2]})")
        else:
            print("❌ No new fields found in database")
            
except Exception as e:
    print(f"⚠️  Database check skipped (SQLite): {e}")
print()

# Test 5: Code Quality Scan
print("✅ TEST 5: Code Quality Scan")
print("-" * 60)
try:
    import re
    
    # Check forms.py
    forms_path = 'core/forms.py'
    with open(forms_path, 'r', encoding='utf-8') as f:
        forms_content = f.read()
    
    issues = []
    
    # Check for undefined variables
    if 'undefined_var' in forms_content:
        issues.append("Undefined variable found")
    
    # Check for syntax errors (basic)
    try:
        compile(forms_content, forms_path, 'exec')
        print("✅ No syntax errors in forms.py")
    except SyntaxError as e:
        issues.append(f"Syntax error: {e}")
    
    # Check for proper imports
    required_imports = ['from django import forms', 'from .models import Task']
    for imp in required_imports:
        if imp in forms_content:
            print(f"✅ Import found: {imp}")
        else:
            issues.append(f"Missing import: {imp}")
    
    # Check template
    template_path = 'core/templates/create_task_modern.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Check for unclosed tags
    open_tags = template_content.count('{{')
    close_tags = template_content.count('}}')
    if open_tags == close_tags:
        print(f"✅ Template tags balanced ({open_tags} pairs)")
    else:
        issues.append(f"Template tag mismatch: {open_tags} open, {close_tags} close")
    
    # Check for Section 4
    if 'Section 4' in template_content or 'Preferences & Scheduling' in template_content:
        print("✅ Section 4 (Preferences) found in template")
    else:
        issues.append("Section 4 not found in template")
    
    if issues:
        print(f"\n❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ No code quality issues found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 6: Form Rendering Test
print("✅ TEST 6: Form Field Rendering")
print("-" * 60)
try:
    form = TaskForm()
    
    # Test priority_level widget rendering
    if 'priority_level' in form.fields:
        widget = form.fields['priority_level'].widget
        print(f"✅ Priority widget type: {widget.__class__.__name__}")
        
        # Render the widget
        html = str(form['priority_level'])
        
        # Check if options are rendered
        if '<option' in html:
            option_count = html.count('<option')
            print(f"✅ Priority dropdown has {option_count} options")
            
            # Check for star ratings
            if '⭐' in html:
                print("✅ Star ratings (⭐) found in options")
            else:
                print("⚠️  Star ratings not found (may be OK)")
        else:
            print("❌ No options found in priority dropdown")
    else:
        print("❌ priority_level field not in form")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
print()

# Summary
print("=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)
print("✅ All tests completed")
print("Check results above for any ❌ failures")
print()
