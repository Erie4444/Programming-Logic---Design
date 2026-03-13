import pygame as pg
class Element:
    def __init__(self,name,object:pg.sprite.Sprite,single:bool):
        self.name = name
        self.single = single
        self.object = object
    
    def update(self):
        self.object.update()

    
class Elements:
    def __init__(self):
        self.singles = {}
        self.groups = {}
    
    def addElement(self,element:Element):
        if element.single:
            self.singles[element.name] = pg.sprite.GroupSingle(element.object)
        else:
            if element.name in self.groups.keys():
                self.groups[element.name].add(element.object)
            else:
                self.groups[element.name] = pg.sprite.Group(element.object)
    
    def removeElement(self,element:Element):
        if element.single:
            if element.name in self.singles.keys():
                del self.singles[element.name]
        else:
            if element.name in self.groups.keys():
                self.groups[element.name].remove(element.object)
    
    def get(self,name):
        if name in self.singles.keys():
            return self.singles[name]
        elif name in self.groups.keys():
            return self.groups[name]

    # def update(self):
    #     for element in self.singles.values():
    #         element.update()
    #     for element in self.groups.values():
    #         element.update()

elementLibrary = Elements()