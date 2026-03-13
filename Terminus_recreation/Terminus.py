import pygame as pg
from sys import exit
from config import *
from Player import Player
from Enemies import *
from Elements import *
from Waves import waveLoader

pg.init()
run = True

screen = pg.display.set_mode((SCREENWIDTH,SCREENHEIGHT))
pg.display.set_caption("Terminus")
clock = pg.time.Clock()
loader = waveLoader()
elementLibrary.addElement(Element("Player",Player(PLAYERSTARTX,PLAYERSTARTY),True))

while run:
    screen.fill(SCREENCOLOR)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            pg.quit()
            exit()

    keys = pg.key.get_pressed()
    if elementLibrary.get("Player"):
        elementLibrary.get("Player").sprite.move(keys)

    if keys[pg.K_SPACE]:
        elementLibrary.get("Player").sprite.shoot()

    ##---updates---
    if elementLibrary.get("Player Bullet"):
        elementLibrary.get("Player Bullet").update()
    if elementLibrary.get("Enemy Bullet"):
        elementLibrary.get("Enemy Bullet").update()
    if elementLibrary.get("Enemy"):
        elementLibrary.get("Enemy").update()
    if elementLibrary.get("Player"):
        elementLibrary.get("Player").update()
    if elementLibrary.get("Enemy Shield"):
        elementLibrary.get("Enemy Shield").update()
    loader.update()
    ##---drawing---
    if elementLibrary.get("Player Bullet"):
        elementLibrary.get("Player Bullet").draw(screen)
    if elementLibrary.get("Enemy Bullet"):
        elementLibrary.get("Enemy Bullet").draw(screen)
    if elementLibrary.get("Player"):
        elementLibrary.get("Player").draw(screen)
    if elementLibrary.get("Enemy"):
        elementLibrary.get("Enemy").draw(screen)
    if elementLibrary.get("Enemy Shield"):
        elementLibrary.get("Enemy Shield").draw(screen)

    clock.tick(60)
    pg.display.update()