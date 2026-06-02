from Dominoes_UI import *
pygame.init()
screen = pygame.display.set_mode((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0], SCREEN_DIMENSIONS[1] * TILE_DIMENSIONS[1]))
pygame.display.set_caption("Dominoes")
clock = pygame.time.Clock()
game = None
selectedDomino = None
running = True
board = UIBoard()

while running:
    screen.fill('#000000')
    if game:
        board.draw(screen)
    
    pygame.display.update()
    clock.tick(60)