import pytesseract
from PIL import Image
import os
import logging
from dotenv import load_dotenv
load_dotenv()


class OCRAgent:
    def __init__(self):
        # Configure Tesseract path for Windows
        self.tesseract_path = os.getenv('TESSERACT_PATH')
        self.tesseract_config = os.getenv('TESSERACT_CONFIG')

        # Verify installation
        if not os.path.exists(self.tesseract_path):
            raise EnvironmentError(
                f"Tesseract not found at {self.tesseract_path}\n"
                "Please install Tesseract first: "
                "https://github.com/UB-Mannheim/tesseract/wiki"
            )

        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

    def extract_text(self, image: Image.Image) -> str:
        """Process image and extract text with error handling"""
        try:
            img = image.convert('L')  # Convert to grayscale

            return pytesseract.image_to_string(
                img,
                config=self.tesseract_config,
                timeout=5
            )
        except pytesseract.TesseractError as e:
            logging.error(e, exc_info=True)
            return f"OCR Error: {str(e)}"
        except Exception as e:
            logging.error(e, exc_info=True)
            logging.error(e, exc_info=True)
            return f"Image processing error: {str(e)}"
