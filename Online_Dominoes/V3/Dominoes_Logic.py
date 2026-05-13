import math
class Pips:
    def __init__(self,pips,x=0,y=0):
        self.x = x
        self.y = y
        self.pips = pips
        self.isEnd = True

class Domino:
    def __init__(self,pipLeft,pipRight):
        self.left = Pips(pipLeft)
        self.right = Pips(pipRight)
        self.angle = 0 ##0 is horizontal, 90 is vertical, etc.
    
    def placeLeft(self,x,y): ##places the domino based position of the left side
        pass

    def findSecondPipOffset(self): ##relative idfk
        return round(math.cos(math.radians(self.angle))), round(math.sin(math.radians(self.angle)))

testDomino = Domino(1,2)
print(testDomino.findSecondPipOffset())
testDomino.angle = 90
print(testDomino.findSecondPipOffset())
testDomino.angle = 180
print(testDomino.findSecondPipOffset())
testDomino.angle = 270
print(testDomino.findSecondPipOffset())
