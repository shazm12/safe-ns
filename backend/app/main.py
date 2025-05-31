from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
import io
import logging
from app.agents import OCRAgent, NSFWAgent, ToxicityAgent
import imghdr
import os
from typing import Dict

app = FastAPI()

# Initialize agents
ocr_agent = OCRAgent()
nsfw_agent = NSFWAgent()
toxicity_agent = ToxicityAgent()

@app.post("/analyze/image")
async def analyze_image(image: UploadFile = File(...)):
    try:
        # Validate file
        contents = await image.read()
        
        # Verify image type
        image_type = imghdr.what(None, h=contents)
        if not image_type:
            raise HTTPException(400, "Invalid image file")
        
        # Reopen image
        img = Image.open(io.BytesIO(contents))
        img.verify()
        img = Image.open(io.BytesIO(contents))  # Reopen after verify
        
        # Process with agents
        ocr_text = ocr_agent.extract_text(img)
        nsfw_result = nsfw_agent.detect(img)
        
        # Handle NSFW API errors
        if nsfw_result.get("rating") == "error":
            raise HTTPException(500, f"NSFW detection failed: {nsfw_result.get('error')}")
        
        text_result = {}
        if ocr_text.strip():
            text_result = toxicity_agent.analyze(ocr_text)
        
        return JSONResponse({
            "image_analysis": {
                "is_safe": nsfw_result["rating"] == "safe",
                "confidence": nsfw_result.get("confidence", 0),
                "details": nsfw_result.get("details", {}),
                "visual_cues": nsfw_result.get("visual_cues",[])
            },
            "text_analysis": {
                "text_found": bool(ocr_text.strip()),
                "is_toxic": text_result.get("is_toxic", False),
                "offensive_words": text_result.get("offensive_words", []),
                "extracted_text": ocr_text if ocr_text.strip() else None
            },
            "verdict": "safe" if (
                nsfw_result["rating"] == "safe" and 
                not text_result.get("is_toxic", False)
            ) else "unsafe"
        })
        
    except UnidentifiedImageError:
        raise HTTPException(400, "Invalid image format")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(500, "Content analysis failed")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# For testing Google Cloud Vision directly
@app.post("/test-nsfw")
async def test_nsfw(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        return JSONResponse(nsfw_agent.detect(img))
    except Exception as e:
        raise HTTPException(500, str(e))