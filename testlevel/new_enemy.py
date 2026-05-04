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
            dt = time.dt
            self.position += self.velocity * dt
            """self.collision_sphere.position = self.position"""
            #self.cone_fov.position = self.cone_offset
            self.cone_fov.position = self.position+self.cone_offset

            from level_maker import Wall
            inter = self.intersects(scene, ignore=self.ignore_list)
            if isinstance(inter.entity, Wall):
                self.grounded = True
            else:
                self.grounded = False
        
            """bxc = boxcast(self.position,
                        direction=Vec3(0,0,0),
                        distance=abs(self.scale_x),
                        ignore=self.ignore_list,
                        thickness=(self.scale_x, self.scale_y),
                        debug=True)"""
            
            normal = inter.normal
            
            """if normal is None:
                normal = Vec3(0,0,0)
            if normal.x == 0 : 
                
            else:
                print(normal)
                self.x -= self.velocity.x * time.dt"""
            
            self.moving_cycle()
                

            
            if isinstance(inter.entity, Wall):
                normal = inter.normal
                if self.grounded:
                    self.velocity.y = 0
                    inter_y = inter.world_point.y
                    if self.position.y < inter_y + self.scale_y/2:
                        self.position.y += (self.position.y-inter_y+self.scale_y/2)

                if normal.x != 0:
                    self.x += -self.velocity.x * time.dt

                

            if not self.grounded:
                self.velocity.y -= self.gravity * time.dt

            
        else:
            self.initialize()

    def set_special_ignore(self, ignore):
        self.special_ignore.append(ignore)
        

    
    def moving_cycle(self):
        right_bound = self.e_start+(self.e_range/2)
        left_bound = self.e_start-(self.e_range/2)

        if not self.break_cycle:
            if self.moving and self.initialized and self.e_range!=0:
                if self.x > right_bound:
                    self.moving = False
                    self.__turn()
                    self.x = right_bound
                    self.parabam = -1
                    
                if self.x < left_bound:
                    self.moving = False
                    self.__turn()
                    self.x = left_bound 
                    self.parabam = 1
                
                    
                self.velocity.x = self.parabam * self.speed
            elif not self.moving:
                self.velocity.x = 0
        else:
            """if self.turn_invoker:
                self.turn_invoker.pause()"""
            self.velocity.x = self.angry_speed * self.parabam

    

    def __turn(self):
        self.moving = True
        self.cone_fov.rotation_y += 180
        #self.cone_offset.x *= -1~
        self.cone_offset.x = -self.cone_offset.x


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


    player_controller = Enemy(scale_x=1, x=3, y=2)
    ec = EditorCamera()
    ec.add_script(SmoothFollow(target=player_controller, offset=[0,1,0], speed=4))

    app.run()



"""
Ideias: 
    . sphere + triangle/pyramid for player detection
"""