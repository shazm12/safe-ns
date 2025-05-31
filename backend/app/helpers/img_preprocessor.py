import cv2
import numpy as np
from skimage import exposure
from skimage.filters import gaussian, median

class ImagePreprocessor:
    def __init__(self, target_size=(1600, 1200), gaussian_sigma=1, mean_kernel_size=3, quality=90):
        """
        Initialize the preprocessor with default parameters
        
        Args:
            target_size (tuple): Target dimensions for resizing (width, height)
            gaussian_sigma (float): Sigma for Gaussian filter
            mean_kernel_size (int): Kernel size for mean filtering
        """
        self.target_size = target_size
        self.gaussian_sigma = gaussian_sigma
        self.mean_kernel_size = mean_kernel_size
        self.quality = quality
    
    def process(self, image_path):
        """
        Complete preprocessing pipeline
        
        Args:
            image_path (str): Path to input image
            
        Returns:
            np.array: Preprocessed image ready for model input
        """
        
        # 1. Load and basic processing
        img = self._load_and_orient(image_path)
        
        # 2. Resize (maintaining aspect ratio)
        img = self._smart_resize(img)
        
        # 3. Quality optimization
        img = self._optimize_quality(img)
        
        return img

    def _load_and_orient(self, image_path):
            """Load image and handle orientation (EXIF)"""
            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            
            try:
                from PIL import Image, ExifTags
                pil_img = Image.open(image_path)
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = dict(pil_img._getexif().items())
                
                if exif[orientation] == 3:
                    img = cv2.rotate(img, cv2.ROTATE_180)
                elif exif[orientation] == 6:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                elif exif[orientation] == 8:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            except:
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
        # Convert to LAB color space for brightness adjustment
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
        """Step 4: Apply various filters"""
       
        img_float = image.astype('float32') / 255.0
        

        blurred = gaussian(img_float, sigma=self.gaussian_sigma, 
                          multichannel=True)
        sharpened = img_float + (img_float - blurred) * 1.5  # Sharpening factor
        
        # 4.2 Mean filtering for noise reduction
        # Using median filter instead of mean for better noise reduction
        filtered = np.zeros_like(sharpened)
        for i in range(3):  # Apply to each channel
            filtered[:,:,i] = median(sharpened[:,:,i], 
                                   np.ones((self.mean_kernel_size, self.mean_kernel_size)))
        

        filtered = np.clip(filtered, 0, 1)
        
        # 4.3 Normalization (per channel)
        for i in range(3):
            channel = filtered[:,:,i]
            filtered[:,:,i] = (channel - np.min(channel)) / (np.max(channel) - np.min(channel) + 1e-7)
        
        return (filtered * 255).astype('uint8')
