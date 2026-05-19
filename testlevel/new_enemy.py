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

        self.velocity = Vec3(1,0,0) # for movement
        self.speed = 4

        self.gravity = 20
        self.grounded = False
        self.distconst = 0.6

        self.hitwall = False
        self.onslope = False

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
        self.no_sight = 0
        self.start_return = False

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
                                debug=True,
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

        self.left_bound = float(self.e_start_pos.x) - float(self.e_range/2)
        self.right_bound = float(self.e_start_pos.x) + float(self.e_range/2)
        

    def initialize(self):
        #print("\n\n\n"+str(self.ignore_list)+"\n\n\n")
        self.initialized = True
        

    def update(self):
        #print(".")
        if self.initialized:
            dt = time.dt
            if not self.start_return:
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
            
            if not self.break_cycle and not self.return_to_cycle:
                if self.return_invoke != None: # just to be safe
                    self.return_invoke.kill()
                    self.return_invoke = None
                #self.moving_cycle()
                if self.x > self.right_bound:
                    self.parabam = -1
                elif self.x < self.left_bound:
                    self.parabam = 1
                self.velocity.x = self.parabam * self.speed
                #print("moving_cycle")
            elif self.return_to_cycle:
                """
                1 . out of left bound
                2 . out of right bound
                3 . below or on top of bound
                4 . default
                """
                if self.x > self.right_bound + 0.1:
                    self.go_to_bound(Vec3(self.right_bound, self.e_start_pos.y, 0), 0)
                elif self.x < self.left_bound - 0.1:
                    self.go_to_bound(Vec3(self.left_bound, self.e_start_pos.y, 0), 0)
                elif self.y < self.e_start_pos.y - 0.1:
                    self.go_to_bound(Vec3(self.x, self.e_start_pos.y, 0), 0)
                elif self.y - self.e_start_pos.y > 1:
                    self.go_to_bound(Vec3(self.x, self.e_start_pos.y, 0), 0)
                else:
                    if self.return_invoke == None:
                        self.return_invoke = invoke(self.finish_return_to_cycle, delay=1)
                #print("return_to_cycle")

            if self.see_player:
                self.no_sight = 0
                self.break_cycle = True
                if self.return_invoke != None:
                    self.return_invoke.kill()
                    self.return_invoke = None
                self.velocity.x = self.angry_speed * self.parabam
                #print("see_player")
            elif not self.see_player and self.break_cycle:
                self.no_sight += 1
                if self.no_sight > 10:
                    self.break_cycle = False
                    self.return_to_cycle = True
                    self.no_sight = 0
                #print("not see_player and break_cycle")
                

            
            if isinstance(inter.entity, Wall): 
                normal = inter.normal
                if self.grounded and normal.y > 0.5:
                    self.velocity.y = 0
                    ground_y = inter.world_point.y + self.scale_y / 2 #fix
                    if self.world_position.y < ground_y:
                        self.world_position = Vec3(self.world_position.x, ground_y, self.world_position.z)

                if abs(normal.x) > 0.5:
                    
                    wall_x = inter.world_point.x + (self.scale_x / 2) * (normal.x/abs(normal.x)) #fix
                    if abs(self.world_position.x - inter.world_point.x) < self.scale_x / 2:
                        self.world_position = Vec3(wall_x, self.world_position.y, self.world_position.z)

                
            if not self.grounded:
                self.velocity.y -= self.gravity * time.dt  
            
        else:
            self.initialize()

    def set_special_ignore(self, ignore):
        self.special_ignore.append(ignore)

    def finish_return_to_cycle(self):
        self.return_invoke = None
        self.return_to_cycle = False
        self.start_return = False
    
    def go_to_bound(self, bound, offset):
        #print(f"z at start of go_to_bound = {self.position.z}")
        if not self.start_return:
            self.start_return = True
            self.position = Vec3(self.position.x, self.position.y, 2)
            print(self.position)
        abs_bound = Vec3(bound.x, bound.y, 0)
        abs_pos = Vec3(self.position.x, self.position.y, 0)
        dist = distance(abs_pos, abs_bound)
        # print(dist)
        dir = (abs_bound - abs_pos).normalized()
        # print(dir)
        
        if dist < 0.5:
            self.position = bound # bound should have z as 0
            if self.return_invoke == None:
                self.return_invoke = invoke(self.finish_return_to_cycle, delay=1)
        else:
            self.position += dir * self.angry_speed * time.dt

        #print(f"z at end of go_to_bound = {self.position.z}")




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