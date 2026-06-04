import json
import time
from config import *
import math

def jsonDump (packet): ##dumps a packet into json
    if packet:
        try:
            return json.dumps(packet)
        except Exception as e:
            print(f"Error encoding packet: {e}")
            return None
    return None

def jsonLoad (packet): ##Loads a packet from json
    if packet:
        try:
            return json.loads(packet)
        except Exception as e:
            print(f"Error decoding packet: {e}")
            return None
    return None

def waitUntil(booleanSupplier): ##waits until a boolean supplier is true
    while not booleanSupplier():
        time.sleep(SLEEP_TIME)

def absCoordToCellCoord(position): ##converts screen positions into cell positions
    return (math.floor(position[0]/TILE_DIMENSIONS[0]),math.floor(position[1]/TILE_DIMENSIONS[1]))

def cellCoordToAbsCoord(position): #converts cell positions into screen positions
    return (position[0]*TILE_DIMENSIONS[0]+TILE_DIMENSIONS[0]/2,position[1]*TILE_DIMENSIONS[1]+TILE_DIMENSIONS[1]/2)

def findDuplicates(iter1,iter2): ##sees if there are duplicates between iterables
    dupes = []
    for item in iter1:
        if item in iter2:
            dupes.append(item)
    return dupes

def getLeftPipDominoCell(absx,absy,domino): ##gets the cell a domino is placed in (we use left cause why not)
    xDiff = math.cos(math.radians(domino.angle))*-1*TILE_DIMENSIONS[0]/2
    yDiff = math.sin(math.radians(domino.angle))*TILE_DIMENSIONS[1]/2 ##no *-1 cause 0 is up
    return absCoordToCellCoord((absx+xDiff,absy+yDiff))
