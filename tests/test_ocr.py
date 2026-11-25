import pytest
from ai.ocr.plate_ocr import LicensePlateOCR
from ai.ocr.preprocessor import ImagePreprocessor
import numpy as np


def test_ocr_plate_cleaning():
    ocr = LicensePlateOCR()
    assert ocr.clean_plate_text("AP 39 XX 1234") == "AP39XX1234"
    assert ocr.clean_plate_text("mh-02-cb-5566") == "MH02CB5566"
    assert ocr.clean_plate_text("  KA.05#MK$4422  ") == "KA05MK4422"
    assert ocr.clean_plate_text("") == ""


def test_image_preprocessor_crop():
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    crop = ImagePreprocessor.extract_lower_vehicle_crop(frame, [100, 100, 300, 300])
    assert crop is not None
    assert crop.shape[0] == 100  # Lower 50% of 200px height
    assert crop.shape[1] == 200  # 200px width
