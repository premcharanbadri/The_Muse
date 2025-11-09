# Quick Start Guide

## 🚀 Getting Your API Key

1. **Get your Gemini API Key:**
   - Visit: https://aistudio.google.com/apikey
   - Sign in with your Google account
   - Click "Create API Key" or use an existing one
   - Copy your API key

## 📝 Create Your .env File

Create a file named `.env` in this directory with your API key:

**Option 1: Using Terminal (macOS/Linux)**
```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

**Option 2: Using a Text Editor**
1. Create a new file named `.env` (with the dot at the beginning)
2. Add this line (replace with your actual key):
   ```
   GEMINI_API_KEY=your-api-key-here
   ```
3. Save the file

**Option 3: Using the Setup Script**
```bash
python3 setup_env.py
```

## ✅ Verify Setup

After creating the `.env` file, run:
```bash
streamlit run app2.py
```

The app should now work without the API key error!

## 🔒 Security Reminder

- ✅ The `.env` file is in `.gitignore` - it won't be committed to git
- ✅ Never share your API key publicly
- ✅ Your API key is safe to use locally

## 🆘 Troubleshooting

If you still see the error:
1. Make sure the `.env` file is in the same directory as `app2.py`
2. Check that the file name is exactly `.env` (not `.env.txt`)
3. Verify the format: `GEMINI_API_KEY=your-key-here` (no spaces around the `=`)
4. Restart your Streamlit app after creating the `.env` file

