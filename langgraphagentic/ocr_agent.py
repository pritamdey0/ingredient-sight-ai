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
        
    # Instruct model to extract ingredients, correct OCR errors, and clean the list
    prompt = (
        "Analyze this image of a product label. "
        "Extract only the ingredients list. "
        "Ignore all marketing text, branding, instructions, or unrelated information. "
        "Correct any spelling errors or OCR inaccuracies you spot based on standard chemical/ingredient nomenclature. "
        "Return the extracted ingredients as a clean, plain text comma-separated list."
    )

    # Stage 1: Try Gemini Vision API
    try:
        client = get_gemini_client()
        try:
            image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Failed to open image at {image_path}: {e}")
            
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image]
        )
        state["ocr_text"] = response.text.strip() if response.text else ""
        print("[INFO] OCR Node successfully processed using Gemini.")
        return state
    except Exception as e:
        print(f"[WARN] Gemini Vision API call failed: {e}. Trying Groq vision fallback...")

    # Stage 2: Try Groq Vision Fallback
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key:
        try:
            import base64
            import requests
            import io
            
            # Read, resize, and compress image to reduce payload size
            try:
                img = Image.open(image_path)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                max_size = 1200
                if max(img.width, img.height) > max_size:
                    ratio = max_size / max(img.width, img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                compressed_bytes = buffer.getvalue()
                encoded_image = base64.b64encode(compressed_bytes).decode("utf-8")
            except Exception as resize_err:
                print(f"[WARN] Image compression failed: {resize_err}. Reading raw file instead...")
                with open(image_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            # Try Qwen 3.6 27B vision model first, then standard llama-3.2 vision
            groq_models = ["qwen/qwen3.6-27b", "llama-3.2-11b-vision-preview"]
            last_groq_err = None
            
            for model in groq_models:
                try:
                    payload = {
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{encoded_image}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "temperature": 0.0
                    }
                    
                    groq_response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    groq_response.raise_for_status()
                    data = groq_response.json()
                    ocr_text = data["choices"][0]["message"]["content"]
                    state["ocr_text"] = ocr_text.strip() if ocr_text else ""
                    print(f"[INFO] OCR Node successfully recovered using Groq Vision ({model})!")
                    return state
                except Exception as model_err:
                    last_groq_err = model_err
                    print(f"[WARN] Groq model '{model}' failed: {model_err}")
            
            if last_groq_err:
                raise last_groq_err
        except Exception as groq_err:
            print(f"[WARN] Groq vision fallback failed: {groq_err}. Trying local pytesseract OCR fallback...")

    # Stage 3: Try Local Pytesseract Fallback
    try:
        import pytesseract
        img = Image.open(image_path)
        ocr_text = pytesseract.image_to_string(img)
        if ocr_text.strip():
            state["ocr_text"] = ocr_text.strip()
            print("[INFO] OCR Node successfully recovered using local pytesseract!")
            return state
        else:
            raise ValueError("Pytesseract returned empty text.")
    except Exception as tesseract_err:
        raise RuntimeError(
            f"All OCR stages failed.\n"
            f"1. Gemini failed: {e}\n"
            f"2. Groq Vision failed: {groq_api_key and locals().get('groq_err', 'Not tried')}\n"
            f"3. Local Pytesseract failed: {tesseract_err}"
        )
