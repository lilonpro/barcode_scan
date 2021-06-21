from pyzbar import pyzbar
import cv2
from glob import glob
import tempfile
import os
import boto3
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import logging

def extract_pages(bucket, key):
    # Get pdf file from S3
    s3 = boto3.client(
        's3',
        aws_access_key_id='AKIA2CHVCTWTCDPGOSNE',
        aws_secret_access_key='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'
    )
    obj = s3.get_object(Bucket=bucket, Key=key)

    # convert each page of PDF to image and scan for barcode, image will be saved in temp folder
    with tempfile.TemporaryDirectory() as path:
        file_prefix = "epod-"
        # next comment line is to test scan local pdf file
        # images_from_path = convert_from_path('SO_BOL.pdf', output_folder=path, fmt="png", output_file=file_prefix)
        images_from_path = convert_from_bytes(obj["Body"].read(), output_folder=path, fmt="png", output_file=file_prefix)
        # list to hold info for each page of pdf
        pdf_info = []
        # scan barcode page by page
        for i in range(1, len(images_from_path) + 1):
            image_path = f"{path}/{file_prefix}0001-{i}.png"
            barcode = scan_barcode(cv2.imread(image_path))
            # throw exception if barcode is none
            if barcode is None:   
                raise ValueError(f'Page {i} of PDF has no barcode')
            # extract info from barcode
            barcode_info = barcode.split("-")
            pdf_info.append({
                "pdf_page": i,
                "pod_type": barcode_info[0],
                "pod_number": barcode_info[1],
                "pod_page": int(barcode_info[2]),
                "barcode": barcode
            })
    return pdf_info

def scan_barcode(image):
    # Scan barcode in image
    decoded_objects = pyzbar.decode(image)
    if len(decoded_objects) >= 1:
        if len(decoded_objects) > 1:
            logging.warning("More than one barcode found in one page, taking first one")
        barcode = decoded_objects[0].data.decode("utf-8")
    else:
        logging.error("No barcode found")
    return barcode

def validate_pdf_info(pdf_info):
    # validate if pdf pages are valid
    for index, page in enumerate(pdf_info):
        if page["pdf_page"] == 1 and page["pod_page"] != 1:
            raise ValueError('PDF first page is not barcode first page')
        elif page["pod_page"] != 1 and page["pod_page"] != (pdf_info[index - 1]["pod_page"] + 1):
            raise ValueError(f'Missing page in between {pdf_info[index - 1]} and {page["pod_page"]} for pod {page["pod_number"]}')

if __name__ == "__main__":
    pdf_info = extract_pages("email-classification-ui", "SO_BOL.pdf")
    validate_pdf_info(pdf_info)
    print(pdf_info)