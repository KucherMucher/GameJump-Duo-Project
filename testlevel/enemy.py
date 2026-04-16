from ursina import *
from math import *



"""
current problem: enemy spawns sometimes at the coordinate and sometimes not on the coordinate
"""
class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'cube'
        self.origin_y = -.5
        self.scale_y = 2
        self.color = color.red
        self.collider = 'box'

        self.animator = Animator({'idle' : None, 'walk' : None, 'jump' : None})

        self.walk_speed = 8
        self.velocity = 0 # the walk direction is stored here. -1 for left and 1 for right.
        self.gravity = 1
        self.grounded = True
        self.air_time = 0   # this increase while we're falling and used when calculating the distance we fall so we fall faster and faster instead of linearly.
        self.traverse_target = scene     # by default, it will collide with everything except itself. you can change this to change the boxcast traverse target.
        self.ignore_list = [self, ]

        self.e_start = 6
        self.e_range = 1
        self.idle = 1
        self.moving = True
        self.break_cycle = False
        self.angry_speed = int(self.walk_speed*1.5)

        self.vision_radius = 5
        self.fov = 60

        self.initialized = False

        # automatically set attributes.
        for key, value in kwargs.items():
            setattr(self, key, value)


        # delay_gravity one frame
        target_gravity = self.gravity
        self.gravity = 0
        invoke(setattr, self, 'gravity', target_gravity, delay=1/60)
        self._original_scale_x = self.scale_x

        self.min_x = -99999
        self.max_x = 99999
        self.irr=1



    """
        in order for enemy to follow the player:
            . has to have a default moving cycle ( __moving_cycle() )
            . if raycast detects a player, break the cycle ( __break_cycle() or __break_cycle = True )
            . if the player is no longer detected by enemy, return to the cycle. ( __start_moving_cycle = True )
    """
    

    def __turn(self):
        self.moving = True

    def moving_cycle(self):
        if not self.break_cycle:
            if self.moving and self.initialized and self.e_range!=0:
                if self.x > abs(self.e_start+(self.e_range/2)):
                    self.x = self.e_start+(self.e_range/2)
                    self.moving = False
                    self.velocity = -1
                    invoke(self.__turn, delay=self.idle)
                if self.x < self.e_start-(self.e_range/2):
                    self.x = self.e_start-(self.e_range/2)
                    self.moving = False
                    self.velocity = 1
                    invoke(self.__turn, delay=self.idle)
                self.x += self.velocity * time.dt * self.walk_speed
        else:
            self.x += self.velocity * time.dt * self.angry_speed

    def follow_player(self):
        pass

    

    def update(self):
        if self.irr == 1: # debug
            print(f"Enemy at {self.position}, grounded={self.grounded}")

            print(
            self.position+Vec3(self.velocity * time.dt * self.walk_speed,self.scale_y/2,0),
            abs(self.scale_x), 
            self.ignore_list,
            self.traverse_target,
            (abs(self.scale_x)*.99, self.scale_y*.9))

            self.irr+=1
            
        if not boxcast(
            self.position+Vec3(self.velocity * time.dt * self.walk_speed,self.scale_y/2,0),
            direction=Vec3(0,0,0),
            distance=abs(self.scale_x),
            ignore=self.ignore_list,
            traverse_target=self.traverse_target,
            thickness=(abs(self.scale_x)*.99, self.scale_y*.9),
            debug=True).hit:
                self.moving_cycle()

        # animations
        if not self.grounded:
            self.animator.state = 'jump'
        else:
            if self.moving:
                self.animator.state = 'walk'
            else:
                self.animator.state = 'idle'


        # check if we're on the ground or not.
        ray = raycast(self.world_position+Vec3(0,.1,0), self.down, distance=max(.15, self.air_time * self.gravity), ignore=self.ignore_list, traverse_target=self.traverse_target)#, debug=True
        left_ray = raycast(self.world_position+Vec3(-abs(self.scale_x)*.49,.1,0), self.down, distance=max(.15, self.air_time * self.gravity), ignore=self.ignore_list, traverse_target=self.traverse_target)#, debug=True
        right_ray = raycast(self.world_position+Vec3(abs(self.scale_x)*.49,.1,0), self.down, distance=max(.15, self.air_time * self.gravity), ignore=self.ignore_list, traverse_target=self.traverse_target)#, debug=True
        
        # added those in order to keep track of slopes (like if it clips, move up or sashimi)
        """central_left_ray = raycast(self.world_position+Vec3(-abs(self.scale_x)*.49,.2,0), self.down, distance=max(.15, self.air_time * self.gravity), ignore=self.ignore_list, traverse_target=self.traverse_target)#, debug=True
        central_right_ray = raycast(self.world_position+Vec3(abs(self.scale_x)*.49,.2,0), self.down, distance=max(.15, self.air_time * self.gravity), ignore=self.ignore_list, traverse_target=self.traverse_target)#, debug=True
        central_ray = raycast(self.world_position+Vec3(0,.4,0), self.down, distance=.15, ignore=self.ignore_list, traverse_target=self.traverse_target) #, debug=True

        #print(self.grounded)"""

        # using fov, we will spawn rays that will detect player, by using the fov angle (using trigonometry) to create a "circle" of detection 
        offset = self.fov/2 # to centralize rays
        detector_ray_list = [
            raycast(self.world_position+Vec3(0,self.scale_y*.5,0),
                     direction=Vec3(cos(radians(i-offset))*self.velocity,sin(radians(i-offset))*self.velocity,0),
                     distance=self.vision_radius,
                     ignore=self.ignore_list, traverse_target=self.traverse_target, debug=True)
            for i in range(self.fov) if i % 5 == 0
        ]

        """for ray in detector_ray_list: 
            if ray.hits == PlatformerController3():
                print("detected player")"""
        
        from new_player import Player # dont put on top to avoid circular import
        if any(ray.hit and isinstance(ray.entity, Player) for ray in detector_ray_list):
            #print("hit player")
            self.break_cycle = True
            #current_player_posistion = (ray.entity.x, ray.entity.y)
        else:
            self.break_cycle = False
        
        #raycast(self.world_position+Vec3(0,self.scale_y*.5,0), direction=Vec3(cos(radians(ang)),sin(radians(ang)),0), distance=self.vision_radius ,ignore=self.ignore_list, traverse_target=self.traverse_target, debug=True)
        

        # like i said, when those are hit, move up the player
        """if any((central_ray.hit, central_left_ray.hit, central_right_ray.hit)): 
            print("hit")
            self.y+=.5"""
        
        if any((ray.hit, left_ray.hit, right_ray.hit)):
            if not self.grounded:
                self.land()
                
            
            self.y = max(r.world_point.y for r in (ray, left_ray, right_ray) if r.hit)
            self.grounded = True
            return
        else:
            self.grounded = False

        # if not on ground and not on way up in jump, fall
        if not self.grounded:
            # print(self.air_time)
            self.y -= min(self.air_time * self.gravity, ray.distance-.1)
            self.air_time += time.dt*4 * self.gravity   # fall faster and faster the long we've stayed in the air
        
        self.initialized = True

        # if in jump and hit the ceiling, fall
        """if self.jumping:
            # if boxcast(self.position+(0,.2,0), self.up, distance=self.scale_y, thickness=.95, ignore=self.ignore_list, traverse_target=self.traverse_target).hit:
            hit_above = raycast(self.world_position+Vec3(0,self.scale_y/2,0), self.up, distance=self.jump_height-(self.scale_y/2), traverse_target=self.traverse_target, ignore=self.ignore_list)
            hit_above_left = raycast(self.world_position+Vec3(-abs(self.scale_x)*.49,self.scale_y/2,0), self.up, distance=self.jump_height-(self.scale_y/2), traverse_target=self.traverse_target, ignore=self.ignore_list)
            hit_above_right = raycast(self.world_position+Vec3(abs(self.scale_x)*.49,self.scale_y/2,0), self.up, distance=self.jump_height-(self.scale_y/2), traverse_target=self.traverse_target, ignore=self.ignore_list)
            if any((hit_above.hit, hit_above_left.hit, hit_above_right.hit)):
                if hasattr(self, 'y_animator'):
                    self.y_animator.kill()
                self.air_time = 0
                self.start_fall()"""
        
        
    """
    # change this to just a fall function
    def jump(self):
        if not self.grounded and self.jumps_left <= 1:
            return

        if self._start_fall_sequence:
            self._start_fall_sequence.kill()

        if hasattr(self, 'y_animator'):
            self.y_animator.kill()
        self.jump_dust = Entity(model=Circle(), scale=.5, color=color.white33, position=self.position)
        self.jump_dust.animate_scale(3, duration=.3, curve=curve.linear)
        self.jump_dust.fade_out(duration=.2)
        destroy(self.jump_dust, 2.1)

        self.jumping = True
        self.jumps_left -= 1
        self.grounded = False

        target_y = self.y + self.jump_height
        duration = self.jump_duration

        self.animate_y(target_y, duration, resolution=30, curve=curve.out_expo)
        self._start_fall_sequence = invoke(self.start_fall, delay=duration)


    def start_fall(self):
        if hasattr(self, 'y_animator'):
            self.y_animator.pause()
        self.jumping = False


    
"""
    def land(self):
        # print('land')
        self.air_time = 0
        self.grounded = True

        





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


    player_controller = Enemy(scale_y=1, x=3, y=20)
    ec = EditorCamera()
    ec.add_script(SmoothFollow(target=player_controller, offset=[0,1,0], speed=4))

    app.run()


    