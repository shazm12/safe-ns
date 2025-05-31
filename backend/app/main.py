from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
import io
import logging
from app.agents import OCRAgent, NSFWAgent, ToxicityAgent, MainAgent
import imghdr


app = FastAPI()


@app.post("/analyze/image")
async def analyze_image(image: UploadFile = File(...)):
    try:
        # Validate file
        contents = await image.read()
        
        # Verify image type
        image_type = imghdr.what(None, h=contents)
        if not image_type:
            raise HTTPException(400, "Invalid image file")
        
        
        img = Image.open(io.BytesIO(contents))
        img.verify()
        img = Image.open(io.BytesIO(contents))
        
        result = await MainAgent().analyze(img)
        if "error" in result:
            logging.error(f"Unexpected error: {result['error']}", exc_info=True)
            raise HTTPException(500, "Internal Server Error")
            
        return JSONResponse(result)
        
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
