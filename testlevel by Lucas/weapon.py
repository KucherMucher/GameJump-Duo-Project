from ursina import *
from new_player import *
import json
from math import *
from projectile import *

class Weapon(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'cube'
        self.scale_x = 1
        self.scale_y = 0.5
        self.color = color.gray

        self.parent = Entity() #always put parent as player from level_maker
        self.offset = Vec3(0.1, 0, 0)
        self.position = Vec3(self.parent.scale_x+self.offset.x, self.offset.y, 0)
        self.weapon = "bazooka"

        for key, value in kwargs.items():
            setattr(self ,key, value)

    def get_weapon(self):
        with open("testlevel/weapons.json", "r") as table:
            elements = json.load(table)
        weapon = elements[self.weapon]
        self.scale_x = weapon["scale_x"]
        self.scale_y = weapon["scale_y"]
        self.offset = Vec3(weapon["offset_x"], weapon["offset_y"], weapon["offset_z"])
        #self.model = weapon["model"]



class Bazooka(Weapon):
    def __init__(self, **kwargs):  # accept kwargs
        super().__init__( **kwargs)

        self.mouse_dir = Vec3(0, 0, 0)

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        player_screen_pos = self.parent.screen_position
    
        normalized_player = Vec2(
            player_screen_pos.x / 2,
            player_screen_pos.y / 2
        )
        
        mouse_offset = Vec2(
            mouse.position.x - normalized_player.x,
            mouse.position.y - normalized_player.y
        )

        if self.parent.rotation_y == 45:
            vec_angle = atan2(mouse_offset.y, mouse_offset.x)
            self.mouse_dir = Vec3(cos(vec_angle), sin(vec_angle), 0)
            self.position = Vec3(self.mouse_dir.x, self.mouse_dir.y, 0)
        else:
            vec_angle = atan2(mouse_offset.y, -mouse_offset.x)
            self.mouse_dir = Vec3(-cos(vec_angle), sin(vec_angle), 0)
            self.position = Vec3(-self.mouse_dir.x, self.mouse_dir.y, 0)
        raycast(
            self.world_position,
            direction=self.mouse_dir, #down
            distance=10,  
            ignore=[self],
            debug=True,
        )
        self.rotation = Vec3(0, 0, -degrees(vec_angle))

    def input(self, key):
        if key == 'left mouse down':
            p = Projectile(dir_vec=self.mouse_dir, position = self.world_position+Vec3(0.5*self.mouse_dir.x, self.mouse_dir.y*0.5, 0), p = self)

        
            
        
