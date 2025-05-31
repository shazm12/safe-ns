from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
import io
import logging
import imghdr
from pydantic import BaseModel
from typing import Union, Optional
from .agents import MainAgent

app = FastAPI()


class TextRequest(BaseModel):
    text: str


@app.post("/moderate")
async def moderate(
    text: Optional[str] = Form(None),
    image: Union[UploadFile, None] = File(None)
):
    try:
        # Validate that at least one input is provided
        if not text and not image:
            raise HTTPException(400, "Either text or image must be provided")

        if text:
            result = await MainAgent().analyze_text(text)
            if "error" in result:
                logging.error(
                    f"Image processing error: {result['error']}", exc_info=True)
                raise HTTPException(400, "Image processing failed")
            return JSONResponse({"result": result})

        if image:
            contents = await image.read()

            # Verify image type
            image_type = imghdr.what(None, h=contents)
            if not image_type:
                raise HTTPException(400, "Invalid image file")

            try:
                img = Image.open(io.BytesIO(contents))
                img.verify()
                img = Image.open(io.BytesIO(contents))

                result = await MainAgent().analyze_image(img)
                if "error" in result:
                    logging.error(
                        f"Image processing error: {result['error']}", exc_info=True)
                    raise HTTPException(400, "Image processing failed")

                return JSONResponse({"result": result})

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
