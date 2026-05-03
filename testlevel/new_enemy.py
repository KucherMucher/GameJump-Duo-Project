from ursina import *
from math import *
from ursina.models.procedural.cone import Cone 
from panda3d.core import BitMask32


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
        

        self.velocity = Vec3(1,0,0) # for movement
        #self.acel = 15 # for gravity and flinging
        self.speed = 4

        self.gravity = 20
        #self.jump_force = 8
        self.grounded = False
        #self.land_y = self.y
        self.distconst = 0.6

        self.hitwall = False
        self.onslope = False

        self.e_start = 4
        self.e_range = 4
        self.idle = 1
        self.moving = True
        self.break_cycle = False
        self.angry_speed = int(self.speed*1.5)

        self.vision_radius = 5
        self.fov = 60
        self.cone_offset = Vec3(self.scale_x*self.vision_radius/2, 0, 0)

        self.traverse_target = scene     
        self.ignore_list = [self] 
        self.init_ignore = self.ignore_list
        self.special_ignore = []

        self.parabam = 1
        self.turn_invoker = None

        self.flinged = False
        # self.fling_direction = ?
        self.__fling_dir = Vec3(1, 1, 0)
        self.__fling_force = Vec3(1, 1, 0)
        self.__enemy_dir = Vec3(1, 1, 0)

        self.initialized = False

        # automatically set attributes.
        for key, value in kwargs.items():
            setattr(self, key, value)

        """self.collision_sphere = Entity(model="sphere",
                                      position=self.position+self.cone_offset,
                                      color=color.white,
                                      alpha=0.2,
                                      scale=Vec3(self.vision_radius*2, self.vision_radius*2, 3),
                                      collider="sphere")"""
        
        self.cone_fov = Entity(model=Cone(2),
                               collider="mesh",
                                position=Vec3(self.position.x, 0, 0),
                                color=color.red,
                                alpha=0.4,
                                scale=Vec3(sin(self.fov)*self.vision_radius*2, self.vision_radius, 3),
                                rotation_z=270,
                                debug=True#,
                                #parent=self,
                                )
        
        for v in self.cone_fov.model.vertices:
            Entity(
                model='sphere',
                scale=0.05,
                color=color.yellow,
                position=self.cone_fov.position + v  # offset by entity position
            )
        
        
        
        self.ignore_list.extend([self.cone_fov])
        

    def initialize(self):
        #print("\n\n\n"+str(self.ignore_list)+"\n\n\n")
        self.initialized = True
        

    def update(self):
        if self.initialized:
            from level_maker import Wall

            dt = time.dt

            # apply gravity
            if not self.grounded:
                self.velocity.y -= self.gravity * dt

            # move
            self.position += self.velocity * dt
            self.cone_fov.position = self.position + self.cone_offset

            # check collisions
            inter = self.intersects(scene, ignore=self.ignore_list)
            hit = inter.entity

            if isinstance(hit, Wall):
                normal = inter.normal

                # floor / ceiling
                if abs(normal.y) > 0.5:
                    self.position.y = inter.world_point.y + (0.5 if normal.y > 0 else -0.5)
                    self.velocity.y = 0
                    self.grounded = normal.y > 0  # grounded only if hitting from above

                # wall (left / right)
                if abs(normal.x) > 0.5:
                    self.velocity.x = 0
                    self.position.x = inter.world_point.x + (self.scale_x * 0.5 * normal.x)
                    
                    self.moving_cycle_blocked()
                    return
            else:
                self.grounded = False

            self.moving_cycle()
 
        else:
            self.initialize()

        
    def moving_cycle_blocked(self):
        if self.break_cycle:
            self.parabam *= -1  # bounce off wall in angry mode
            self.velocity.x = self.angry_speed * self.parabam
        else:
            self.moving = False
            self.parabam *= -1
            invoke(self.__turn, delay=self.idle)
            """if hasattr(self, 'turn_invoker') and self.turn_invoker:
                self.turn_invoker.pause()
            self.turn_invoker = invoke(self.__turn, delay=self.idle)"""
    
    def moving_cycle(self):
        right_bound = self.e_start+(self.e_range/2)
        left_bound = self.e_start-(self.e_range/2)

        if not self.break_cycle:
            if self.moving and self.initialized and self.e_range!=0:
                if self.x > right_bound:
                    self.x = right_bound
                    self.moving = False
                    invoke(self.__turn, -1 ,delay=self.idle)
                elif self.x < left_bound:
                    self.x = left_bound 
                    self.moving = False
                    invoke(self.__turn, 1 ,delay=self.idle)
                self.velocity.x = self.parabam * self.speed
            """elif not self.moving:
                self.velocity.x = 0"""
        else:
            self.velocity.x = self.angry_speed * self.parabam

    """def moving_cycle(self):
        if self.break_cycle:
            self.velocity.x = self.angry_speed * self.parabam
            
        
        if not self.moving and not self.initialized and self.e_range==0:
            self.velocity.x = 0
            
        
        right_bound = self.e_start+(self.e_range/2)
        left_bound = self.e_start-(self.e_range/2)

        if self.x > right_bound:
            self.x = right_bound
            self.__change_dir(-1)

        elif self.x > left_bound:
            self.x = left_bound
            self.__change_dir(1)

        self.velocity.x = self.speed * self.parabam"""

    def __change_dir(self, d):
        self.moving = False 
        self.parabam = d
        invoke(self.__turn, delay=self.idle)
        

    def __turn(self, dir=0):
        self.cone_fov.rotation_y += 180
        #self.cone_offset.x *= -1~
        self.cone_offset.x = -self.cone_offset.x
        self.parabam = dir
        self.moving = True

    def set_special_ignore(self, ignore):
        self.special_ignore.append(ignore)
        


if __name__ == '__main__':
    # window.vsync = False
    app = Ursina()
    camera.orthographic = True
    camera.fov = 10
    from level_maker import Wall
    ground = Wall(model='cube', color=color.white33, origin_y=.5, scale=(20, 1, 1), collider='box', y=-1)
    wall = Wall(model='cube', color=color.azure, origin=(-.5,.5), scale=(5,10), x=10, y=.5, collider='box')
    wall_2 = Wall(model='cube', color=color.white33, origin=(-.5,.5), scale=(5,10), x=10, y=0, collider='box')
    ceiling = Wall(model='cube', color=color.white33, origin_y=-.5, scale=(1, 1, 1), y=1, collider='box')
    ceiling = Wall(model='cube', color=color.white33, origin_y=-.5, scale=(5, 5, 1), y=2, collider='box')
    ground = Wall(model='cube', color=color.white33, origin_y=.5, scale=(20, 3, 1), collider='box', y=-1, rotation_z=45, x=-5)

    def input(key):
        if key == 'c':
            wall.collision = not wall.collision
            print(wall.collision)


    player_controller = Enemy(scale_x=1, x=4, y=2)
    ec = EditorCamera()
    ec.add_script(SmoothFollow(target=player_controller, offset=[0,1,0], speed=4))

    app.run()



"""
Ideias: 
    . sphere + triangle/pyramid for player detection
"""