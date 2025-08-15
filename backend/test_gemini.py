#!/usr/bin/env python3
"""
Quick test script for Gemini API integration.
Run from backend directory: python test_gemini.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.gemini import get_gemini_service
from app.schemas.entities import Finding

# Test basic connectivity
def test_gemini_connection():
    print("Testing Gemini API connection...")
    service = get_gemini_service()
    
    if not service._enabled:
        print("❌ Gemini service not enabled. Please set GEMINI_API_KEY in .env file")
        return False
    
    print("✅ Gemini service initialized")
    return True

# Test text summarization
def test_summarization():
    print("\nTesting text summarization...")
    service = get_gemini_service()
    
    test_report = """
    CHEST X-RAY REPORT
    
    Clinical History: 45-year-old male with persistent cough.
    
    Findings:
    - The lungs are hyperinflated with flattened diaphragms, consistent with emphysema.
    - There is a 3 cm opacity in the right upper lobe, concerning for malignancy.
    - No pleural effusion or pneumothorax.
    - The cardiac silhouette is normal in size.
    
    Impression:
    1. Right upper lobe opacity concerning for malignancy. CT chest recommended.
    2. Emphysematous changes.
    """
    
    summary = service.summarize_text(test_report)
    if summary:
        print(f"✅ Summary generated: {summary}")
        return True
    else:
        print("❌ Failed to generate summary")
        return False

# Test image classification (with stub image)
def test_image_classification():
    print("\nTesting image classification...")
    service = get_gemini_service()
    
    # Create a simple test image (white square)
    from PIL import Image
    import io
    
    img = Image.new('RGB', (512, 512), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    findings = service.classify_bytes(img_bytes)
    if findings:
        print(f"✅ Found {len(findings)} findings:")
        for f in findings:
            print(f"   - {f.label} (confidence: {f.confidence})")
        return True
    else:
        print("❌ No findings returned")
        return False

if __name__ == "__main__":
    print("=== Gemini Integration Test ===\n")
    
    # Load env vars
    from dotenv import load_dotenv
    load_dotenv()
    
    tests = [
        test_gemini_connection(),
        test_summarization(),
        test_image_classification()
    ]
    
    if all(tests):
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. Check your GEMINI_API_KEY in .env")
