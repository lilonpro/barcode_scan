from pyzbar import pyzbar
import cv2
from glob import glob
import tempfile
import os
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)


def decode(image):
    # decodes all barcodes from an image
    decoded_objects = pyzbar.decode(image)
    print(decoded_objects)
    for obj in decoded_objects:
        # draw the barcode
        print("detected barcode:", obj)
        image = draw_barcode(obj, image)
        # print barcode type & data
        print("Type:", obj.type)
        print("Data:", obj.data)
        print()

    return image

def draw_barcode(decoded, image):
    # n_points = len(decoded.polygon)
    # for i in range(n_points):
    #     image = cv2.line(image, decoded.polygon[i], decoded.polygon[(i+1) % n_points], color=(0, 255, 0), thickness=5)
    # uncomment above and comment below if you want to draw a polygon and not a rectangle
    image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top), 
                            (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
                            color=(0, 255, 0),
                            thickness=5)
    return image

def lambda_handler(event, context):
    with tempfile.TemporaryDirectory() as path:
        file_prefix = "epod-"
        images_from_path = convert_from_path('SO_BOL.pdf', output_folder=path, fmt="png", output_file=file_prefix)
        for i in range(1, len(images_from_path) + 1):
            image_path = f"{path}/{file_prefix}0001-{i}.png"
            print(image_path)
            decode(cv2.imread(image_path))
if __name__ == "__main__":
    lambda_handler(None, None)
        
#     barcodes = glob("/tmp/epod0001-2.png")
#     for barcode_file in barcodes:
#         print(barcode_file)
#         img = cv2.imread(barcode_file)
#         img = decode(img)