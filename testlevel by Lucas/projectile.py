from ursina import *
from new_player import *
from math import *

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

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.position += self.dir_vec * self.speed * time.dt

        if self.intersects(scene) and not self.intersects(self.p):
            destroy(self)