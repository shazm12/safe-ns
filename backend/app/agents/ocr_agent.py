import pytesseract
from PIL import Image
import os
import logging


class OCRAgent:
    def __init__(self):
        # Configure Tesseract path for Windows
        self.tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

            # OEM=LSTM, PSM=Assume single uniform block
            custom_config = r'--oem 3 --psm 6'

            return pytesseract.image_to_string(
                img,
                config=custom_config,
                timeout=5
            )
        except pytesseract.TesseractError as e:
            logging.error(e, exc_info=True)
            return f"OCR Error: {str(e)}"
        except Exception as e:
            logging.error(e, exc_info=True)
            logging.error(e, exc_info=True)
            return f"Image processing error: {str(e)}"
