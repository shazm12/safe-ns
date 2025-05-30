from langchain.tools import tool
from PIL import Image
import pytesseract

class OCRAgent:
    def __init__(self):
        # Configure Tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        pass

    @tool
    def process(self, image: Image.Image) -> str:
        try:
            img = image.convert('L')  # Grayscale
            return pytesseract.image_to_string(img)
        except Exception as e:
            return f"OCR Error: {str(e)}"