import math
class Pips:
    def __init__(self,pips,x=0,y=0):
        self.x = x
        self.y = y
        self.pips = pips
        self.isEnd = True
    
    def __str__(self):
        return str(self.pips)

class Domino:
    def __init__(self,pipLeft,pipRight):
        self.left = Pips(pipLeft)
        self.right = Pips(pipRight)
        self.angle = 0 ##0 is horizontal, 90 is vertical, etc.
    
    def placeLeft(self,x,y): ##gets coordinates to place a domino assuming left side is the connecting side
        xOffset, yOffset = self.findSecondPipOffset("left")
        self.left.x = x
        self.left.y = y
        self.right.x = x+xOffset
        self.right.y = y+yOffset

    def placeRight(self,x,y):
        xOffset, yOffset = self.findSecondPipOffset("right")
        self.right.x = x
        self.right.y = y
        self.left.x = x+xOffset
        self.left.y = y+yOffset

    def findSecondPipOffset(self,sideyouHave):
        if sideyouHave == "left":
            return round(math.cos(math.radians(self.angle))), -1*round(math.sin(math.radians(self.angle))) ##y is -1x because up in matricies have decreasing indexes
        elif sideyouHave == "right":
            return -1*round(math.cos(math.radians(self.angle))), round(math.sin(math.radians(self.angle))) ##-1x of outputs in "left" if because position is the opposite of left

class DominoBoard:
    ##all x,y parameters are relative to the 1st domino (not indexes for self.board because it can expand backwards)
    def __init__(self):
        self.board = AdaptiveBoard()
        self.rightCoord = (1,0)
        self.leftCoord = (0,0)
        self.board.addItem(0,0,Pips(4))
        self.board.addItem(1,0,Pips(3))
        self.board.addItem(2,1,Pips(1))
        self.board.addItem(3,0,Pips(2))
        self.board.addItem(2,-1,Pips(5))
        self.board.addItemRel(-1,0,Pips(6))
        self.board.printBoard()
    
    def placeDomino(self,domino):
        self.board.addItem(domino.left.x,domino.left.y,domino.left)
        self.board.addItem(domino.right.x,domino.right.y,domino.right)
    
    def calculateValidPositions(self):
        validPositions = {"left":[],"right":[]}
        orthogonalOffsets = [(0,1),(1,0),(0,-1),(-1,0)]
        for xOffset,yOffset in orthogonalOffsets:
            if self.board.getItemRel(self.leftCoord[0]+xOffset,self.leftCoord[1]+yOffset) == '':
                for xOffset2,yOffset2 in orthogonalOffsets:
                    if self.board.getItemRel(self.leftCoord[0]+xOffset+xOffset2,self.leftCoord[1]+yOffset+yOffset2) == '':
                        validPositions["left"].append((self.leftCoord[0]+xOffset,self.leftCoord[1]+yOffset))
                        break
    
        for xOffset,yOffset in orthogonalOffsets:
            if self.board.getItemRel(self.rightCoord[0]+xOffset,self.rightCoord[1]+yOffset) == '':
                for xOffset2,yOffset2 in orthogonalOffsets:
                    if self.board.getItemRel(self.rightCoord[0]+xOffset+xOffset2,self.rightCoord[1]+yOffset+yOffset2) == '':
                        validPositions["right"].append((self.rightCoord[0]+xOffset,self.rightCoord[1]+yOffset))
                        break
        ##check if current pos has pips, go through ortho squares, and if no pips, append
        return validPositions

    def getOrthogonalPips(self,x,y):
        """Gets the pips in orthogonal tiles from x,y"""
        orthogonalOffsets = [(0,1),(1,0),(0,-1),(-1,0)]
        output = {}
        for xOffset, yOffset in orthogonalOffsets:
            if self.board.inBoardRel(x+xOffset,y+yOffset):
                if self.board.getItemRel(x+xOffset,y+yOffset) != '':
                    ##idk if i should return the offset or relative coord as key then pip as value
                    output[(xOffset,yOffset)] = self.board.getItemRel(x+xOffset,y+yOffset).pips
        return output
    

class AdaptiveBoard():
    """All x,y parameters are matrix coordinates\n
    x - column index\n
    y - row index\n
    Board will expand to accomodate the position\n
    Negative indecies are above or to the left of the matrix"""

    def __init__(self,startDimensions = (1,1)):
        self.origin = [0,0]
        self.rows = startDimensions[0]
        self.cols = startDimensions[1]
        self.board = [['' for _ in range(self.cols)] for _ in range(self.rows)]
    
    def expandDown(self):
        self.board.append(['' for _ in range(self.cols)])
        self.rows+=1
    
    def expandUp(self):
        self.board.insert(0,['' for _ in range(self.cols)])
        self.origin[1]+=1
        self.rows+=1
    
    def expandRight(self):
        for row in range(self.rows):
            self.board[row].append('')
        self.cols+=1
    
    def expandLeft(self):
        for row in range(self.rows):
            self.board[row].insert(0,'')
        self.origin[0]+=1
        self.cols+=1
    
    def checkCoordinates(self,x,y):
        if x < 0:
            for _ in range(abs(x)):
                self.expandLeft()
            x=0
        if x >=self.cols:
            for _ in range(x-self.cols+1):
                self.expandRight()
        if y < 0:
            for _ in range(abs(y)):
                self.expandUp()
            y=0
        if y >= self.rows:
            for _ in range(y-self.rows+1):
                self.expandDown()
        return x,y

    def addItem(self,x,y,item):
        x,y = self.checkCoordinates(x,y)
        self.board[y][x] = item
    
    def addItemRel(self,x,y,item):
        x,y = self.convertRelToAbs(x,y)
        self.addItem(x,y,item)
    
    def getItem(self,x,y):
        x,y = self.checkCoordinates(x,y)
        return self.board[y][x]

    def getItemRel(self,x,y):
        x,y = self.convertRelToAbs(x,y)
        return self.getItem(x,y)

    def getOrigin(self):
        return self.origin

    def getBoard(self):
        return self.board

    def convertRelToAbs(self,x,y):
        return (x+self.origin[0],y+self.origin[1])
    
    def convertAbsToRel(self,x,y):
        return (x-self.origin[0],y-self.origin[1])

    def printBoard(self):
        for row in self.board:
            printRow = []
            for item in row:
                printRow.append(str(item))
            print(printRow)
                
    def inBoard(self,x,y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return True
        return False
    
    def inBoardRel(self,x,y):
        x,y = self.convertRelToAbs(x,y)
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return True
        return False
    
    def clearBoard(self):
        self.board = [['' for _ in range(self.cols)] for _ in range(self.rows)]

    def checkOrigin(self):
        self.clearBoard()
        self.board[self.origin[1]][self.origin[0]] = 'x'
        self.printBoard()
    
    def testBoard(self):
        debugInput = input("Testing the adaptive board, type \"quit\" to exit, press Enter to continue...")
        while True:
            print("===========================DEBUG=======================")
            debugInput = input("1 - addItem\n2 - addItemRel\n3 - getItem\n4 - getItemRel\n5 - checkOrigin\n>> ")
            if debugInput == "quit":
                return
            else:
                debugInput = int(debugInput)
                if debugInput < 5:
                    x,y = [int(item) for item in input("coordinate (x,y): ").split(",")]
                    if debugInput < 3: 
                        item = input("item to add: ")

                    if debugInput == 1:
                        self.addItem(x,y,item)
                    elif debugInput == 2:
                        self.addItemRel(x,y,item)
                    elif debugInput == 3:
                        print(self.getItem(x,y))
                    elif debugInput == 4:
                        print(self.getItemRel(x,y))
                    self.printBoard()
                else:
                    self.checkOrigin()
                

test = DominoBoard()
print(test.calculateValidPositions())
