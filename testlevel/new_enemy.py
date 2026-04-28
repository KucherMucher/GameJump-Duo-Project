from ursina import *
from math import *

class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'cube'
        #self.origin_y = -.5
        self.scale_y = 1
        self.color = color.red
        self.collider = 'box'

        self.animator = Animator({'idle' : None, 'walk' : None, 'jump' : None})

        #self.walk_speed = 8
        #self.velocity = 0 # the walk direction is stored here. -1 for left and 1 for right.
        #self.gravity = 1
        #self.grounded = True
        #self.air_time = 0   # this increase while we're falling and used when calculating the distance we fall so we fall faster and faster instead of linearly.
        

        self.velocity = Vec3(0,0,0) # for movement
        #self.acel = 15 # for gravity and flinging
        self.speed = 8

        self.gravity = 20
        #self.jump_force = 8
        self.grounded = False
        #self.land_y = self.y
        self.distconst = 0.6

        self.hitwall = False
        self.onslope = False

        self.e_start = 6
        self.e_range = 1
        self.idle = 1
        self.moving = True
        self.break_cycle = False
        self.angry_speed = int(self.walk_speed*1.5)

        self.vision_radius = 5
        self.fov = 60

        self.traverse_target = scene     
        self.ignore_list = [self] 
        self.init_ignore = self.ignore_list

        self.flinged = False
        # self.fling_direction = ?
        self.__fling_dir = Vec3(1, 1, 0)
        self.__fling_force = Vec3(1, 1, 0)
        self.__enemy_dir = Vec3(1, 1, 0)

        self.initialized = False

        # automatically set attributes.
        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        if self.initialized:
            dt = time.dt
        
            bxc = boxcast(self.position+Vec3(self.input_dir.x*dt*self.speed, 0, 0),
                        direction=Vec3(0,0,0),
                        distance=abs(self.scale_x),
                        ignore=self.ignore_list,
                        thickness=(abs(self.scale_x-self.speed*dt), self.scale_y*.9),
                        debug=True)

            

            # gravity (maybe this will be moved )
            self.velocity.y -= self.gravity * time.dt

            # movement
            self.position += self.velocity * dt

