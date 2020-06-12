#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   07/06/2020
#   Agent Pi QR Credentials Class

## Acknowledgement
## This code is adapted from:
## https://www.pyimagesearch.com/2018/05/21/an-opencv-barcode-and-qr-code-scanner-with-zbar/
## pip3 install pyzbar

from pyzbar import pyzbar
import datetime
import time
import cv2

class ScannerQR:

  def __init__(self):
    super().__init__()

  def scanQR(self):
    """
    Scans the QR code and returns the data

    Args:
        None

    Returns:
        dict: {'success': True, 'dataType': string, 'data': string} or {'error': True, 'msg': string}
    """

    # initialize the video stream and allow the camera sensor to warm up
    print("[INFO] Loading QR Scanner")
    vs = cv2.VideoCapture(0)
    vs.set(3, 640)
    vs.set(3, 480)
    time.sleep(2.0)

    found = set()

    exit = False

    # loop over the frames from the video stream
    while exit == False:
      # Get the current frame and check
      ret, frame = vs.read()
      if not ret:
        return {"error": True, "msg": "Camera Error - Frame Capture Issue"}
        break

      # find the barcodes in the frame and decode each of the barcodes
      barcodes = pyzbar.decode(frame)

      for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        print("[FOUND] Type: {}, Data: {}".format(barcodeType, barcodeData))
        exit = True
        return {"success": True, "type": barcodeType, "data": barcodeData}

      time.sleep(1)
    
    vs.release()


if __name__ == "__main__":
    qr = ScannerQR()
    qr.scanQR()