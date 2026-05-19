from ursina import *
from new_player import *
from math import *
from level_maker import *


class Projectile(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = "sphere"
        self.collider = "sphere"
        self.scale = 1
        self.color = color.pink

        self.p = scene
        self.speed = 10
        self.dir_vec = Vec3(0, 0, 0)

        self.rotation = Vec3(0, 0, 0)

        self.traverse_target = scene

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        #print("spawned projectile")
        self.position += self.dir_vec * self.speed * time.dt

        

    def destroy_self(self, world_pos):
        destroy(self)


class Rocket(Projectile):
    def __init__(self, **kwargs):  # accept kwargs
        super().__init__( **kwargs)

        self.model = "cube"
        self.collider = "box"
        self.scale_y = 1
        self.scale_x = 2

        for key, value in kwargs.items():
            setattr(self, key, value)

    def destroy_self(self, world_pos):
        self.megumin_sphere = EXPLOSION(position=world_pos)
        destroy(self)

class EXPLOSION(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = "sphere"
        self.collider="sphere"
        self.position=(0,0,0)
        self.scale=Vec3(5, 5, 0)
        self.color=color.yellow
        self.alpha=0.4

        for key, value in kwargs.items():
            setattr(self, key, value)

    def explode(self):
        invoke(destroy(self), delay=4)