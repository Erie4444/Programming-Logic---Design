import pygame as pg
from config import *
from MoveableObjects import moveableObjectPos
from Elements import *
class PlayerBullet (moveableObjectPos):
    def __init__(self,x,y):
        super().__init__(x,y,-90,PLAYERBULLETWIDTH,PLAYERBULLETHEIGHT,PLAYERBULLETVEL)
        self.image.fill(PLAYERBULLETCOLOR)
    
    def update(self):
        super().movePos()
        super().update()

class EnemyBullet (moveableObjectPos):
    def __init__(self,x,y,angle):
        super().__init__(x,y,angle,BASICENEMYBULLETWIDTH,BASICENEMYBULLETHEIGHT,BASICENEMYBULLETVEL)
        self.image.fill(BASICENEMYBULLETCOLOR)
    
    def update(self):
        super().movePos()
        super().update()