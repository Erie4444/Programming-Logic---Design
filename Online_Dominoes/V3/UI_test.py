from Dominoes_UI import *
pygame.init()
screen = pygame.display.set_mode((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0], SCREEN_DIMENSIONS[1] * TILE_DIMENSIONS[1]+DASHBOARD_DIMENSIONS))
pygame.display.set_caption("Dominoes")
clock = pygame.time.Clock()
game = True
running = True
board = pygame.sprite.GroupSingle(UIBoard())
dashboard = pygame.sprite.GroupSingle(UIDashboard())
selectedDomino = pygame.sprite.GroupSingle()

while running:
    screen.fill('#000000')
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                dashboard.sprite.dominoes.add(UIDomino(Domino(1,2)))
            if event.key == pygame.K_2:
                dashboard.sprite.dominoes.add(UIDomino(Domino(2,3)))
            if event.key == pygame.K_3:
                dashboard.sprite.dominoes.add(UIDomino(Domino(3,4)))
            if event.key == pygame.K_4:
                dashboard.sprite.dominoes.add(UIDomino(Domino(4,5)))
            if event.key == pygame.K_5:
                dashboard.sprite.dominoes.add(UIDomino(Domino(5,6)))
        if event.type == pygame.MOUSEBUTTONDOWN:
            if selectedDomino.sprite:
                if dashboard.sprite.isHovering(pygame.mouse.get_pos()):
                    dashboard.sprite.dominoes.add(selectedDomino.sprite)
                    selectedDomino.empty()
                else:
                    ##place code
                    selectedDomino.empty()
            else:
                selectedDomino.add(dashboard.sprite.getHovering(event.pos))
                print(selectedDomino)
                if selectedDomino:
                    dashboard.sprite.removeDomino(selectedDomino.sprite)

        if event.type == pygame.MOUSEMOTION:
            if selectedDomino.sprite:
                selectedDomino.sprite.setAbsPos(pygame.mouse.get_pos())
    if game:
        board.update([[]],(0,0))
        dashboard.update()
        board.draw(screen)
        dashboard.draw(screen)
        selectedDomino.draw(screen)
        # print(dashboard.sprite.dominoes.sprites())
    
    pygame.display.update()
    clock.tick(60)