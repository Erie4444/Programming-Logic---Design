import pygame as pg
from config import *
from MoveableObjects import *
from Projectiles import EnemyBullet
from Elements import *
import random
import math

'''
NEW ENEMY

PARAMETERS - x, y both ints
CONSTANTS - width, height, maxVel, velInc, color, shootCooldown, health
MANDATORY METHODS

__init__() -> needs internalCooldown & self.name

update() -> super already handles cooldowns, health, collisions, shooting, and death
    add any extra updates

shoot() -> empty in super
    handles what happens when the enemy shoots

die() -> super just has self.kill()
    add any effects on death

collision() -> empty in super
    handles collisions in the elementsLibrary
'''
class ENEMYBASE(moveableObjectVel):
    def __init__(self,x,y,angle,width,height,maxVel,velInc,color,health,borderCollide = True):
        super().__init__(x,y,angle,width,height,maxVel,velInc,borderCollide)
        self.image.fill(color)
        self.health = health
        self.width = width
        self.height = height
    
    def update(self):
        super().update()
        self.collision()
        if self.health <= 0:
            self.die()

    def die(self):
        self.kill()
    
    def collision(self):
        pass

class BasicEnemy(ENEMYBASE):
    def __init__(self,x,y):
        super().__init__(x,y,0,BASICENEMYWIDTH,
                         BASICENEMYHEIGHT,
                         BASICENEMYMAXVEL,
                         BASICENEMYVELINCREMENT,
                         BASICENEMYCOLOR,
                         BASICENEMYHEALTH)
        self.internalCooldown = random.randint(BASICENEMYBULLETCOOLDOWNMIN,BASICENEMYBULLETCOOLDOWNMAX)
        self.name = "Basic"
    
    def shoot(self):
        playerx = elementLibrary.get("Player").sprite.x + random.randint(-BASICENEMYAIMVARIATIONX,BASICENEMYAIMVARIATIONX)
        playery = elementLibrary.get("Player").sprite.y + random.randint(-BASICENEMYAIMVARIATIONY,BASICENEMYAIMVARIATIONY)
        angle = -math.degrees(math.atan2(self.y-playery,playerx-self.x))
        elementLibrary.addElement(Element(
            "Enemy Bullet",
            EnemyBullet(self.x,self.y,angle),False)
            )
    
    def collision(self):
        if elementLibrary.get("Player Bullet"):
            if pg.sprite.spritecollide(self,elementLibrary.get("Player Bullet"),True):
                self.health -= PLAYERDAMAGE
    
    def die(self):
        super().die()

    def update(self):
        super().update()
        if self.internalCooldown <= 0:
            self.shoot()
            self.internalCooldown = random.randint(BASICENEMYBULLETCOOLDOWNMIN,BASICENEMYBULLETCOOLDOWNMAX)
        self.internalCooldown -= 1

class TripleEnemy(ENEMYBASE):
    def __init__(self,x,y):
        super().__init__(x,y,0,TRIPLEENEMYWIDTH,
                         TRIPLEENEMYHEIGHT,
                         TRIPLEENEMYMAXVEL,
                         TRIPLEENEMYVELINCREMENT,
                         TRIPLEENEMYCOLOR,
                         TRIPLEENEMYHEALTH)
        self.name = "Triple"
        self.shootState = "triple"
        self.internalCooldown = random.randint(TRIPLEENEMYBULLETCOOLDOWNMIN,TRIPLEENEMYBULLETCOOLDOWNMAX)
    
    def shootTriple(self):
        elementLibrary.addElement(Element(
            "Enemy Bullet",
            EnemyBullet(self.x,self.y,90),False)
            )
        elementLibrary.addElement(Element(
            "Enemy Bullet",
            EnemyBullet(self.x,self.y,45),False)
            )
        elementLibrary.addElement(Element(
            "Enemy Bullet",
            EnemyBullet(self.x,self.y,135),False)
            )
        self.shootState = "single"
    
    def shootSingle(self):
        playerx = elementLibrary.get("Player").sprite.x + random.randint(-BASICENEMYAIMVARIATIONX,BASICENEMYAIMVARIATIONX)
        playery = elementLibrary.get("Player").sprite.y + random.randint(-BASICENEMYAIMVARIATIONY,BASICENEMYAIMVARIATIONY)
        angle = -math.degrees(math.atan2(self.y-playery,playerx-self.x))
        elementLibrary.addElement(Element(
            "Enemy Bullet",
            EnemyBullet(self.x,self.y,angle),False)
            )
        self.shootState = "triple"


    def collision(self):
        if elementLibrary.get("Player Bullet"):
            if pg.sprite.spritecollide(self,elementLibrary.get("Player Bullet"),True):
                self.health -= PLAYERDAMAGE
    
    def die(self):
        super().die()

    def update(self):
        super().update()
        if self.internalCooldown <= 0:
            if self.shootState == "triple":
                self.shootTriple()
                self.internalCooldown = TRIPLEENEMYSHOTTIMEOFFSET
            elif self.shootState == "single":
                self.shootSingle()
                self.internalCooldown = random.randint(TRIPLEENEMYBULLETCOOLDOWNMIN,TRIPLEENEMYBULLETCOOLDOWNMAX)
        self.internalCooldown -= 1

class UfoEnemy(ENEMYBASE):
    def __init__(self,side,y):
        if side == "left":
            x = -UFOENEMYWIDTH/2
            angle = 0
        elif side == "right":
            x = SCREENWIDTH+UFOENEMYWIDTH/2
            angle = 180
        super().__init__(x,y,angle,UFOENEMYWIDTH,
                         UFOENEMYHEIGHT,
                         UFOENEMYMAXVEL,
                         UFOENEMYVELINCREMENT,
                         UFOENEMYCOLOR,
                         UFOENEMYHEALTH,
                         False)
        self.internalCooldown = random.randint(UFOENEMYBULLETCOOLDOWNMIN,UFOENEMYBULLETCOOLDOWNMAX)
        self.name = "UFO"
    
    def shoot(self):
        elementLibrary.addElement(Element(
            "Enemy Bullet",
            EnemyBullet(self.x,self.y,55),False)
            )
        elementLibrary.addElement(Element(
            "Enemy Bullet",
            EnemyBullet(self.x,self.y,125),False)
            )
    
    def collision(self):
        if elementLibrary.get("Player Bullet"):
            if pg.sprite.spritecollide(self,elementLibrary.get("Player Bullet"),True):
                self.health -= PLAYERDAMAGE
    
    def die(self):
        super().die()

    def update(self):
        super().update()
        if self.internalCooldown <= 0:
            self.shoot()
            self.internalCooldown = random.randint(UFOENEMYBULLETCOOLDOWNMIN,UFOENEMYBULLETCOOLDOWNMAX)
        self.internalCooldown -= 1
        self.moveVel()

class ShieldEnemy(ENEMYBASE):
    def __init__(self,x,y):
        super().__init__(x,y,0,SHEILDENEMYWIDTH,
                         SHEILDENEMYHEIGHT,
                         SHEILDENEMYMAXVEL,
                         SHEILDENEMYVELINCREMENT,
                         SHEILDENEMYCOLOR,
                         SHEILDENEMYHEALTH)
        self.name = "Shield"
        self.buildShield()

    def buildShield(self):
        self.shield = Shield(self.x,self.y+SHEILDENEMYHEIGHT/2+SHEILDENEMYSHEILDHEIGHT/2,SHEILDENEMYSHEILDWIDTH,SHEILDENEMYSHEILDHEIGHT,SHEILDENEMYSHEILDHEALTH)
        elementLibrary.addElement(Element("Enemy Shield",self.shield,False))
        
    def collision(self):
        if elementLibrary.get("Player Bullet"):
            if pg.sprite.spritecollide(self,elementLibrary.get("Player Bullet"),True):
                self.health -= PLAYERDAMAGE
    
    def die(self):
        self.shield.die()
        super().die()

    def update(self):
        super().update()

class Shield(moveableObjectPos):
    def __init__(self,x,y,shieldWidth,shieldHeight,health):
        super().__init__(x,y,0,shieldWidth,shieldHeight,0)
        self.image.fill(SHIELDCOLOR)
        self.maxHealth = health
        self.health = health
        self.regenTimer = SHIELDREGENTIMER

    def collision(self):
        if elementLibrary.get("Player Bullet"):
            if self.health>0:
                if pg.sprite.spritecollide(self,elementLibrary.get("Player Bullet"),True):
                    self.health -= PLAYERDAMAGE
    
    def die(self):
        self.kill()

    def update(self):
        super().update()
        self.collision()
        if self.health <=0:
            self.image.fill(SHIELDDOWNCOLOR)
            self.regenTimer-=1
        if self.regenTimer <=0:
            self.image.fill(SHIELDCOLOR)
            self.health = self.maxHealth
            self.regenTimer = SHIELDREGENTIMER

##used for testing
class EnemySpawner(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((0,0))
        self.rect = self.image.get_rect(center = (0,0))
        self.cooldown = ENEMYSPAWNERCOOLDOWN

    def spawnEnemy(self):
        elementLibrary.addElement(Element(
            "Enemy",
            BasicEnemy(random.randint(round(ENEMYSPAWNXMIN),round(ENEMYSPAWNXMAX)),
                  random.randint(round(ENEMYSPAWNYMIN),round(ENEMYSPAWNYMAX))),
                  False))
        self.cooldown = ENEMYSPAWNERCOOLDOWN

    def update(self):
        if self.cooldown <= 0:
            self.spawnEnemy()
        self.cooldown -=1