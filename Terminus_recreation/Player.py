import pygame as pg
from config import *
from MoveableObjects import moveableObjectVel
from Projectiles import PlayerBullet
from Elements import *
import sys

class Player (moveableObjectVel):
    def __init__(self,x,y):
        super().__init__(x,y,0,PLAYERWIDTH,PLAYERHEIGHT,PLAYERMAXVEL,PLAYERVELINCREMENT)
        self.image.fill(PLAYERCOLOR)
        self.bulletCount = 0
        self.bulletCooldown = PLAYERBULLETCOOLDOWN
    
    def move(self,keys):
        if keys[PLAYERLEFTINPUT] and self.x > PLAYERXMIN:
            self.angle = 180
            super().moveVel()
        if keys[PLAYERRIGHTINPUT] and self.x < PLAYERXMAX:
            self.angle = 0
            super().moveVel()
        if not keys[PLAYERLEFTINPUT] and not keys[PLAYERRIGHTINPUT]:
            super().moveDrag()
        
    def shoot(self):
        if self.bulletCooldown <= 0:
            if self.bulletCount%2 == 0:
                elementLibrary.addElement(Element(
                    "Player Bullet",
                    PlayerBullet(elementLibrary.get("Player").sprite.x-PLAYERBULLETXOFFSET,elementLibrary.get("Player").sprite.y),
                    False
                    ))
            else:
                elementLibrary.addElement(Element(
                    "Player Bullet",
                    PlayerBullet(elementLibrary.get("Player").sprite.x+PLAYERBULLETXOFFSET,elementLibrary.get("Player").sprite.y),
                    False
                    ))
            self.bulletCount+=1
            self.bulletCooldown = PLAYERBULLETCOOLDOWN

    def printVel(self):
        print(f"xVel: {self.velocityX}, yVel: {self.velocityY}")

    def update(self):
        super().update()
        if self.bulletCooldown > 0: self.bulletCooldown -= 1
        
        if elementLibrary.get("Enemy Bullet"):
            if pg.sprite.spritecollide(self,elementLibrary.get("Enemy Bullet"),True):
                print("died")