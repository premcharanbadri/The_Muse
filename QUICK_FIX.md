# Quick Fix: Create Your .env File

## Option 1: Using the Setup Script (Recommended)

Run this command in your terminal:
```bash
./create_env.sh
```

Then enter your API key when prompted.

## Option 2: Manual Creation

### Step 1: Create the file
Run this command (replace `your-api-key-here` with your actual key):
```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

### Step 2: Verify it was created
```bash
cat .env
```

You should see:
```
GEMINI_API_KEY=your-api-key-here
```

### Step 3: Edit if needed
If you need to edit it later:
```bash
nano .env
# or
open -e .env  # Opens in TextEdit on macOS
```

## Option 3: Using Python

```bash
python3 -c "api_key = input('Enter your API key: '); open('.env', 'w').write(f'GEMINI_API_KEY={api_key}\n'); print('✅ .env file created!')"
```

## Get Your API Key

1. Visit: https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key" or use an existing one
4. Copy your API key

## After Creating .env

1. **Restart Streamlit** completely (stop with Ctrl+C, then start again)
2. Run: `streamlit run app2.py`
3. The error should be gone!

## Verify It Works

Test the .env loading:
```bash
python3 test_env_loading.py
```

## Important Notes

- ✅ The `.env` file is already in `.gitignore` - it won't be committed to git
- ✅ Never share your API key publicly
- ✅ Make sure there are **no spaces** around the `=` sign
- ✅ Don't use quotes around the key value (unless the key itself contains special characters)
- ✅ The file must be named exactly `.env` (with the dot at the beginning)

