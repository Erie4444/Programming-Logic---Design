import pygame
from Dominoes_Logic import *
from util import *
from config import *

class DominoesUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0], SCREEN_DIMENSIONS[1] * TILE_DIMENSIONS[1]))
        pygame.display.set_caption("Dominoes")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game = None
        self.selectedDomino = None 
        self.dominoes = pygame.sprite.Group(UIDomino(Domino((1,2)),(100,100)),UIDomino(Domino((3,4)),(100,200)),UIDomino(Domino((5,6)),(100,300)))
        self.run()

    def draw(self):
        self.screen.fill('#000000')
        self.dominoes.draw(self.screen)
        if self.game:
            # Here you would draw the game state (players, hands, board, etc.)
            pass
        pygame.display.update()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.selectedDomino:
                    for domino in self.dominoes.sprites():
                        if domino.isHovering(event.pos):
                            self.selectedDomino = domino
                else:
                    self.selectedDomino = None
            
            if event.type == pygame.MOUSEMOTION:
                if self.selectedDomino:
                    self.selectedDomino.setAbsPos(event.pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.selectedDomino.rotateCounterclockwise()
                if event.key == pygame.K_x:
                    self.selectedDomino.rotateClockwise()
        self.dominoes.update()

    def run(self):
        while self.running:
            self.update()
            self.draw()
            self.clock.tick(60)  # Limit to 60 FPS
        pygame.quit()

class UIElement(pygame.sprite.Sprite):
    def __init__(self, image = pygame.Surface((0, 0)), position = (0, 0)):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=position)
    
class UIDomino(UIElement):
    def __init__(self, domino, position=(0, 0)):
        self.originalDomino = self.createDominoImage(domino)
        super().__init__(self.originalDomino, position)
        self.angle = 0
        self.position = position
    
    def createDominoImage(self, domino):
        surface = pygame.Surface(DOMINO_DIMENSIONS)
        surface.fill('#FFFFFF')
        pygame.draw.rect(surface, '#000000', surface.get_rect(), 2)  # Draw border
        left_pips = self.getPipCoordinates(domino.left)
        right_pips = self.getPipCoordinates(domino.right)
        for pip in left_pips:
            pygame.draw.circle(surface, '#000000', (int(pip[0]), int(pip[1])), PIP_DIAMETER/2)
        for pip in right_pips:
            pygame.draw.circle(surface, '#000000', (int(pip[0]+DOMINO_DIMENSIONS[0]/2), int(pip[1])), PIP_DIAMETER/2)
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
    
    def rotateClockwise(self):
        self.angle -= 90
    
    def rotateCounterclockwise(self):
        self.angle += 90

    def setAbsPos(self,position):
        self.position = position
    
    def isHovering(self,position):
        return self.rect.collidepoint(position)

    def update(self):
        if self.angle < 0:
            self.angle += 360
        elif self.angle > 360:
            self.angle -= 360
        self.rotatedDomino = pygame.transform.rotate(self.originalDomino,self.angle)
        self.image = self.rotatedDomino
        self.rect = self.rotatedDomino.get_rect()
        self.rect.center = self.position


UI = DominoesUI()

