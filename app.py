# app.py

# This app uses Streamlit to create a user interface for an AI-powered fashion stylist powered by a local open-source model via Ollama.

import os
import streamlit as st
import base64
import requests
from PIL import Image
from io import BytesIO

# --- Configuration ---
# Ollama runs a local server at this address by default
OLLAMA_API_URL = "http://localhost:11434/api/generate"
# Use a VLM model installed via Ollama (e.g., llava or qwen-vl)
MODEL_NAME = "llava:7b" 

# --- UI Customization: Injected CSS for Lavender Theme ---
CUSTOM_CSS = """
<style>
/* 1. Global Background Color (Indigo) */
.stApp {
    background-color: #6c62c0; /* Indigo */
    color: white; /* White text for contrast */
}

/* 2. Main Title Styling */
h1 {
    color: #ffffff; /* White for better contrast */
    text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.3);
}

/* 3. Header Styling */
h2, h3, .st-emotion-cache-1qg6de1 {
    color: #ffecff; /* Soft light lavender for headers */
    border-bottom: 2px solid #c9ace6;
    padding-bottom: 5px;
    margin-top: 20px;
}

/* 4. Sidebar Styling */
.stSidebar {
    background-color: #5a51a3; /* Darker Indigo for Sidebar */
    border-right: 5px solid #c9ace6;
    box-shadow: 5px 0 15px rgba(0, 0, 0, 0.25);
    color: white;
}

/* Ensure sidebar text is readable */
.stSidebar, .stSidebar * {
    color: white !important;
}

/* 5. Primary Button Styling */
.stButton>button {
    background-color: #b19cd9; /* Soft Lavender */
    color: #000 !important;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    border: none;
    transition: background-color 0.3s;
}

.stButton>button:hover {
    background-color: #d8c9ff; /* Lighter on hover */
    color: #000 !important;
}

/* 6. Info/Warning Boxes */
.stAlert {
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.20);
}
</style>
"""


# --- Function to Encode Image and Call Ollama ---
# def encode_image_to_base64(image: Image.Image) -> str:
#     """Converts a PIL Image object to a base64 string for the Ollama API."""
#     buffered = BytesIO()
#     # JPEG is often a good default for size/quality balance
#     image.save(buffered, format="JPEG")
#     return base64.b64encode(buffered.getvalue()).decode('utf-8')
def encode_image_to_base64(image: Image.Image) -> str:
    """Converts a PIL Image object to a base64 string for the Ollama API."""
    # Convert RGBA or LA to RGB since JPEG doesn't support alpha
    if image.mode in ("RGBA", "LA"):
        image = image.convert("RGB")
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def generate_outfit_suggestion_local(wardrobe_image: Image.Image, occasion_description: str) -> str:
    """
    Calls the local Ollama API to analyze the wardrobe image and suggest an outfit.
    """
    
    # 1. Encode the image
    base64_image = encode_image_to_base64(wardrobe_image)

    # 2. Construct the User Prompt
    prompt = (
        f"You are an expert personal stylist. Analyze the entire wardrobe in the image. "
        f"Based on the items and accessories visible, what is the best outfit "
        f"for the following occasion: **{occasion_description}**? "
        "Suggest a complete look and justify your choices. "
        "Structure your response with the sections: 'Suggested Outfit', 'Stylist Notes', and 'Visible Items Used'."
    )
    
    # 3. Construct the API Payload for Ollama
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [base64_image], # Ollama takes a list of base64 images
        "stream": False # We want the full response at once
    }

    try:
        # 4. Call the local Ollama server
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status() # Raise an exception for bad status codes
        
        # 5. Extract the generated text
        data = response.json()
        return data.get('response', 'Error: Model response not found.')
        
    except requests.exceptions.ConnectionError:
        return f"🚨 **Connection Error:** Could not connect to Ollama at {OLLAMA_API_URL}. \n\n" \
               f"Please ensure Ollama is installed, the {MODEL_NAME} model is pulled, and the Ollama application is running on your Mac."
    except requests.exceptions.RequestException as e:
        return f"An error occurred during the API call: {e}"


# --- Streamlit UI Layout ---
st.set_page_config(
    page_title="🥼 The Muse",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject the custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("🥼 The Muse - now powered by LLaVA")
st.markdown("Upload your wardrobe photo and tell me the occasion. I'll suggest the perfect outfit!")

# 1. User Input Area (Sidebar)
with st.sidebar:
    st.header("Input Your Wardrobe & Occasion")
    
    uploaded_file = st.file_uploader(
        "Upload a clear image of your wardrobe:",
        type=["jpg", "jpeg", "png"]
    )
    
    # Add a custom divider for separation
    st.markdown("---") 
    
    occasion = st.text_area(
        "Describe the occasion, time of day, and formality:",
        placeholder="Example: Casual Saturday lunch with friends, mid-afternoon.",
        value="A semi-formal evening dinner party on a cool autumn night."
    )
    
    # Add a decorative element
    st.markdown("<p style='text-align: center; color: #5D3FD3;'>Ready to get styled?</p>", unsafe_allow_html=True)

    if st.button("✨ Get Outfit Suggestion", type="primary", use_container_width=True): # Use full width button
        if uploaded_file and occasion:
            st.session_state['run_generation'] = True
        else:
            st.session_state['run_generation'] = False
            st.warning("Please upload an image and describe the occasion.")
    else:
        if 'run_generation' not in st.session_state:
             st.session_state['run_generation'] = False


# 2. Main Content Area
col1, col2 = st.columns([1, 1.5]) # Slightly wider column for the text result

# Column 1: Image Display
with col1:
    st.header("Wardrobe Preview")
    if uploaded_file:
        wardrobe_image = Image.open(uploaded_file)
        # Replaced use_column_width with use_container_width
        st.image(wardrobe_image, caption="Your Wardrobe", use_container_width=True) 
    else:
        st.info("Waiting for image upload. Ensure Ollama is running and LLaVA is pulled!")

# Column 2: Result Display
with col2:
    st.header("Stylist's Recommendation")
    
    if st.session_state.get('run_generation', False):
        if uploaded_file and occasion:
            wardrobe_image_to_process = Image.open(uploaded_file)
            
            # Use a colorful spinner to match the theme
            with st.spinner(f"Analyzing wardrobe with {MODEL_NAME} and styling the look..."):
                suggestion = generate_outfit_suggestion_local(wardrobe_image_to_process, occasion)
                # Use a markdown container to present the final result
                st.markdown(
                    f'<div style="border: 2px solid #6c62c0; padding: 15px; border-radius: 10px; background-color: #6c62c0;">'
                    f'{suggestion}'
                    f'</div>', 
                    unsafe_allow_html=True
                )
            
            st.session_state['run_generation'] = False

        else:
            st.error("Cannot process: Missing image or occasion description.")