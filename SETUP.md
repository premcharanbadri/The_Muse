# Setup Instructions

## API Key Configuration

To protect your API keys, follow these steps:

1. **Create a `.env` file** in the project root directory:
   ```bash
   GEMINI_API_KEY=your-actual-api-key-here
   ```

2. The `.env` file is already in `.gitignore` and will **NOT** be committed to git.

3. Your app will automatically load the API key from the `.env` file when you run it.

## Installation

Dependencies have been installed. If you need to reinstall:
```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app2.py
```

## Security Notes

- ✅ Your `.env` file is protected by `.gitignore`
- ✅ API keys are never hardcoded in the source code
- ✅ Safe to push to GitHub or host on Git Pages
