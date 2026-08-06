import os
from PIL import Image
from google import genai
from dotenv import load_dotenv

load_dotenv()

_gemini_client_instance = None

def get_gemini_client():
    """
    Initializes and returns (or reuses) the GenAI Client using GOOGLE_API_KEY or GEMINI_API_KEY.
    Module-level singleton to avoid re-creating the client for every graph invocation.
    """
    global _gemini_client_instance
    if _gemini_client_instance is not None:
        return _gemini_client_instance

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Neither GOOGLE_API_KEY nor GEMINI_API_KEY was found in the environment/dotenv file.")
    _gemini_client_instance = genai.Client(api_key=api_key)
    return _gemini_client_instance

def ocr_node(state: dict) -> dict:
    """
    OCR Node using Gemini Vision (google-genai SDK) to extract ingredient lists.
    
    Expects state["image_path"] to point to a valid product label image.
    Stores the extracted ingredient list in state["ocr_text"].
    """
    image_path = state.get("image_path")
    if not image_path:
        raise ValueError("No 'image_path' provided in the state.")
        
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")
        
    client = get_gemini_client()
    
    # Load image using PIL
    try:
        image = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Failed to open image at {image_path}: {e}")
        
    # Instruct Gemini to extract ingredients, correct OCR errors, and clean the list
    prompt = (
        "Analyze this image of a product label. "
        "Extract only the ingredients list. "
        "Ignore all marketing text, branding, instructions, or unrelated information. "
        "Correct any spelling errors or OCR inaccuracies you spot based on standard chemical/ingredient nomenclature. "
        "Return the extracted ingredients as a clean, plain text comma-separated list."
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image]
        )


        
        # Store the cleaned extracted text in the state
        state["ocr_text"] = response.text.strip() if response.text else ""
    except Exception as e:
        raise RuntimeError(f"Gemini Vision API call failed: {e}")
        
    return state
