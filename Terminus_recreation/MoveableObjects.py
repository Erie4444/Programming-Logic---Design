import pygame as pg
import math
from config import *
##0 deg == right
class moveableObjectPos(pg.sprite.Sprite):
    ##constant velocity
    def __init__(self,x,y,angle,width,height,velocity,borderCollide = True):
        super().__init__()
        self.image = pg.Surface((width,height))
        self.rect = self.image.get_rect(center = (x,y))
        self.x = x
        self.y = y
        self.angle = angle
        self.velocity = velocity
        self.borderCollide = borderCollide
    
    ##moves via modifying position
    def movePos (self):
        self.x+=round(self.velocity*math.cos(math.radians(self.angle)),4)
        self.y+=round(self.velocity*math.sin(math.radians(self.angle)),4)
    
    def update(self):
        if (SCREENHEIGHT < self.y or 0 > self.y or SCREENWIDTH < self.x or 0 > self.x) and self.borderCollide:
            self.kill()
        self.rect.center = (self.x,self.y)

class moveableObjectVel(pg.sprite.Sprite):
    ##varied velocity
    def __init__(self,x,y,angle,width,height,maxVel,incVel,borderCollide = True):
        super().__init__()
        self.image = pg.Surface((width,height))
        self.rect = self.image.get_rect(center = (x,y))
        self.x = x
        self.y = y
        self.velocityX = 0
        self.velocityY = 0
        self.velocityIncrement = incVel
        self.velocityMax = maxVel
        self.angle = angle
        self.borderCollide = borderCollide
        
    ##moves via modifying velocity
    def moveVel(self):
        ##checking if the velocity vector mag is less than the max
        if math.sqrt(self.velocityX**2 + self.velocityY**2) < self.velocityMax:
            ##components of the velocity vector
            self.velocityX+=round(self.velocityIncrement*math.cos(math.radians(self.angle)),4)
            self.velocityY+=round(self.velocityIncrement*math.sin(math.radians(self.angle)),4)
        else:
            ##setting the compoents to only result in a vector with mag around the max
            self.velocityX = round(self.velocityMax*math.cos(math.radians(self.angle)),4)
            self.velocityY = round(self.velocityMax*math.sin(math.radians(self.angle)),4)
        ##updating x&y positions based on the velocity vector components
        self.x+=self.velocityX
        self.y+=self.velocityY
    
    ##uses the vel increment to deccelerate the object to vel 0
    def moveDrag(self):
        if math.sqrt(self.velocityX**2 + self.velocityY**2) > self.velocityIncrement:
            ##components of the velocity vector
            self.velocityX-=round(self.velocityIncrement*math.cos(math.radians(self.angle)),4)
            self.velocityY-=round(self.velocityIncrement*math.sin(math.radians(self.angle)),4)
        else:
            ##setting the compoents to only result in a vector with mag 0
            self.velocityX = 0
            self.velocityY = 0
        ##updating x&y positions based on the velocity vector components
        self.x+=self.velocityX
        self.y+=self.velocityY
    
    def update(self):
        if (SCREENHEIGHT < self.y or 0 > self.y or SCREENWIDTH < self.x or 0 > self.x) and self.borderCollide:
            self.kill()
        self.rect.center = (self.x,self.y)
