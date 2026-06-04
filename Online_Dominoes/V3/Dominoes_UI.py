import pygame
from Dominoes_Logic import *
from util import *
from config import *

class UIElement(pygame.sprite.Sprite):
    def __init__(self, image = pygame.Surface((0, 0)), position = (0, 0)):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=position)

class UIPip(UIElement):
    def __init__(self, pip, position=(0, 0)):
        super().__init__(self.createPipImage(pip), position)
        self.pip = pip
        self.position = position
    
    def createPipImage(self, pip):
        surface = pygame.Surface((DOMINO_DIMENSIONS[1],DOMINO_DIMENSIONS[1]))
        surface.fill('#FFFFFF')
        pygame.draw.rect(surface, '#000000', surface.get_rect(), 2)
        pips = self.getPipCoordinates(pip)
        for pipCoord in pips:
            pygame.draw.circle(surface, '#000000', (int(pipCoord[0]), int(pipCoord[1])), PIP_DIAMETER/2)
        return surface

    def getPipCoordinates(self,pips):
        coordinates = []
        if pips == 0:
            return coordinates
        elif pips == 1:
            return [(TILE_DIMENSIONS[0]/2, TILE_DIMENSIONS[1]/2)]
        elif pips == 2:
            return [(TILE_DIMENSIONS[0]/4, TILE_DIMENSIONS[1]/4), (3*TILE_DIMENSIONS[0]/4, 3*TILE_DIMENSIONS[1]/4)]
        elif pips == 3:
            return self.getPipCoordinates(2) + self.getPipCoordinates(1)
        elif pips == 4:
            return [(TILE_DIMENSIONS[0]/4, TILE_DIMENSIONS[1]/4), (3*TILE_DIMENSIONS[0]/4, TILE_DIMENSIONS[1]/4), (TILE_DIMENSIONS[0]/4, 3*TILE_DIMENSIONS[1]/4), (3*TILE_DIMENSIONS[0]/4, 3*TILE_DIMENSIONS[1]/4)]
        elif pips == 5:
            return self.getPipCoordinates(4) + self.getPipCoordinates(1)
        elif pips == 6:
            return self.getPipCoordinates(4) + [(TILE_DIMENSIONS[0]/2, TILE_DIMENSIONS[1]/4), (TILE_DIMENSIONS[0]/2, 3*TILE_DIMENSIONS[1]/4)]
        else:
            raise ValueError("Pips must be between 0 and 6")

    def setAbsPos(self,position):
        self.position = position
        self.rect.center = position
    
    def isHovering(self,position):
        return self.rect.collidepoint(position)

class UIDomino(UIElement):
    def __init__(self, domino, position=(0, 0)):
        super().__init__()
        self.pips = pygame.sprite.Group()
        self.originalDomino = self.createDominoImage(domino)
        self.image = self.originalDomino
        self.rect = self.image.get_rect()
        self.angle = 0
        self.position = position
    
    def createDominoImage(self, domino):
        self.pips.add(UIPip(domino.left.pips, (TILE_DIMENSIONS[0]/2, TILE_DIMENSIONS[1]/2)))
        self.pips.add(UIPip(domino.right.pips, (TILE_DIMENSIONS[0]/2 + DOMINO_DIMENSIONS[0]/2, TILE_DIMENSIONS[1]/2)))
        tempSurface = pygame.Surface(DOMINO_DIMENSIONS)
        self.pips.draw(tempSurface)
        return tempSurface
        
    def rotateClockwise(self):
        self.angle -= 90
    
    def rotateCounterclockwise(self):
        self.angle += 90

    def resetDirection(self):
        self.angle = 0
        self.update()

    def setAbsPos(self,position):
        self.position = position
        self.rect.center = position
    
    def isHovering(self,position):
        return self.rect.collidepoint(position)

    def getPips(self):
        return [self.pips.sprites()[0].pip,self.pips.sprites()[1].pip]

    def update(self):
        if self.angle < 0:
            self.angle += 360
        elif self.angle > 360:
            self.angle -= 360
        self.rotatedDomino = pygame.transform.rotate(self.originalDomino,self.angle)
        self.image = self.rotatedDomino
        self.rect = self.rotatedDomino.get_rect()
        self.rect.center = self.position

class UIDashboard(UIElement):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0], DASHBOARD_DIMENSIONS))
        self.rect = self.image.get_rect(bottomleft=(0,SCREEN_DIMENSIONS[1] * TILE_DIMENSIONS[1]+DASHBOARD_DIMENSIONS))
        self.dominoes = pygame.sprite.Group()
    
    def draw(self):
        self.arrangeDominoes()
        self.drawDashboard()
        self.drawDominoes()
    
    def drawDashboard(self):
        self.image.fill(DASHBOARD_COLOR)
        pygame.draw.rect(self.image, '#FFFFFF', self.image.get_rect(), 2)
    
    def drawDominoes(self):
        self.dominoes.draw(self.image)
    
    def setDominoes(self,dominoList):
        self.dominoes.empty()
        for domino in dominoList:
            self.dominoes.add(UIDomino(domino))
    
    def arrangeDominoes(self):
        for i, domino in enumerate(self.dominoes.sprites()):
            row = i // DASHBOARD_MAX_DOMINOES_HORIZONTAL
            col = i % DASHBOARD_MAX_DOMINOES_HORIZONTAL
            x = DASHBOARD_DOMINO_SPACING + col * (DOMINO_DIMENSIONS[0] + DASHBOARD_DOMINO_SPACING) + DOMINO_DIMENSIONS[0]/2
            y = DASHBOARD_DOMINO_SPACING + row * (DOMINO_DIMENSIONS[1] + DASHBOARD_DOMINO_SPACING) + DOMINO_DIMENSIONS[1]/2
            domino.setAbsPos((x,y))
    
    def addDomino(self,domino):
        self.dominoes.add(UIDomino(domino))
    
    def removeDomino(self,domino):
        if domino in self.dominoes.sprites():
            self.dominoes.remove(domino)
    
    def getHovering(self,pos):
        pos = self.globalToLocal(pos)
        for domino in self.dominoes.sprites():
            print(domino.position)
            if domino.isHovering(pos):
                return domino
        return None

    def globalToLocal(self,position):
        return (position[0]-self.rect.x, position[1]-self.rect.y)
    
    def localToGlobal(self,position):
        return (position[0]+self.rect.x, position[1]+self.rect.y)
        
    def isHovering(self,position):
        return self.rect.collidepoint(position)

    def update(self):
        self.draw()
    
class UIBoard(UIElement):
    def __init__(self):
        super().__init__()
        self.pips = pygame.sprite.Group()
        self.image = pygame.Surface((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0], SCREEN_DIMENSIONS[1] * TILE_DIMENSIONS[1]))
        self.rect = self.image.get_rect()
        self.origin = (0,0)
    
    def updatePips(self,boardMatrix,origin):
        self.pips.empty()
        boardOrigin = origin
        for y,row in enumerate(boardMatrix):
            for x,cell in enumerate(row):
                if cell != BOARD_EMPTY:
                    pip = UIPip(cell)
                    boardCoords = [x-(boardOrigin[0]-self.origin[0]),y-(boardOrigin[1]-self.origin[1])]
                    pip.setAbsPos((cellCoordToAbsCoord(boardCoords)))
                    self.pips.add(pip)
    
    def clear(self):
        self.image.fill('#000000')
    
    def scrollLeft(self):
        self.origin = (self.origin[0]-1,self.origin[1])

    def scrollRight(self):
        self.origin = (self.origin[0]+1,self.origin[1])

    def scrollUp(self):
        self.origin = (self.origin[0],self.origin[1]-1)

    def scrollDown(self):
        self.origin = (self.origin[0],self.origin[1]+1)

    def updateBoard(self):
        self.pips.draw(self.image)
    
    def update(self,boardMatrix,origin):
        self.clear()
        self.updatePips(boardMatrix,origin)
        self.updateBoard()

class UIButton(UIElement):
    def __init__(self, text, position, dimensions,color,fontSize = 30):
        super().__init__()
        self.image = pygame.Surface(dimensions)
        self.rect = self.image.get_rect(center=position)
        self.font = pygame.font.SysFont('Arial', fontSize)
        self.text = self.font.render(text, True, '#FFFFFF')
        self.image.fill(color)
        pygame.draw.rect(self.image, '#FFFFFF', self.image.get_rect(), 2)
        textRect = self.text.get_rect(center=(self.rect.width/2,self.rect.height/2))
        self.image.blit(self.text,textRect)
    
    def isHovering(self,position):
        return self.rect.collidepoint(position)

class UIText(UIElement):
    def __init__(self,text,position,fontSize):
        super().__init__()
        self.position = position
        self.image = pygame.Surface((100,20),pygame.SRCALPHA)
        self.rect = self.image.get_rect(center = (self.image.width/2,self.image.height/2))
        self.font = pygame.font.SysFont('Arial',fontSize)
        self.text = self.font.render(text,True,'#FFFFFF')
        self.textRect = self.text.get_rect(center = (self.rect.width/2,self.rect.height/2))
        self.image.blit(self.text,self.textRect)
    
    def changeText(self,text):
        self.text = self.font.render(text,True,'#FFFFFF')
        self.textRect = self.text.get_rect(center = (self.rect.width/2,self.rect.height/2))
        self.image.fill('#000000')
        self.image.blit(self.text,self.textRect)

class UITitleScreen(UIElement):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0], SCREEN_DIMENSIONS[1] * TILE_DIMENSIONS[1]+DASHBOARD_DIMENSIONS))
        self.rect = self.image.get_rect()
        self.font = pygame.font.SysFont('Arial', 50)
        self.titleText = self.font.render('Dominoes', True, '#FFFFFF')
        self.startButton = UIButton('Start Game', TITLE_BUTTON_COORDS, TITLE_BUTTON_DIMENSIONS, TITLE_BUTTON_COLOR)
        self.instructionButton = UIButton('Instructions',(TITLE_BUTTON_COORDS[0],TITLE_BUTTON_COORDS[1]+TITLE_BUTTON_OFFSET),TITLE_BUTTON_DIMENSIONS,TITLE_BUTTON_COLOR)

        self.image.fill('#000000')
        titleRect = self.titleText.get_rect(center=TITLE_COORDS)
        self.image.blit(self.titleText,titleRect)
        self.image.blit(self.startButton.image,self.startButton.rect)
        self.image.blit(self.instructionButton.image,self.instructionButton.rect)
    
    def isHoveringStart(self,position):
        return self.startButton.isHovering(position)

    def isHoveringInstruction(self,position):
        return self.instructionButton.isHovering(position)

class UIWaitingScreen(UIElement):
    def __init__(self,text,fontSize = 30):
        super().__init__()
        self.image = pygame.Surface((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0], SCREEN_DIMENSIONS[1] * TILE_DIMENSIONS[1]+DASHBOARD_DIMENSIONS))
        self.rect = self.image.get_rect()
        self.font = pygame.font.SysFont('Arial', fontSize)
        self.waitingText = self.font.render(text, True, '#FFFFFF')
        self.image.fill('#000000')
        waitingRect = self.waitingText.get_rect(center=((SCREEN_DIMENSIONS[0]*TILE_DIMENSIONS[0])/2,(SCREEN_DIMENSIONS[1]*TILE_DIMENSIONS[1])/2))
        self.image.blit(self.waitingText,waitingRect)    
    

test = UIDashboard()
test.arrangeDominoes()

