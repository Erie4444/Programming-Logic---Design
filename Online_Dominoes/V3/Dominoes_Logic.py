import math
from config import *
import random
class Pips:
    '''
    Just a pip object used in dominos
    '''
    def __init__(self,pips,x=0,y=0):
        self.x = x
        self.y = y
        self.pips = pips
        self.isEnd = True ##is the end of the board
    
    def __str__(self):
        return str(self.pips)

    def getCoord(self):
        return (self.x,self.y)

class Domino:
    '''
    Domino object made with 2 pips
    '''
    def __init__(self,pipLeft,pipRight):
        self.left = Pips(pipLeft)
        self.right = Pips(pipRight)
        self.angle = 0 ##0 is horizontal, 90 is vertical, etc.
    
    def __str__(self):
        return f"[{self.left}|{self.right}]"
    
    def placeLeft(self,x,y): ##assigns pip positions based that you're placing the left pip on x,y
        xOffset, yOffset = self.findSecondPipOffset("left")
        self.left.x = x
        self.left.y = y
        self.right.x = x+xOffset
        self.right.y = y+yOffset

    def placeRight(self,x,y): ##assigns pip positions based that you're placing the right pip on x,y
        xOffset, yOffset = self.findSecondPipOffset("right")
        self.right.x = x
        self.right.y = y
        self.left.x = x+xOffset
        self.left.y = y+yOffset
    
    def place(self,lx,ly,rx,ry): ##force place function
        self.left.x = lx
        self.left.y = ly
        self.right.x = rx
        self.right.y = ry
    
    def getDomino(self):
        return [self.left.pips,self.right.pips]

    def deconstruct(self):
        ##deconstructs the domino so it's able to be sent over as a json
        return {"leftPip":self.left.pips,"leftX":self.left.x,"leftY":self.left.y,"rightPip":self.right.pips,"rightX":self.right.x,"rightY":self.right.y}

    def reconstruct(self,domino):
        ##reconstructs itself to be the same as the deconstructed domino sent over
        self.left = Pips(domino["leftPip"])
        self.right = Pips(domino["rightPip"])
        self.left.x, self.left.y = domino["leftX"],domino["leftY"]
        self.right.x, self.right.y = domino["rightX"],domino["rightY"]
    
    def findSecondPipOffset(self,sideyouHave):
        ##finds the offset of the other pip position based on the angle of the domino and the side you are placing
        if sideyouHave == "left":
            return round(math.cos(math.radians(self.angle))), -1*round(math.sin(math.radians(self.angle))) ##y is -1x because up in matricies have decreasing indexes
        elif sideyouHave == "right":
            return -1*round(math.cos(math.radians(self.angle))), round(math.sin(math.radians(self.angle))) ##-1x of outputs in "left" if because position is the opposite of left

    def printVars(self):
        print(self.left.pips,self.left.x,self.left.y,self.right.pips,self.right.x,self.right.y)

class DominoBoard:
    def __init__(self):
        self.board = AdaptiveBoard()
        ##left pip and right pip of the board (None because there aren't any dominos)
        self.right = False
        self.left = False
    
    def placeDomino(self,domino):
        ##places the domino based on the position on the left and right pips
        ##adds the Pip Object from the domino passed in
        self.board.addItemRel(domino.left.x,domino.left.y,domino.left)
        self.board.addItemRel(domino.right.x,domino.right.y,domino.right)
    
    def canPlacePip(self,domino):
        ##assumes its in a valid placement
        ##checks if the pip value of the domino matches the ends of the chain
        boardPip = self.findSidePlaced(domino)
        dominoPip = domino.left if domino.left.getCoord() in self.getOrthogonalCoords(boardPip.x,boardPip.y) else domino.right if domino.right.getCoord() in self.getOrthogonalCoords(boardPip.x,boardPip.y) else None
        if dominoPip:
            if boardPip.pips == dominoPip.pips:
                return True
        return False


    def placeDominoWithChecks(self, domino):
        ##places the dominos with validity checks
        if not (self.right or self.left): ##if there aren't any dominos, place it
            self.right = domino.right
            self.left = domino.left
            self.placeDomino(domino)
            return True
        else:
            if self.canPlaceDominoPositionally(domino): ##checks if the domino is in the valid placements
                if self.canPlacePip(domino): ##if the domino has matching pips
                    if self.findSidePlaced(domino) == self.left:
                        ##finds out which side is placed next to the chain, and which is the new end of the chain
                        if domino.left.getCoord() in self.getOrthogonalCoords(self.left.x,self.left.y) and domino.left.pips == self.left.pips:
                            self.left = domino.right
                        elif domino.right.getCoord() in self.getOrthogonalCoords(self.left.x,self.left.y) and domino.right.pips == self.left.pips:
                            self.left = domino.left

                    if self.findSidePlaced(domino) == self.right:
                        ##finds out which side is placed next to the chain, and which is the new end of the chain
                        if domino.left.getCoord() in self.getOrthogonalCoords(self.right.x,self.right.y) and domino.left.pips == self.right.pips:
                            self.right = domino.right
                        elif domino.right.getCoord() in self.getOrthogonalCoords(self.right.x,self.right.y) and domino.right.pips == self.right.pips:
                            self.right = domino.left
                    
                    ##places the domino on the board
                    self.placeDomino(domino)
                    return True

                else:
                    print("pip failed") ##pip placement failed
            else:
                print("pos failed") ##not valid position
        return False

    def canPlaceDominoPositionally(self,domino): ##checks if position of domino is valid
        ##gets all valid positions
        globalValidPositions = self.calculateGlobalValidPositions()[self.left]+self.calculateGlobalValidPositions()[self.right]
        for orthoPos, orthoPos2 in globalValidPositions:
            ##checks if the position pairs are the same as the domino pip positions
            if orthoPos in [domino.left.getCoord(),domino.right.getCoord()] and orthoPos2 in [domino.left.getCoord(),domino.right.getCoord()]:
                return True
        return False

    def findSidePlaced(self,domino): ##finds the side the domino was placed on
        ##if the position is the same as the domino position, then return the side the position is on
        for side, poses in self.calculateGlobalValidPositions().items():
            for orthoPos, orthoPos2 in poses:
                if orthoPos in [domino.left.getCoord(),domino.right.getCoord()] and orthoPos2 in [domino.left.getCoord(),domino.right.getCoord()]:
                    return side
        return False

    def calculateGlobalValidPositions(self):
        ##gets all the valid positions and sorts them as which one is on the left side and which is right
        leftPoses = self.calculateValidPositions(self.left.x,self.left.y)
        rightPoses = self.calculateValidPositions(self.right.x,self.right.y)
        return {self.left : leftPoses, self.right : rightPoses}
    

    def calculateValidPositions(self,x,y):
        """Calculates valid positions for dominos
        returns in position pairs"""
        ##[(x,y),(x,y)] first pos is directly orthogonal to the edge of the chain
        validPositions = []
        for orthoCell in self.checkOrthogonalCells(x,y,BOARD_EMPTY):
            for orthoCell2 in self.checkOrthogonalCells(orthoCell[0],orthoCell[1],BOARD_EMPTY): ##second degree ortho
                validPositions.append([orthoCell,orthoCell2])
        return validPositions

    def checkOrthogonalCells(self,x,y,itemToCheck):
        ##checks which cells orthogonal to x,y is itemToCheck
        validCells = []
        for X,Y in self.getOrthogonalCoords(x,y):
            if self.board.getItemRel(X,Y) == itemToCheck:
                validCells.append((X,Y))
        return validCells

    def getOrthogonalCoords(self,x,y):
        ##gets the coordinates orthogonal to x,y
        coords = []
        orthogonalOffsets = [(0,1),(1,0),(0,-1),(-1,0)]
        for xOffset,yOffset in orthogonalOffsets:
            coords.append((x+xOffset,y+yOffset))
        return coords

    def debug(self):
        ##To test the logic itself
        running = True
        while running:
            print("=====DEBUG=====\n - d place domino\n - p print board\n - q quit")
            user = input(">> ")
            if user == "d":
                print("input pip values (l,r)")
                pipL, pipR = input(">> ").split(",")
                debugDomino = Domino(int(pipL),int(pipR))
                print("input angle of domino")
                angle = int(input(">> "))
                debugDomino.angle = angle
                print("place left or right")
                side = input(">> ")
                print("input pos (x,y)")
                x,y = input(">> ").split(",")
                if side == "left":
                    debugDomino.placeLeft(int(x),int(y))
                elif side == "right":
                    debugDomino.placeRight(int(x),int(y))
                self.placeDominoWithChecks(debugDomino)
                print("placed!")
            
            elif user == "p":
                self.board.printBoard()
            
            elif user == "q":
                running = False
                
class AdaptiveBoard:
    """All x,y parameters are matrix coordinates\n
    x - column index\n
    y - row index\n
    Board will expand to accomodate the position\n
    Negative indecies are above or to the left of the matrix"""

    ##this is a board that can expand if an item is placed outside of its bounds
    ##it keeps track of the original origin it started with so we can draw the dominos at the same positions

    def __init__(self,startDimensions = (1,1)):
        self.origin = [0,0]
        self.rows = startDimensions[0]
        self.cols = startDimensions[1]
        self.board = [[BOARD_EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
    
    ##EXPANSION FUNCTIONS
    def expandDown(self):
        self.board.append([BOARD_EMPTY for _ in range(self.cols)])
        self.rows+=1
    
    def expandUp(self):
        self.board.insert(0,[BOARD_EMPTY for _ in range(self.cols)])
        self.origin[1]+=1
        self.rows+=1
    
    def expandRight(self):
        for row in range(self.rows):
            self.board[row].append(BOARD_EMPTY)
        self.cols+=1
    
    def expandLeft(self):
        for row in range(self.rows):
            self.board[row].insert(0,BOARD_EMPTY)
        self.origin[0]+=1
        self.cols+=1
    
    def checkCoordinates(self,x,y):
        ##checks if a coordinate is valid, if its outside, expand the board
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
        ##adds items based on the current origin
        x,y = self.checkCoordinates(x,y)
        self.board[y][x] = item
    
    def addItemRel(self,x,y,item):
        ##adds an item based on the tracked original origin
        x,y = self.convertRelToAbs(x,y)
        self.addItem(x,y,item)
    
    def getItem(self,x,y):
        ##gets an item based on the current origin
        x,y = self.checkCoordinates(x,y)
        return self.board[y][x]

    def getItemRel(self,x,y):
        ##gets an item based on the tracked original origin
        x,y = self.convertRelToAbs(x,y)
        return self.getItem(x,y)

    def getOrigin(self):
        return self.origin

    def isEmpty(self):
        return all(item == '' for item in self.board)

    def getBoard(self):
        return self.board

    def convertRelToAbs(self,x,y):
        ##converts the original origin coordinates to current origin coordinates
        return (x+self.origin[0],y+self.origin[1])
    
    def convertAbsToRel(self,x,y):
        ##converts the current origin coordinates to original origin coordinates
        return (x-self.origin[0],y-self.origin[1])

    def printBoard(self): ##Prints a pretty version of the board
        for i in range(self.rows):
            printRow = []
            for item in self.board[i]:
                printRow.append(str(item))
            yAxis = (' '*(4-len(str(i-self.origin[1])))) + str(i-self.origin[1]) + " |"
            print(yAxis,printRow)
        print("======="+"="*5*self.cols)
        xValues = [str(i-self.origin[0]) for i in range(self.cols)]
        xAxis = " "*7
        for xValue in xValues:
            xAxis+=' '*(3-len(xValue)) + xValue + '  '
        print(xAxis)
      
    def inBoard(self,x,y):
        ##checks if a position is inside the board
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return True
        return False
    
    def inBoardRel(self,x,y):
        ##checks if the position is inside the board based on the original coordinates
        x,y = self.convertRelToAbs(x,y)
        return self.inBoard(x,y)
    
    def clearBoard(self):
        self.board = [[BOARD_EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

    def checkOrigin(self):
        ##used for debug, checks where the original origin is
        self.clearBoard()
        self.board[self.origin[1]][self.origin[0]] = 'x'
        self.printBoard()
    
    def deconstruct(self):
        ##deconstructs the whole board to send over json
        deconstructed = [[BOARD_EMPTY if self.board[j][i] == BOARD_EMPTY else self.board[j][i].pips for i in range(self.cols)] for j in range(self.rows)]
        return deconstructed
    
    def testBoard(self):
        ##debug to test the expanding features of the board
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

class DominoList:
    '''
    Just a list of dominos
    '''
    def __init__(self, dominoes):
        self.dominoes = dominoes
    
    def __str__(self):
        return " ".join(str(d) for d in self.dominoes)
    
    def addDomino(self, domino):
        self.dominoes.append(domino)
    
    def removeDomino(self, domino):
        self.dominoes.remove(domino)
    
    def removeDominoAtIndex(self, index):
        return self.dominoes.pop(index)

    def getList(self):
        return self.dominoes

class Hand(DominoList):
    '''
    Added additional features to DominoList
    to act as a player hand
    '''
    def __init__(self, dominoes):
        super().__init__(dominoes)
    
    def playDomino(self, domino): ##before the confirmation that it is playable
        ##check if the domino is in the hand
        if domino in self.dominoes:
            return domino
        else:
            return False
    
    def drawDomino(self, domino):
        self.addDomino(domino)
    
    def hasDominoWithPip(self,pips):
        ##check if the hand has a domino with a specific pip
        ##used to check if you have playable dominos
        for domino in self.dominoes:
            if pips in domino.getDomino():
                return True
        return False

    def getDominoWithPips(self,pips):
        ##gets a domino with specific pips
        ##used to get the logic domino from the UI domino
        for domino in self.dominoes:
            if pips[0] == domino.getDomino()[0] and pips[1] == domino.getDomino()[1]:
                return domino
        return False  
    
class Boneyard(DominoList):
    '''
    Expanded features of DominoList
    to act as a draw pile
    '''
    def __init__(self):
        dominoes = [Domino(i, j) for i in range(7) for j in range(i, 7)]
        super().__init__(dominoes)
    
    def shuffle(self):
        ##shuffles the deck
        random.shuffle(self.dominoes)
    
    def drawDomino(self):
        ##draws a domino, if empty return false
        if self.dominoes:
            return self.removeDominoAtIndex(0)
        else:
            print("boneyard empty")
            return False

class ServerLogic:
    '''
    Logic used in the server code
    '''
    def __init__(self):
        self.board = DominoBoard()
        self.boneyard = Boneyard()
        self.currentPlayer = 1
    
    def getCurrentPlayer(self):
        return self.currentPlayer
    
    def nextPlayer(self):
        ##passes the turn to the next player
        self.currentPlayer+=1
        if self.currentPlayer > NUM_PLAYERS:
            self.currentPlayer = 1

    def initGame(self):
        self.boneyard.shuffle()
        self.dealHands()

    def dealHands(self):
        ##makes a list of Hand Objects, all drawn from the boneyard
        self.hands = [Hand([]) for i in range(NUM_PLAYERS)]
        for i in range(PLAYER_HAND_LIMIT):
            for j in range(NUM_PLAYERS):
                self.hands[j].addDomino(self.boneyard.drawDomino())
    
    def getHands(self):
        try:
            return self.hands
        except:
            print("dealHands method not run!")
    
    def placeDomino(self,domino):
        ##places a domino on the board
        return self.board.placeDominoWithChecks(domino)

    def placeDominoDB(self,domino):
        ##debug force place domino on the board
        self.board.placeDomino(domino)
        return True

    def drawDomino(self):
        ##draws a domino
        if len(self.boneyard.getList()) > 0:
            return self.boneyard.drawDomino()
    
class ClientLogic:
    '''
    Logic used in the client code
    '''
    def __init__(self,hand):
        self.hand = hand
    
    def playDomino(self,domino):
        return self.hand.playDomino(domino)

    def getLogicDomino(self,pips):
        return self.hand.getDominoWithPips(pips)

    def getScore(self):
        ##gets the score based on the dominos in the player's hand
        score = 0
        if len(self.hand.getList()) == 0:
            return -1
        for domino in self.hand.getList():
            score+=domino.left.pips
            score+=domino.right.pips
        return score