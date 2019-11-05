# Invoice Parser
A web-app that extracts useful info like Invoice number ,Date , Amount and e-mail id from a scanned invoice image.

The OCR used here is via an API from https://www.abbyy.com/en-eu/cloud-ocr-sdk/.
I am not using the pytesseract library as this API gives me more accurate result and helps recognize aspects of invoice easily.
The API key is to be entered in the AbbyyOnlineSdk.py file.
