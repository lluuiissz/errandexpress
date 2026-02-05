"""
Python Syntax Validator
Checks all Python files for syntax errors
"""
import py_compile
import os
import sys

def check_python_file(filepath):
    """Check a single Python file for syntax errors"""
    try:
        py_compile.compile(filepath, doraise=True)
        return None
    except py_compile.PyCompileError as e:
        return str(e)

# Check critical files
files_to_check = [
    r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\errandexpress\settings.py',
    r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\context_processors.py',
    r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\views.py',
]

print("\n" + "="*70)
print("PYTHON SYNTAX VALIDATION")
print("="*70)

errors_found = []

for filepath in files_to_check:
    if os.path.exists(filepath):
        filename = os.path.basename(filepath)
        error = check_python_file(filepath)
        if error:
            errors_found.append((filename, error))
            print(f"❌ {filename}: SYNTAX ERROR")
            print(f"   {error}")
        else:
            print(f"✅ {filename}: OK")
    else:
        print(f"⚠️  {os.path.basename(filepath)}: FILE NOT FOUND")

print("="*70)

if errors_found:
    print(f"\n❌ Found {len(errors_found)} files with syntax errors")
    sys.exit(1)
else:
    print(f"\n✅ All {len(files_to_check)} Python files validated successfully!")
    sys.exit(0)
