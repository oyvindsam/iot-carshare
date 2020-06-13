#!/usr/bin/env python3
import bluetooth
import os
import time

class ScannerBlue:
  def __init__(self):
    super().__init__()

  # Search for device based on device's name
  def search(self):
    while True:
        device_address = None
        dt = time.strftime("%a, %d %b %y %H:%M:%S", time.localtime())
        print("\nCurrently: {}".format(dt))
        time.sleep(3) #Sleep three seconds 
        nearby_devices = bluetooth.discover_devices()

        for mac_address in nearby_devices:
            if "engineer" == bluetooth.lookup_name(mac_address, timeout=5):
                device_address = mac_address
                break
        if device_address is not None:
            print("Your phone ({}) has the MAC address: {}".format("engineer", device_address))
            return {"success": True, "data": "engineer"}
        else:
            print("Could not find target device nearby...")
            return {"error": True, "msg": "Could not find device"}
