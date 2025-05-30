from fastapi import FastAPI,UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import io
import logging
from app.agents import ocr_agent

# Initalize server
app = FastAPI(
    title="Content Moderation Agent API",
    description="API for analyzing images/text for safety violations",
    version="0.1.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/analyze/image")
async def analyze_image(image: UploadFile = File(...)):
    try:
   
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        
        # Step 2: Parallel agent processing
        ocr_text = ocr_agent.process(img)
        nsfw_result = nsfw_agent.process(img)
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail="Image processing failed")

@app.get("/health")
async def health_check():
        return { "status" : "running" }