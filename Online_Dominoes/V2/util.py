import json
import time
from config import *

def jsonDump (packet):
    if packet:
        try:
            return json.dumps(packet)
        except Exception as e:
            print(f"Error encoding packet: {e}")
            return None
    return None

def jsonLoad (packet):
    if packet:
        try:
            return json.loads(packet)
        except Exception as e:
            print(f"Error decoding packet: {e}")
            return None
    return None

def waitUntil(booleanSupplier):
    while not booleanSupplier():
        time.sleep(SLEEP_TIME)
