#!/bin/bash
# Script to create .env file for Gemini API Key

echo "🔑 Gemini API Key Setup"
echo "========================"
echo ""
echo "Get your API key from: https://aistudio.google.com/apikey"
echo ""
read -p "Enter your Gemini API key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

echo "GEMINI_API_KEY=$api_key" > .env
echo ""
echo "✅ .env file created successfully!"
echo "📍 Location: $(pwd)/.env"
echo ""
echo "🚀 You can now run: streamlit run app2.py"
