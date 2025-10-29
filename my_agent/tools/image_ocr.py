
import easyocr
from pathlib import Path
from typing import Union, List, Dict, Any
import numpy as np
from PIL import Image
import io

reader = None


def _get_reader():
    """Lazy initialization of EasyOCR reader."""
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False)
    return reader


def image_ocr(image_path: Union[str, Path, bytes, Image.Image, np.ndarray]) -> Dict[str, Any]:
    """
    Extract text from an image using EasyOCR.
    
    Args:
        image_path: Path to image file (str or Path), image bytes, PIL Image, or numpy array
        
    Returns:
        Dictionary containing:
            - text: All extracted text as a single string
            - text_lines: List of extracted text lines
            - details: List of dictionaries with detailed OCR results (text, confidence, bbox)
            - success: Boolean indicating if OCR was successful
            - error: Error message if any
    """
    try:
        ocr_reader = _get_reader()
        
        # Handle different input types
        if isinstance(image_path, (str, Path)):
            # File path
            image_path = Path(image_path)
            if not image_path.exists():
                return {
                    "text": "",
                    "text_lines": [],
                    "details": [],
                    "success": False,
                    "error": f"Image file not found: {image_path}"
                }
            results = ocr_reader.readtext(str(image_path))
        elif isinstance(image_path, bytes):
            # Image bytes
            image = Image.open(io.BytesIO(image_path))
            image_np = np.array(image)
            results = ocr_reader.readtext(image_np)
        elif isinstance(image_path, Image.Image):
            # PIL Image
            image_np = np.array(image_path)
            results = ocr_reader.readtext(image_np)
        elif isinstance(image_path, np.ndarray):
            # NumPy array
            results = ocr_reader.readtext(image_path)
        else:
            return {
                "text": "",
                "text_lines": [],
                "details": [],
                "success": False,
                "error": f"Unsupported image type: {type(image_path)}"
            }
        
        # Process results
        text_lines = []
        details = []
        
        for detection in results:
            # EasyOCR returns: (bbox, text, confidence)
            bbox, text, confidence = detection
            
            text_lines.append(text)
            details.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": [[float(x), float(y)] for x, y in bbox]  # Convert to list of lists
            })
        
        # Combine all text lines
        full_text = "\n".join(text_lines)
        
        return {
            "text": full_text,
            "text_lines": text_lines,
            "details": details,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        return {
            "text": "",
            "text_lines": [],
            "details": [],
            "success": False,
            "error": f"OCR processing error: {str(e)}"
        }


if __name__ == "__main__":
    test_image = "benchmark/attachments/28.png"
    result = image_ocr(test_image)
    print(result)

