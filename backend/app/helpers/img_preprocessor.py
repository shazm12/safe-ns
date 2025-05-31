from PIL import Image
import cv2
import numpy as np
import asyncio
from skimage.filters import gaussian, median
import io
from typing import Dict

class ImagePreprocessor:
    def __init__(self, target_size=(1600, 1200), gaussian_sigma=1, mean_kernel_size=3, quality=90):
        """
        Initialize the preprocessor with default parameters
        
        Args:
            target_size (tuple): Target dimensions for resizing (width, height)
            gaussian_sigma (float): Sigma for Gaussian filter
            mean_kernel_size (int): Kernel size for mean filtering
            quality (int): JPEG quality for output
        """
        self.target_size = target_size
        self.gaussian_sigma = gaussian_sigma
        self.mean_kernel_size = mean_kernel_size
        self.quality = quality
        
    async def preprocess(self, image: Image.Image) -> Image.Image:
        """Async wrapper for image preprocessing"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self._sync_preprocess(image)
        )
    
    def _sync_preprocess(self, image: Image.Image) -> Image.Image:
        """Actual preprocessing logic"""
        img = np.array(image)
        
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # 1. Resize (maintain aspect ratio)
        img = self._smart_resize(img)
        
        # 2. Quality optimization
        img = self._optimize_quality(img)
        
        # 3. Apply filters
        img = self._apply_filters(img)
        

        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img)

    def _load_and_orient(self, image_path):
        """Load image and handle orientation (EXIF)"""
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        
        try:
            from PIL import Image, ExifTags
            pil_img = Image.open(image_path)
            if hasattr(pil_img, '_getexif'):
                exif = pil_img._getexif()
                if exif is not None:
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    if orientation in exif:
                        if exif[orientation] == 3:
                            img = cv2.rotate(img, cv2.ROTATE_180)
                        elif exif[orientation] == 6:
                            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                        elif exif[orientation] == 8:
                            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        except (AttributeError, KeyError, IndexError):
            pass
                
        return img
        
    def _smart_resize(self, img):
        """Resize maintaining aspect ratio without upscaling"""
        h, w = img.shape[:2]
        target_w, target_h = self.target_size
        
        # Only resize if image is larger than target
        if w > target_w or h > target_h:
            ratio = min(target_w/w, target_h/h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        return img
    
    def _optimize_quality(self, img):
        """Optimize image quality with contrast enhancement and sharpening"""

        if len(img.shape) == 2:
            return img
            

        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Mild CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        lab = cv2.merge((l, a, b))
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Mild sharpening
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)
        
        return img
 
    def _apply_filters(self, image):
        """Apply various filters to the image"""
        # Convert to float32 for processing
        if len(image.shape) == 2:
            # Handle grayscale images
            img_float = image.astype('float32') / 255.0
            blurred = gaussian(img_float, sigma=self.gaussian_sigma)
            sharpened = img_float + (img_float - blurred) * 1.5
            filtered = median(sharpened, np.ones((self.mean_kernel_size, self.mean_kernel_size)))
        else:
            # Handle color images
            img_float = image.astype('float32') / 255.0
            blurred = gaussian(img_float, sigma=self.gaussian_sigma, channel_axis=-1)
            sharpened = img_float + (img_float - blurred) * 1.5
            
            # Median filtering for noise reduction
            filtered = np.zeros_like(sharpened)
            for i in range(3):  # Apply to each channel
                filtered[:,:,i] = median(sharpened[:,:,i], 
                                       np.ones((self.mean_kernel_size, self.mean_kernel_size)))
        
        # Clip values to 0-1 range
        filtered = np.clip(filtered, 0, 1)
        
        # Normalization (per channel)
        if len(filtered.shape) == 3:
            for i in range(filtered.shape[2]):
                channel = filtered[:,:,i]
                filtered[:,:,i] = (channel - np.min(channel)) / (np.max(channel) - np.min(channel) + 1e-7)
        else:
            filtered = (filtered - np.min(filtered)) / (np.max(filtered) - np.min(filtered) + 1e-7)
        
        return (filtered * 255).astype('uint8')