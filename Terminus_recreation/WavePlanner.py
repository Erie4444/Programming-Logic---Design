import pygame as pg
from sys import exit
from config import *
from Player import Player
from Enemies import *
from Elements import *
from Waves import waveLoader

pg.init()
run = True

screen = pg.display.set_mode((PLANNINGWIDTH,PLANNINGHEIGHT))
pg.display.set_caption("Terminus Wave Planner")
clock = pg.time.Clock()
loader = waveLoader()
currentEnemy = pg.sprite.GroupSingle(BasicEnemy(PLANNINGWIDTH/2,PLANNINGHEIGHT/2))
elementLibrary.addElement(Element("Enemy",BasicEnemy(0,0),False))
elementLibrary.get("Enemy").empty()
while run:
    screen.fill(SCREENCOLOR)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            output = {}
            for enemy in elementLibrary.get("Enemy").sprites():
                if not enemy.name in output.keys():
                    output[enemy.name] = [enemy.rect.center]
                else:
                    output[enemy.name].append(enemy.rect.center)
            print(output)
            run = False
            pg.quit()
            exit()
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_n:
                loader.clearWave()
                loader.next()
                print(f"Current wave: {loader.wave}")
            if event.key == pg.K_p:
                loader.clearWave()
                loader.previous()
                print(f"Current wave: {loader.wave}")
            if event.key == pg.K_SPACE:
                if not pg.sprite.spritecollide(currentEnemy.sprite,elementLibrary.get("Enemy"),False):
                    x = currentEnemy.sprite.rect.centerx
                    y = currentEnemy.sprite.rect.centery
                    currentEnemy.sprite.image.fill(TRIPLEENEMYCOLOR)
                    elementLibrary.addElement(Element("Enemy", currentEnemy,False))
                    currentEnemy.empty()
                    currentEnemy.add(BasicEnemy(x,y))
                else:
                    print("Already Occupied!")
            if event.key == pg.K_LEFT:
                currentEnemy.sprite.rect.centerx-=MOVEINCREMENTS
                print(f"pos: {currentEnemy.sprite.rect.center}")
            if event.key == pg.K_RIGHT:
                currentEnemy.sprite.rect.centerx+=MOVEINCREMENTS
                print(f"pos: {currentEnemy.sprite.rect.center}")
            if event.key == pg.K_UP:
                currentEnemy.sprite.rect.centery-=MOVEINCREMENTS
                print(f"pos: {currentEnemy.sprite.rect.center}")
            if event.key == pg.K_DOWN:
                currentEnemy.sprite.rect.centery+=MOVEINCREMENTS
                print(f"pos: {currentEnemy.sprite.rect.center}")
            if event.key == pg.K_q:
                MOVEINCREMENTS/=10
                print(f"increment: {MOVEINCREMENTS}")
            if event.key == pg.K_e:
                MOVEINCREMENTS*=10
                print(f"increment: {MOVEINCREMENTS}")
            if event.key == pg.K_BACKSPACE:
                pg.sprite.spritecollide(currentEnemy.sprite,elementLibrary.get("Enemy"),True)
            if event.key == pg.K_i:
                currentEnemy.sprite.rect.centerx = int(input("x value: "))
                currentEnemy.sprite.rect.centery = int(input("y value: "))
            if event.key == pg.K_0:
                x = currentEnemy.sprite.rect.centerx
                y = currentEnemy.sprite.rect.centery
                currentEnemy.empty()
                currentEnemy.add(BasicEnemy(x,y))
            if event.key == pg.K_1:
                x = currentEnemy.sprite.rect.centerx
                y = currentEnemy.sprite.rect.centery
                currentEnemy.empty()
                currentEnemy.add(TripleEnemy(x,y))
            if event.key == pg.K_2:
                x = currentEnemy.sprite.rect.centerx
                y = currentEnemy.sprite.rect.centery
                currentEnemy.empty()
                currentEnemy.add(ShieldEnemy(x,y))

    ##---updates---
    ##---drawing---
    if elementLibrary.get("Enemy"):
        elementLibrary.get("Enemy").draw(screen)
    currentEnemy.sprite.image.fill("#0700C8")
    currentEnemy.draw(screen)

    clock.tick(60)
    pg.display.update()