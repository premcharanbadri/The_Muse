# app2.py

# This app uses Streamlit to create a user interface for an AI-powered fashion stylist powered by Google's Gemini API.

import os
import streamlit as st
from pathlib import Path
from PIL import Image
from io import BytesIO  
# You are importing Client and types from google.genai
from google.genai import Client, types 

# Load environment variables from .env file if it exists
# IMPORTANT: This must happen BEFORE any Streamlit UI code
# Get the directory where this script is located
try:
    script_dir = Path(__file__).parent.absolute()
except NameError:
    # Fallback if __file__ is not available (shouldn't happen in normal execution)
    script_dir = Path.cwd()

env_path = script_dir / ".env"

# Load .env file explicitly from the script's directory
# This ensures it works even if Streamlit runs from a different directory
_env_loaded = False
_env_error = None

try:
    from dotenv import load_dotenv
    
    # Try loading from script directory first
    if env_path.exists():
        result = load_dotenv(dotenv_path=str(env_path), override=True, verbose=False)
        if result:
            _env_loaded = True
    else:
        # Try loading from current directory and parent directories (find_dotenv behavior)
        # This searches up the directory tree for a .env file
        result = load_dotenv(override=True, verbose=False)
        if result:
            _env_loaded = True
            # Update env_path to the found location for debugging
            try:
                from dotenv import find_dotenv
                found_path = find_dotenv()
                if found_path:
                    env_path = Path(found_path)
            except:
                pass
                
except ImportError:
    _env_error = "python-dotenv not installed"
except Exception as e:
    _env_error = str(e)

# --- Configuration ---
# Get the API key from environment variables (loaded from .env or system env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check for API key and show helpful error if not found
if not GEMINI_API_KEY:
    # Set page config first before showing errors
    st.set_page_config(
        page_title="🥼 The Muse - Setup Required",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.error("🚨 **GEMINI_API_KEY environment variable not found.**")
    
    # Debug information in expander
    with st.expander("🔍 Debug Information", expanded=True):
        st.write(f"**Script directory:** `{script_dir}`")
        st.write(f"**Expected .env path:** `{env_path}`")
        st.write(f"**.env file exists:** {env_path.exists()}")
        st.write(f"**Environment loaded:** {_env_loaded}")
        if _env_error:
            st.write(f"**Error:** {_env_error}")
        
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    content = f.read().strip()
                    lines = content.split('\n')
                    st.write(f"**.env file found with {len(lines)} line(s)**")
                    # Show file structure without revealing the key
                    for line in lines:
                        if '=' in line:
                            key, _ = line.split('=', 1)
                            st.code(f"{key}=***HIDDEN***", language='text')
                        else:
                            st.code(line, language='text')
                    
                    # Check if GEMINI_API_KEY is in the file
                    if 'GEMINI_API_KEY' in content:
                        st.warning("⚠️ GEMINI_API_KEY found in .env file but not loaded into environment.")
                        st.info("💡 Try: 1) Restart Streamlit, 2) Check file format (no spaces around =), 3) Ensure file encoding is UTF-8")
            except Exception as e:
                st.write(f"❌ Error reading .env file: {e}")
        else:
            st.info(f"💡 Create a `.env` file at: `{env_path}`")
    
    st.markdown("---")
    st.info("💡 **Solution:** Create a `.env` file in the same directory as `app2.py` with the following content:")
    st.code("GEMINI_API_KEY=your-api-key-here", language='text')
    st.info("📝 **Get your API key from:** https://aistudio.google.com/apikey")
    st.warning("🔄 **Important:** After creating the `.env` file, **restart Streamlit** completely (stop and start again) for the changes to take effect.")
    
    st.stop()

# Initialize the Gemini Client
try:
    # Pass the API key explicitly to the Client
    client = Client(api_key=GEMINI_API_KEY)
    MODEL_NAME = "gemini-2.5-flash"  # Excellent for multimodal tasks
except Exception as e:
    # Use st.exception for better error display in Streamlit
    st.exception(f"Failed to initialize Gemini Client: {e}")
    st.stop()


def generate_outfit_suggestion(wardrobe_image: Image.Image, occasion_description: str) -> str:
    """
    Calls the Gemini API to analyze the wardrobe image and suggest an outfit.
    
    FIXED: Uses types.Part.from_bytes() to correctly pass the PIL image data.
    """
    
    # 1. Define the System Instruction for Role-Playing and better response structure
    system_instruction = (
        "You are an expert personal stylist. Your task is to analyze a user's "
        "wardrobe image and suggest the best possible outfit for a specific occasion. "
        "Your response MUST be structured, starting with a clear outfit recommendation, "
        "and then justifying the choice based on the items visible in the image. "
        "If a perfect item isn't visible, suggest a suitable alternative. "
        "Be encouraging and concise."
    )
    
    # 2. Construct the User Prompt for the multimodal request
    user_prompt = (
        f"Based on the attached image of my wardrobe, what is the best outfit "
        f"for the following occasion: **{occasion_description}**? "
        "Please suggest a complete look (main item, accessories, color coordination) "
        "using only the clothes and accessories visible. "
        "Structure your response with the sections: 'Suggested Outfit', 'Stylist Notes', and 'Items Used'."
    )
    
    # --- Convert PIL Image to Bytes for the API call ---
    # Convert images with alpha channel (RGBA, LA) or palette mode (P) to RGB
    # since JPEG doesn't support transparency
    image_mode = wardrobe_image.mode
    if image_mode in ("RGBA", "LA"):
        # Create a white background and paste the image with alpha channel
        rgb_image = Image.new("RGB", wardrobe_image.size, (255, 255, 255))
        rgb_image.paste(wardrobe_image, mask=wardrobe_image.split()[-1])
        wardrobe_image = rgb_image
    elif image_mode == "P":
        # Convert palette mode - check if it has transparency
        if "transparency" in wardrobe_image.info:
            # Has transparency, convert to RGBA then to RGB with white background
            rgba_image = wardrobe_image.convert("RGBA")
            rgb_image = Image.new("RGB", rgba_image.size, (255, 255, 255))
            rgb_image.paste(rgba_image, mask=rgba_image.split()[-1])
            wardrobe_image = rgb_image
        else:
            # No transparency, just convert to RGB
            wardrobe_image = wardrobe_image.convert("RGB")
    elif image_mode != "RGB":
        # Convert any other mode (like L grayscale, CMYK, etc.) to RGB
        wardrobe_image = wardrobe_image.convert("RGB")
    
    # Save the image as JPEG into the in-memory byte buffer
    img_byte_arr = BytesIO()
    wardrobe_image.save(img_byte_arr, format='JPEG', quality=95) 
    img_bytes = img_byte_arr.getvalue()
    
    # 3. Assemble the Content (Image + Text + Instruction)
    contents = [
        # CORRECT WAY: Use from_bytes with the byte data and mime type
        types.Part.from_bytes(
            data=img_bytes,
            mime_type='image/jpeg' 
        ),
        user_prompt
    ]
    # --- END OF FIX ---

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return response.text
    except Exception as e:
        return f"An error occurred while generating the suggestion: {e}"


# --- Streamlit UI Layout ---
st.set_page_config(
    page_title="🥼 The Muse",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS for purple gradient theme matching the HTML design
st.markdown(
    """
    <style>
        /* Main app background - purple gradient */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        /* Sidebar - purple gradient matching main theme */
        .stSidebar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        /* Ensure sidebar text is readable */
        .stSidebar, .stSidebar * {
            color: white !important;
        }
        
        /* Title bar (header) at the top - purple gradient */
        header[data-testid="stHeader"],
        .stApp > header,
        div[data-testid="stHeader"],
        .stApp header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        
        /* Header decoration/divider */
        .stApp > header::before,
        header[data-testid="stHeader"]::before {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        
        /* Main title styling - white text */
        h1 {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        /* Headers - white text */
        h2, h3 {
            color: white;
        }
        
        /* Main content area - white background with rounded corners */
        .main .block-container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-top: 20px;
            margin-bottom: 20px;
        }
        
        /* Description/info/warning/error boxes - white with purple border */
        .stAlert {
            background-color: #CEA2FD!important;
            color: #333 !important;
            border: 2px solid #667eea;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            padding: 15px;
        }
        
        /* Info boxes specifically */
        .stAlert > div {
            # background-color: #f2bdf9 !important;
            color: #333 !important;
        }
        
        /* Make text in white boxes readable */
        .stAlert p, .stAlert div, .stAlert span {
            color: #333 !important;
        }
        
        /* Specific styling for info, warning, error, success boxes */
        div[data-baseweb="notification"] {
            background-color: white !important;
            border: 2px solid #667eea;
            border-radius: 12px;
        }
        
        /* Buttons - purple gradient */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px 30px;
            font-size: 1.1rem;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* Text input and textarea styling */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* File uploader styling */
        .stFileUploader > div {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            background: #f2bdf9;
        }
        
        .stFileUploader > div:hover {
            border-color: #764ba2;
            background: #f8f9fa;
        }
        
        /* Markdown text in main area - dark text on white background */
        .main .block-container p,
        .main .block-container div {
            color: #f2bdf9;
        }
        
        /* Sidebar headers and text */
        .stSidebar h1,
        .stSidebar h2,
        .stSidebar h3 {
            color: white;
        }
        
        /* Image captions */
        .stImage > div > img {
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Spinner/loading indicator */
        .stSpinner > div {
            border-top-color: #667eea;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🥼 The Muse - now powered by Gemini")
st.markdown("Upload your wardrobe photo and tell me the occasion. I'll suggest the perfect outfit!")

# 1. User Input Area (Sidebar)
with st.sidebar:
    st.header("Input Your Wardrobe & Occasion")
    
    # File Uploader
    uploaded_file = st.file_uploader(
        "Upload a clear image of your wardrobe:",
        type=["jpg", "jpeg", "png"]
    )
    
    # Text Input for Occasion
    occasion = st.text_area(
        "Describe the occasion, time of day, and formality:",
        placeholder="Example: Casual Saturday lunch with friends, mid-afternoon.",
        value="A semi-formal evening dinner party on a cool autumn night."
    )

    # Submission Button
    if st.button("✨ Get Outfit Suggestion", type="primary"):
        if uploaded_file and occasion:
            st.session_state['run_generation'] = True
        else:
            st.session_state['run_generation'] = False
            st.warning("Please upload an image and describe the occasion.")
    else:
        # Initialize state if the button hasn't been clicked or was just unclicked
        if 'run_generation' not in st.session_state:
             st.session_state['run_generation'] = False


# 2. Main Content Area (Visualization and Output)

col1, col2 = st.columns([1, 1.5])

# Column 1: Image Display
with col1:
    st.header("Wardrobe Preview")
    if uploaded_file:
        # Display the uploaded image
        wardrobe_image = Image.open(uploaded_file)
        # Replacing deprecated use_column_width with use_container_width
        st.image(wardrobe_image, caption="Your Wardrobe", use_container_width=True) 
    else:
        st.info("Waiting for image upload...")

# Column 2: Result Display
with col2:
    st.header("Stylist's Recommendation")
    
    # Run the model when the button is pressed and inputs are valid
    if st.session_state.get('run_generation', False):
        if uploaded_file and occasion:
            # Re-read the image for the model call
            wardrobe_image_to_process = Image.open(uploaded_file)
            
            with st.spinner("Analyzing wardrobe and styling the perfect look..."):
                # Call the API function
                suggestion = generate_outfit_suggestion(wardrobe_image_to_process, occasion)
                st.markdown(suggestion) # Display the styled markdown response
            
            # Reset state to prevent re-running on every interaction
            st.session_state['run_generation'] = False

        else:
            st.error("Cannot process: Missing image or occasion description.")

    # To set your API key, use: export GEMINI_API_KEY="your-api-key-here"
    # Or create a .env file with: GEMINI_API_KEY=your-api-key-here
    # pip install google-genai 
    # streamlit run app2.py