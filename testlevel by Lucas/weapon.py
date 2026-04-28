from ursina import *
from new_player import *
import json

class Weapon(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'cube'
        self.scale_x = 1
        self.scale_y = 0.5
        self.color = color.gray

        self.parent = Entity() #always put parent as player from level_maker
        self.offset = Vec3(0, 0)
        self.position = Vec3(self.parent.scale_x+self.offset.x, 0, 0)
        self.weapon = "bazooka"
        


        for key, value in kwargs.items():
            setattr(self,key,value)

    def update(self):
        pass

    def get_weapon(self):
        with open("testlevel/weapons.json", "r") as table:
            elements = json.load(table)
        print("\n\n\n\n\n\n\n\n\n\n\n"+str(elements[self.weapon]))
        weapon = elements[self.weapon]
        self.scale_x = weapon["scale_x"]
        self.scale_y = weapon["scale_y"]
        self.offset = Vec3(weapon["offset_x"], weapon["offset_y"], weapon["offset_z"])
        #self.model = weapon["model"]
        
            
        
