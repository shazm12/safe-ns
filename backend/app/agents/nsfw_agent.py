from google.cloud import vision
from PIL import Image
import io
from typing import Dict, List
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


class NSFWAgent:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

        self.categories = {
            'adult': {
                'threshold': 3,
                'description': 'Nudity or sexual content'
            },
            'violence': {
                'threshold': 3,
                'description': 'Violent or graphic content'
            },
            'racy': {
                'threshold': 3,
                'description': 'Suggestive content'
            },
            'medical': {
                'threshold': 3,
                'description': 'Medical conditions/injuries'
            },
            'spoof': {
                'threshold': 3,
                'description': 'Edited/doctored media'
            }
        }

    def detect(self, image: Image.Image) -> Dict:
        try:
            # Convert image if needed
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            content = img_byte_arr.getvalue()

            # Call APIs
            safe_response = self.client.safe_search_detection(
                image=vision.Image(content=content))
            object_response = self.client.object_localization(
                image=vision.Image(content=content))

            if safe_response.error.message:
                return {"error": safe_response.error.message}

            # Process results
            safe = safe_response.safe_search_annotation
            likelihood_name = ['UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY',
                               'POSSIBLE', 'LIKELY', 'VERY_LIKELY']

            # Get flagged categories
            flagged = []
            for cat, config in self.categories.items():
                level = getattr(safe, cat)
                if level >= config['threshold']:
                    flagged.append({
                        'category': cat,
                        'level': likelihood_name[level],
                        'description': config['description']
                    })

            # Get visual cues
            visual_cues = list({
                obj.name for obj in object_response.localized_object_annotations
                if obj.score > 0.7
            })

            return {
                "rating": "unsafe" if flagged else "safe",
                "flagged_categories": flagged,
                "visual_cues": visual_cues,
                "details": {
                    cat: likelihood_name[getattr(safe, cat)]
                    for cat in self.categories
                }
            }

        except Exception as e:
            return {"error": str(e)}
