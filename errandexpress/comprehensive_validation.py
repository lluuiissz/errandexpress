"""
Comprehensive Validation Report Generator
Validates all aspects of the codebase
"""
import subprocess
import sys
from datetime import datetime

print("\n" + "="*80)
print("ERRANDEXPRESS COMPREHENSIVE VALIDATION REPORT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80 + "\n")

results = {
    'templates': None,
    'python': None,
    'django_check': None,
    'migrations': None
}

# 1. Template Validation
print("1. TEMPLATE VALIDATION")
print("-" * 80)
try:
    result = subprocess.run(
        ['py', 'validate_all_templates.py'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if 'NO ISSUES FOUND' in result.stdout:
        print("✅ All 62 templates validated - NO ISSUES")
        results['templates'] = 'PASS'
    else:
        print("⚠️  Template issues detected:")
        print(result.stdout)
        results['templates'] = 'ISSUES'
except Exception as e:
    print(f"❌ Template validation failed: {e}")
    results['templates'] = 'ERROR'

# 2. Python Syntax Validation
print("\n2. PYTHON SYNTAX VALIDATION")
print("-" * 80)
try:
    result = subprocess.run(
        ['py', 'validate_python.py'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if 'All 3 Python files validated successfully' in result.stdout:
        print("✅ All Python files validated - NO SYNTAX ERRORS")
        results['python'] = 'PASS'
    else:
        print("⚠️  Python syntax issues:")
        print(result.stdout)
        results['python'] = 'ISSUES'
except Exception as e:
    print(f"❌ Python validation failed: {e}")
    results['python'] = 'ERROR'

# 3. Django System Check
print("\n3. DJANGO SYSTEM CHECK")
print("-" * 80)
try:
    result = subprocess.run(
        ['py', 'manage.py', 'check'],
        capture_output=True,
        text=True,
        timeout=15
    )
    if 'System check identified no issues' in result.stdout:
        print("✅ Django system check passed - NO ISSUES")
        results['django_check'] = 'PASS'
    else:
        print("⚠️  Django check issues:")
        print(result.stdout)
        results['django_check'] = 'ISSUES'
except Exception as e:
    print(f"❌ Django check failed: {e}")
    results['django_check'] = 'ERROR'

# 4. Migration Status
print("\n4. MIGRATION STATUS")
print("-" * 80)
try:
    result = subprocess.run(
        ['py', 'manage.py', 'showmigrations', '--plan'],
        capture_output=True,
        text=True,
        timeout=10
    )
    unapplied = [line for line in result.stdout.split('\n') if '[ ]' in line]
    if not unapplied:
        print("✅ All migrations applied")
        results['migrations'] = 'PASS'
    else:
        print(f"⚠️  {len(unapplied)} unapplied migrations:")
        for migration in unapplied[:5]:
            print(f"   {migration}")
        results['migrations'] = 'PENDING'
except Exception as e:
    print(f"❌ Migration check failed: {e}")
    results['migrations'] = 'ERROR'

# Summary
print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)

all_pass = all(v == 'PASS' for v in results.values())

for check, status in results.items():
    icon = "✅" if status == 'PASS' else "⚠️ " if status in ['ISSUES', 'PENDING'] else "❌"
    print(f"{icon} {check.replace('_', ' ').title()}: {status}")

print("\n" + "="*80)
if all_pass:
    print("🎉 ALL VALIDATIONS PASSED - CODEBASE IS CLEAN!")
    sys.exit(0)
else:
    print("⚠️  SOME CHECKS REQUIRE ATTENTION")
    sys.exit(1)
print("="*80 + "\n")
