from ursina import *
from new_player import *

class Weapon(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'cube'
        self.scale_x = 0.5
        self.scale_y = 0.1
        self.color = color.gray

        self.parent = Entity() #always put parent as player from level_maker
        self.position = Vec3(self.parent.scale_x, 0, 0)


        for key, value in kwargs.items():
            setattr(self,key,value)

class Bazooka(Weapon):
    def __init__(self, **kwargs):
        super().__init__()

        for key, value in kwargs.items():
            setattr(self,key,value)
