from config import *
from Elements import *
from Enemies import *

class waveLoader():
    def __init__(self):
        self.wave = 0
        self.waveContents = WAVES
        self.state = "idle"
        self.loadFrames = 0
    
    def loadWave(self):
        enemyTimings = self.waveContents[self.wave]
        if self.loadFrames > max(enemyTimings.keys()):
            self.state = "idle"
        for frame,enemies in enemyTimings.items():
            if self.loadFrames == frame:
                for enemyType, coordinates in enemies.items():
                    self.loadEnemy(enemyType,coordinates)
    
    def loadEnemy(self,enemyType,coords):
        if enemyType == "Basic":
            for coordinate in coords:
                x = coordinate[0]/PLANNINGWIDTH*SCREENWIDTH
                y = coordinate[1]/PLANNINGHEIGHT*SCREENHEIGHT
                elementLibrary.addElement(Element("Enemy",BasicEnemy(x,y),False))
        if enemyType == "Triple":
            for coordinate in coords:
                x = coordinate[0]/PLANNINGWIDTH*SCREENWIDTH
                y = coordinate[1]/PLANNINGHEIGHT*SCREENHEIGHT
                elementLibrary.addElement(Element("Enemy",TripleEnemy(x,y),False))
        if enemyType == "UFO":
            for coordinate in coords:
                side = coordinate[0]
                y = coordinate[1]/PLANNINGHEIGHT*SCREENHEIGHT
                elementLibrary.addElement(Element("Enemy",UfoEnemy(side,y),False))
        if enemyType == "Sheild":
            for coordinate in coords:
                x = coordinate[0]/PLANNINGWIDTH*SCREENWIDTH
                y = coordinate[1]/PLANNINGHEIGHT*SCREENHEIGHT
                elementLibrary.addElement(Element("Enemy",ShieldEnemy(x,y),False))

    def next(self):
        if self.wave+1 in self.waveContents.keys():
            self.wave+=1
            self.state = "load"
        else:
            print("no wave found")
    
    def previous(self):
        if self.wave-1 in self.waveContents.keys():
            self.wave-=1
            self.state = "load"
        else:
            print("no wave found")

    def clearWave(self):
        if elementLibrary.get("Enemy"):
            elementLibrary.get("Enemy").empty()

    def update(self):
        if self.state == "load":
            self.loadWave()
            self.loadFrames+=1
        if self.state == "idle":
            if not elementLibrary.get("Enemy"):
                self.loadFrames = 0
                self.next()