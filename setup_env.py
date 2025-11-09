#!/usr/bin/env python3
"""
Setup script to create .env file for Gemini API Key
"""
import os
from pathlib import Path

def setup_env_file():
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled. Existing .env file preserved.")
            return
    
    print("\n🔑 Gemini API Key Setup")
    print("=" * 40)
    print("You need a Gemini API key from Google AI Studio.")
    print("Get it here: https://aistudio.google.com/apikey")
    print()
    
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
    
    print(f"\n✅ .env file created successfully!")
    print(f"📍 Location: {env_file.absolute()}")
    print("\n💡 Your API key is now stored in .env (which is in .gitignore)")
    print("🚀 You can now run: streamlit run app2.py")

if __name__ == "__main__":
    setup_env_file()

