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
        self.angry_speed = int(self.speed*1.5)

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
            
            # LETS USE VECTORS YAAAAAAYYY
            """move_x = held_keys['d'] - held_keys['a']
            self.input_dir = Vec3(move_x, 0, 0)
            target_x = self.input_dir.x * self.speed"""
        
            bxc = boxcast(self.position,
                        direction=Vec3(0,0,0),
                        distance=abs(self.scale_x),
                        ignore=self.ignore_list,
                        thickness=(self.scale_x, self.scale_y),
                        debug=True)

            """dist = self.distconst*self.scale_y
            b_rays=[
                    raycast(
                    self.world_position + Vec3(0.4*self.scale_x, 0.05*self.scale_y, 0), #slightly above feet
                    direction=Vec3(0,-1,0), #down
                    distance=dist,  
                    ignore=self.ignore_list,
                    debug=True
                ),
                    raycast(
                    self.world_position + Vec3(-0.4*self.scale_x, 0.05*self.scale_y, 0), #slightly above feet
                    direction=Vec3(0,-1,0), #down
                    distance=dist, 
                    ignore=self.ignore_list,
                    debug=True
                ),
                #raycast(self.position+ Vec3(0,0.1,0),  Vec3(0,-1,0), distance=dist, ignore=[self], debug=True)


                #---------------------------------------------------
                # add boxcast for to resolve the spike collision on a slope
                # ---------------------------------------------------
            ]

            top_ray = raycast(
                self.world_position + Vec3(0, -0.05*self.scale_y, 0), #slightly above feet
                direction=Vec3(0,1,0), #down
                distance=dist, 
                ignore=self.ignore_list,
                debug=True
            )

            if top_ray.hit:
                self.hitting_head = True
                if self.velocity.y > 0:
                    self.velocity.y = 0
                    self.y += 0.05 * self.scale_y
            else: self.hitting_head = False"""

            epsilon = 0.05
            #hit_rays = [r for r in b_rays if r.hit]
            normal = bxc.normal
            if normal is None:
                normal = Vec3(0,0,0)

            print(normal)
            if normal == 1:
                self.grounded = True # change this to somewhere else or else that logic* wont work 

                #most_sloped = min(hit_rays, key=lambda r: r.normal.y) # looks for the ray with lover normal value, in other words, looks for the bigest angle with a surface. a_slope > a_flat==0
                #self.onslope = most_sloped.normal.y < 0.9 # checks if really on slope
                

                if self.velocity.y < 0:
                    self.velocity.y = 0
                """if self.grounded: # *- this logic
                        if bxc.hit:
                            correct = min(r.world_point.y for r in hit_rays) + 0.5*self.scale_y
                        else:
                            correct = max(r.world_point.y for r in hit_rays) + 0.5*self.scale_y
                        self.y = correct"""
                
                """
                    case 1: bxc hit and not grounded - dont make offset
                    case 2: bxc hit and grounded - offset min
                    case 3: not bxc hit and grounded - offset max (for onslope) 
                """
            else:
                self.onslope = False
                self.grounded= False

            if normal.x == 0:
                self.moving_cycle()
            else:
                self.velocity.x = 0

            # /(0,707^2 + 0,707^2) = 0.5 + 0.5 = 1 => 45º 


            """if bxc.hit and not self.onslope: # bug: when hitting a head, bxc stops working properly
                print(bxc.normal)
                self.velocity.x = 0
                # movement witn aceleration USING LEEERRRPPPP
                # lerp - transition from one value to another during determined time (instead of using for :P)
            elif self.flinged:
                if self.input_dir.x != 0:
                    d = -self.input_dir.x
                else:
                    d = self.__enemy_dir.x
                self.velocity = Vec3(d*self.__fling_dir.x*self.__fling_force.x, self.__fling_dir.y*self.__fling_force.y, 0)
                self.flinged = False
                invoke(setattr, self, 'ignore_list', self.init_ignore, delay=dt*2)
            elif self.input_dir.x != 0:
                self.velocity.x = lerp(self.velocity.x, target_x, self.acel*dt)
            else:
                self.velocity.x = lerp(self.velocity.x, 0, self.friction*dt)"""

            # gravity (maybe this will be moved )
            if not self.grounded:
                self.velocity.y -= self.gravity * time.dt

            # movement
            self.position += self.velocity * dt
        self.initialized = True

    def moving_cycle(self):
        if not self.break_cycle:
            if self.moving and self.initialized and self.e_range!=0:
                if self.x > abs(self.e_start+(self.e_range/2)):
                    self.x = self.e_start+(self.e_range/2)
                    self.moving = False
                    self.velocity.x = -1
                    invoke(self.__turn, delay=self.idle)
                if self.x < self.e_start-(self.e_range/2):
                    self.x = self.e_start-(self.e_range/2)
                    self.moving = False
                    self.velocity.x = 1
                    invoke(self.__turn, delay=self.idle)
                self.velocity.x *= self.speed
        else:
            self.velocity.x *= self.angry_speed

    def __turn(self):
        self.moving = True


if __name__ == '__main__':
    # window.vsync = False
    app = Ursina()
    camera.orthographic = True
    camera.fov = 10

    ground = Entity(model='cube', color=color.white33, origin_y=.5, scale=(20, 1, 1), collider='box', y=-1)
    wall = Entity(model='cube', color=color.azure, origin=(-.5,.5), scale=(5,10), x=10, y=.5, collider='box')
    wall_2 = Entity(model='cube', color=color.white33, origin=(-.5,.5), scale=(5,10), x=10, y=0, collider='box')
    ceiling = Entity(model='cube', color=color.white33, origin_y=-.5, scale=(1, 1, 1), y=1, collider='box')
    ceiling = Entity(model='cube', color=color.white33, origin_y=-.5, scale=(5, 5, 1), y=2, collider='box')
    ground = Entity(model='cube', color=color.white33, origin_y=.5, scale=(20, 3, 1), collider='box', y=-1, rotation_z=45, x=-5)

    def input(key):
        if key == 'c':
            wall.collision = not wall.collision
            print(wall.collision)


    player_controller = Enemy(scale_y=1, x=3, y=1)
    ec = EditorCamera()
    ec.add_script(SmoothFollow(target=player_controller, offset=[0,1,0], speed=4))

    app.run()