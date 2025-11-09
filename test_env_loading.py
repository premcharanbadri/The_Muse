#!/usr/bin/env python3
"""
Test script to verify .env file loading works correctly
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 70)
print("Testing .env File Loading")
print("=" * 70)

# Get script directory (same logic as app2.py)
try:
    script_dir = Path(__file__).parent.absolute()
except NameError:
    script_dir = Path.cwd()

env_path = script_dir / ".env"

print(f"\n1. Script directory: {script_dir}")
print(f"2. Expected .env path: {env_path}")
print(f"3. .env file exists: {env_path.exists()}")

if env_path.exists():
    print(f"\n4. Reading .env file...")
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            print(f"   File size: {len(content)} bytes")
            print(f"   Content preview: {repr(content[:100])}")
            
            # Check for common issues
            lines = content.strip().split('\n')
            print(f"   Number of lines: {len(lines)}")
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    print(f"   Line {i}: {key} = {'***' + value[-4:] if len(value) > 4 else '***'}")
                    if key == 'GEMINI_API_KEY':
                        if not value:
                            print(f"      ⚠️  WARNING: Value is empty!")
                        if value.startswith('"') and value.endswith('"'):
                            print(f"      ⚠️  WARNING: Value has quotes - remove them!")
                        if value.startswith("'") and value.endswith("'"):
                            print(f"      ⚠️  WARNING: Value has quotes - remove them!")
                        if ' ' in key or ' ' in value.split()[0] if value else False:
                            print(f"      ⚠️  WARNING: Check for spaces around = sign!")
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        exit(1)
else:
    print(f"\n4. ❌ .env file not found!")
    print(f"   Create it with: echo 'GEMINI_API_KEY=your-key' > '{env_path}'")
    exit(1)

print(f"\n5. Loading .env file with load_dotenv()...")
try:
    result = load_dotenv(dotenv_path=str(env_path), override=True, verbose=True)
    print(f"   load_dotenv() returned: {result}")
except Exception as e:
    print(f"   ❌ Error loading .env: {e}")
    exit(1)

print(f"\n6. Checking environment variable...")
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"   ✅ SUCCESS! GEMINI_API_KEY found in environment")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Preview: {api_key[:15]}...{api_key[-5:]}")
    print(f"\n✅ All tests passed! .env file loading works correctly.")
else:
    print(f"   ❌ FAILED! GEMINI_API_KEY not found in environment")
    print(f"\n❌ Troubleshooting:")
    print(f"   1. Check .env file format: GEMINI_API_KEY=your-key (no spaces)")
    print(f"   2. Make sure there are no quotes around the value")
    print(f"   3. Make sure the file is saved as UTF-8")
    print(f"   4. Try: export GEMINI_API_KEY=your-key (to test if it works)")
    exit(1)

print("=" * 70)

