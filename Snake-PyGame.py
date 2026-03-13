"""
Eric Zhao
3/6/2026
A snake game made in pygame
Snake:
A game where you control a snake using arrow keys
the snake starts small, but as you eat apples to increase your score,
the snake body gets bigger
you die if you hit the boundaries or yourself
"""
##------IMPORTS----------
import pygame as pygame
from sys import exit
import math
import random
##-------CONSTANTS--------
CELL_WIDTH = 25
##board size (in cells)
WIDTH = 20
HEIGHT = 20
STARTINGLENGTH = 3

##a object for each segment in the snake
class SnakeSegment(pygame.sprite.Sprite):
    ##required attributes
    ##self.image -> pygame.Surface
    ##self.rect -> pygame.Rect
    def __init__(self,coord:tuple):
        super().__init__()
        self.color = "#20FF20"
        self.height = CELL_WIDTH
        self.width = CELL_WIDTH
        self.segmentNumber = 0
        self.image = pygame.Surface((self.height,self.width))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft = coord)
    
    ##sets the color of the segment
    def setColor(self,color):
        self.color = color
        self.image.fill(self.color)

    ##increases the segment number for the game logic
    def update(self):
        self.segmentNumber+=1
    
class Apple(pygame.sprite.Sprite):
    ##basically the same attributes as SnakeSegment
    def __init__(self,coord:tuple):
        super().__init__()
        self.color = "#F30000"
        self.height = CELL_WIDTH
        self.width = CELL_WIDTH
        self.image = pygame.Surface((self.height,self.width))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft = coord)

##converts the coordinates in cell units into normal pixel units
def convertCellCoordtoAbsCoord(coord:tuple):
    return (coord[0]*CELL_WIDTH,coord[1]*CELL_WIDTH)

##converts pixel coordinates into cell coordinates
def convertAbsCoordtoCellCoord(coord:tuple):
    return (int(coord[0]/CELL_WIDTH),int(coord[1]/CELL_WIDTH))

##returns the segment in the snake that is the head
def findSnakeHead(group:pygame.sprite.Group):
    for segment in group:
        if segment.segmentNumber == 0:
            return segment

##returns the segment in the snake that is the tail
def findSnakeTail(group:pygame.sprite.Group, length:int):
    for segment in group:
        if segment.segmentNumber == length-1:
            return segment

##verifies if the direction pressed is a valid direction (i.e. the opposite direction the snake is facing)
def validDirection(key,direction):
    if key == pygame.K_UP and direction != "DOWN" or key == pygame.K_DOWN and direction != "UP" or key == pygame.K_LEFT and direction != "RIGHT" or key == pygame.K_RIGHT and direction != "LEFT":
        return True
    return False

##=========================main===============================
pygame.init()
screen = pygame.display.set_mode((CELL_WIDTH*WIDTH,CELL_WIDTH*HEIGHT))
clock = pygame.time.Clock()
runGame = True
gameState = "MENU"
font = pygame.font.Font()
highScore = 0
##game loop
while runGame:
    ##======EVENT HANDLER========
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        ##key inputs
        if event.type == pygame.KEYDOWN:
            if gameState == "GAME":
                ##snake inputs
                if validDirection(event.key,snakeDirection):
                    if event.key == pygame.K_UP:
                        snakeDirection = "UP"
                    if event.key == pygame.K_DOWN:
                        snakeDirection = "DOWN"
                    if event.key == pygame.K_LEFT:
                        snakeDirection = "LEFT"
                    if event.key == pygame.K_RIGHT:
                        snakeDirection = "RIGHT"
            elif gameState == "MENU":
                ##setting up the game
                snakeDirection = "RIGHT"
                score = 0
                snakeLength = STARTINGLENGTH
                ##making starting snake
                snake = pygame.sprite.Group()
                for i in range(STARTINGLENGTH):
                    tempSprite = SnakeSegment(
                        convertCellCoordtoAbsCoord((STARTINGLENGTH-i-1,math.floor(HEIGHT/2)))
                        )
                    tempSprite.segmentNumber = i
                    snake.add(tempSprite)
                apples = pygame.sprite.Group()
                apples.add(Apple(convertCellCoordtoAbsCoord((math.ceil(WIDTH/4*3),int(HEIGHT/2)))))
                gameState = "GAME"
            
            ##setting the gamestate to menu after you press the button in the lose or win menus
            elif gameState == "LOSE":
                gameState = "MENU"
            elif gameState == "WIN":
                gameState = "MENU"

##================SNAKE GAME==================
    if gameState == "GAME":
        head = findSnakeHead(snake)
        tail = findSnakeTail(snake,snakeLength)
        headCoord = convertAbsCoordtoCellCoord(head.rect.topleft)

        ##adding the new head based on the current snake direction
        for segment in snake: segment.update()
        if snakeDirection == "RIGHT":
            snake.add(SnakeSegment(convertCellCoordtoAbsCoord((headCoord[0]+1,headCoord[1]))))
        if snakeDirection == "LEFT":
            snake.add(SnakeSegment(convertCellCoordtoAbsCoord((headCoord[0]-1,headCoord[1]))))
        if snakeDirection == "UP":
            snake.add(SnakeSegment(convertCellCoordtoAbsCoord((headCoord[0],headCoord[1]-1))))
        if snakeDirection == "DOWN":
            snake.add(SnakeSegment(convertCellCoordtoAbsCoord((headCoord[0],headCoord[1]+1))))

        ##========COLLISION HANDLER==========
        ##checking if head collides with snake (without the snake head)
        if [segment for segment in pygame.sprite.spritecollide(head,snake,False) if segment != head]:
            snake.empty()
            apples.empty()
            gameState = "LOSE"
        ##checking for border collision
        if headCoord[0] < 0 or headCoord[0] > WIDTH-1 or headCoord[1] < 0 or headCoord[1] > HEIGHT-1:
            snake.empty()
            apples.empty()
            gameState = "LOSE"
        ##checking for apple collision
        if pygame.sprite.spritecollide(head,apples,True):
            ##finding empty coords to put the apple in
            snakeCoords = [segment.rect.topleft for segment in snake]
            emptyCoords = [(i,j) for i in range(WIDTH) for j in range(HEIGHT) if not convertCellCoordtoAbsCoord((i,j)) in snakeCoords]
            apples.add(Apple(convertCellCoordtoAbsCoord(random.choice(emptyCoords))))
            score+=1
            snakeLength+=1
            if highScore < score: highScore = score
        else:
            ##remove the extra tail segment
            tail.kill()
        
        if snakeLength >= WIDTH*HEIGHT:
            gameState = "WIN"

        ##----game updates----
        screen.fill("#000000")
        apples.draw(screen)
        snake.draw(screen)
        ##drawing the score text
        scoreText = font.render(f"Score: {score} Highscore: {highScore}",True,"#FFFFFF")
        scoreTextRect = scoreText.get_rect(topleft = (0,0))
        screen.blit(scoreText,scoreTextRect)

    elif gameState == "MENU":
        ##drawing the menu text
        screen.fill("#000000")
        title = font.render("Snake",True,"#FFFFFF")
        titleRect = title.get_rect(center = convertCellCoordtoAbsCoord((WIDTH/2,HEIGHT/2)))
        text = font.render("Press any key to begin",True,"#FFFFFF")
        textRect = text.get_rect(center = convertCellCoordtoAbsCoord((WIDTH/2,HEIGHT/2+2)))
        screen.blit(title,titleRect)
        screen.blit(text,textRect)
    
    elif gameState == "LOSE":
        ##drawing the lose text
        screen.fill("#000000")
        loseHeading = font.render("You Died...",True,"#FFFFFF")
        loseHeadingRect = title.get_rect(center = convertCellCoordtoAbsCoord((WIDTH/2,HEIGHT/2-2)))
        scoreText = font.render(f"Score: {score} Highscore: {highScore}",True,"#FFFFFF")
        scoreTextRect = text.get_rect(center = convertCellCoordtoAbsCoord((WIDTH/2,HEIGHT/2)))
        continueText = font.render("Press any key to continue",True,"#FFFFFF")
        continueTextRect = text.get_rect(center = convertCellCoordtoAbsCoord((WIDTH/2,HEIGHT/2+2)))
        screen.blit(loseHeading,loseHeadingRect)
        screen.blit(scoreText,scoreTextRect)  
        screen.blit(continueText,continueTextRect)  

    elif gameState == "WIN":
        ##drawing the win text
        screen.fill("#000000")
        loseHeading = font.render("You Won!",True,"#FFFFFF")
        loseHeadingRect = title.get_rect(center = convertCellCoordtoAbsCoord((WIDTH/2,HEIGHT/2-2)))
        scoreText = font.render(f"Score: {score}",True,"#FFFFFF")
        scoreTextRect = text.get_rect(center = convertCellCoordtoAbsCoord((WIDTH/2,HEIGHT/2)))
        continueText = font.render("Press any key to continue",True,"#FFFFFF")
        continueTextRect = text.get_rect(center = convertCellCoordtoAbsCoord((WIDTH/2,HEIGHT/2+2)))
        screen.blit(loseHeading,loseHeadingRect)
        screen.blit(scoreText,scoreTextRect)  
        screen.blit(continueText,continueTextRect)  

    ##------updates---------
    pygame.display.update()
    clock.tick(10)