from collections import deque
import random
from config import *

class Domino:
    def __init__(self, pips):
        self.left, self.right = pips
    
    def __str__(self):
        return f"[{self.left}|{self.right}]"

    def canPlace(self, pip):
        return self.left == pip or self.right == pip

    def flip(self):
        self.left, self.right = self.right, self.left
    
    def tuple(self):
        return (self.left, self.right)

class DominoList:
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
    
    def getPlayableDominoes(self, pip):
        return [d for d in self.dominoes if d.canPlace(pip)]

    def getList(self):
        return self.dominoes
    

class Hand(DominoList):
    def __init__(self, dominoes):
        super().__init__(dominoes)
    
    def playDomino(self, domino):
        if domino in self.dominoes:
            self.removeDomino(domino)
            return domino
        else:
            raise ValueError("Domino not in hand")
    
    def drawDomino(self, domino):
        self.addDomino(domino)
    
class Boneyard(DominoList):
    def __init__(self):
        dominoes = [Domino((i, j)) for i in range(7) for j in range(i, 7)]
        super().__init__(dominoes)
    
    def shuffle(self):
        random.shuffle(self.dominoes)
    
    def drawDomino(self):
        if self.dominoes:
            return self.removeDominoAtIndex(0)
        
        else:
            raise ValueError("Bone yard is empty")

class Board:
    '''
    Board is a line of dominoes placed end to end
    '''
    def __init__(self):
        self.dominoes = deque()
    
    def __str__(self):
        return " ".join(str(d) for d in self.dominoes)
    
    def placeDomino(self, domino, end):
        '''
        end should be "left" or "right" indicating which end of the board to place the domino on
        '''
        if not self.dominoes:
            self.dominoes.append(domino)
            return True

        elif end == "left":
            if domino.canPlace(self.dominoes[0].left):
                ##to match left side of board to right side of domino
                if domino.left == self.dominoes[0].left:
                    print("flipped")
                    domino.flip()
                self.dominoes.appendleft(domino)
                return True
            else:
                return False
            
        elif end == "right":
            if domino.canPlace(self.dominoes[-1].right):
                ##to match right side of board to left side of domino
                if domino.right == self.dominoes[-1].right:
                    print("flipped")
                    domino.flip()
                self.dominoes.append(domino)
                return True
            else:
                return False
        else:
            raise ValueError("End must be 'left' or 'right'")
    
    def getPlayableEnds(self,domino):
        playable_ends = []
        if self.dominoes:
            if domino.canPlace(self.dominoes[0].left):
                playable_ends.append("left")
            if domino.canPlace(self.dominoes[-1].right):
                playable_ends.append("right")
        else:
            playable_ends = ["left", "right"]
        
        return playable_ends
    

class Player:
    def __init__(self, name, hand):
        self.name = name
        self.hand = hand
    
    def __str__(self):
        return f"{self.name}: {self.hand}"
    
    def playDomino(self, domino):
        return self.hand.playDomino(domino)
    
    def drawDomino(self, domino):
        self.hand.drawDomino(domino)
    
class Game:
    def __init__(self, players):
        self.players = [Player(name, Hand([])) for name in players]
        self.boneyard = Boneyard()
        self.board = Board()
        self.currentPlayerIndex = 0
        self.boneyard.shuffle()
        self.deal()
    
    def deal(self):
        for i in range(PLAYER_HAND_LIMIT):
            for player in self.players:
                player.drawDomino(self.boneyard.drawDomino())
    
    def getCurrentPlayer(self):
        return self.players[self.currentPlayerIndex]
    
    def nextTurn(self):
        self.currentPlayerIndex = (self.currentPlayerIndex + 1) % len(self.players)
    
    def status(self):
        print("Board:", self.board)
        for player in self.players:
            print(player)
        print("Boneyard:", len(self.boneyard.dominoes), "dominoes left")
    
    def testDominoPlacement(self):
        test_domino = input("Enter a domino to test (format: left,right): ")
        test_domino = tuple(map(int, test_domino.split(",")))
        test_domino = Domino(test_domino)
        print("Playable ends for", test_domino, ":", self.board.getPlayableEnds(test_domino))
        if self.board.getPlayableEnds(test_domino):
            end = input("Enter end to place domino (left/right): ")
            if self.board.placeDomino(test_domino, end):
                print("Domino placed on the board.")
            else:
                print("Invalid move.")
        print(self.board)