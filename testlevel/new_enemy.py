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

        #self.e_start_pos.x = 4
        self.e_start_pos = Vec3(4,0,0)
        self.e_range = 4
        self.idle = 1
        self.moving = True
        self.angry_speed = int(self.speed*1.5)

        self.parabam = 1
        self.return_to_cycle = False
        self.return_invoke: invoke = None
        self.see_player = False
        self.break_cycle = False

        self.vision_radius = 5
        self.fov = 60
        self.cone_offset = Vec3(self.scale_x*self.vision_radius/2, 0, 0)

        self.traverse_target = scene     
        self.ignore_list = [self] 
        self.init_ignore = self.ignore_list
        self.special_ignore = []

        

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
            self.cone_fov.position = self.position+self.cone_offset*self.parabam
            angle = abs(self.cone_fov.rotation_z) * self.parabam
            self.cone_fov.rotation_z = angle
            #print(self.cone_fov.rotation_z)

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
            

            if not self.break_cycle and not self.return_to_cycle:
                if self.return_invoke != None: # just to be safe
                    self.return_invoke = None
                self.moving_cycle()
                #print("moving_cycle")
            elif self.return_to_cycle:
                if self.return_invoke == None:
                    self.return_invoke = invoke(self.finish_return_to_cycle, delay=1)
                #print("return_to_cycle")

            if self.see_player:
                self.break_cycle = True
                if self.return_invoke != None:
                    self.return_invoke.kill()
                self.velocity.x = self.angry_speed * self.parabam
                #print("see_player")
            elif not self.see_player and self.break_cycle:
                self.break_cycle = False
                self.return_to_cycle = True
                #print("not see_player and break_cycle")
                

            
            if isinstance(inter.entity, Wall): 
                normal = inter.normal
                if self.grounded and normal.y > 0.5:
                    self.velocity.y = 0
                    ground_y = inter.world_point.y + self.scale_y / 2 #fix
                    if self.world_position.y < ground_y:
                        self.world_position = Vec3(self.world_position.x, ground_y, 0)

                if abs(normal.x) > 0.5:
                    
                    wall_x = inter.world_point.x + (self.scale_x / 2) * (normal.x/abs(normal.x)) #fix
                    if abs(self.world_position.x - inter.world_point.x) < self.scale_x / 2:
                        self.world_position = Vec3(wall_x, self.world_position.y, 0)

                

            if not self.grounded:
                self.velocity.y -= self.gravity * time.dt

            
        else:
            self.initialize()

    def set_special_ignore(self, ignore):
        self.special_ignore.append(ignore)

    def finish_return_to_cycle(self):
        self.return_invoke = None
        self.return_to_cycle = False
        

    
    def moving_cycle(self):
        left_bound = float(self.e_start_pos.x) - float(self.e_range/2)
        right_bound = float(self.e_start_pos.x) + float(self.e_range/2)

        #print(f"current={self.world_position}")
        if self.moving and self.initialized and self.e_range!=0:
            if self.x > right_bound:
                #self.moving = False
                #self.__turn()
                self.go_to_bound(Vec3(right_bound, self.e_start_pos.y, 0), 1)
                self.parabam = -1
                
            elif self.x < left_bound:
                #self.moving = False
                #self.__turn()
                #print(f"call={Vec3(left_bound-0.5, self.e_start_pos.y+0.5, 0)}")
                self.go_to_bound(Vec3(left_bound, self.e_start_pos.y, 0), -1)
                self.parabam = 1
            else:
                self.world_position.z = 0
            
            
                
            self.velocity.x = self.parabam * self.speed
        elif not self.moving:
            self.velocity.x = 0
        
    def __turn(self):
        self.moving = True
    
    def go_to_bound(self, bound, offset):
        sp = 6
        self.world_position.z = -5
        target = Vec3(bound.x+offset, bound.y+1, -5)
        #print(target)
        #print(f"target= {target}")
        world_pos = Vec3(self.world_position.x, self.world_position.y, -5)
        dir = (target - world_pos).normalized()
        dir = Vec3(dir.x, dir.y, dir.z)
        print(f"dir={dir}")
        
        dist = distance(world_pos, target)
        print(f"dist={dist}") 

        if dist > 0.5:
            self.world_position += dir * sp * time.dt
        else:
            self.world_position = bound
            print(f"\n\nend={self.world_position}")




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

    


    player_controller = Enemy(scale_x=1, x=3, y=2)
    ec = EditorCamera()
    ec.add_script(SmoothFollow(target=player_controller, offset=[0,1,0], speed=4))

    def input(key):
        if key == 'c':
            player_controller.y -= 0.5
        if key == 'v':
            player_controller.velocity.y+=10

    app.run()



"""
Ideias: 
    . sphere + triangle/pyramid for player detection
"""