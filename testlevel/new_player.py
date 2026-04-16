from ursina import *
from math import *

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'cube'
        #self.origin_y = -.5
        self.scale_y = 1
        self.color = color.orange
        self.collider = 'box'

        self.animator = Animator({'idle' : None, 'walk' : None, 'jump' : None})

        self.velocity = Vec3(0,0,0) # for movement
        self.acel = 15 # for gravity and flinging
        self.speed = 8
        
        self.friction = 10

        self.gravity = 20
        self.jump_force = 8
        self.grounded = False
        
        self.hitwall = False
        self.hitting_head = False
        self.onslope = False

        self.traverse_target = scene
        #self.ignore = [self, ]
        #self.init_ignore = self.ignore

        self.flinged = False
        # self.fling_direction = ?
        self.fling_force = 1

        

        """self.start_position = (.5, .5)

        #spawn player on top of the ground
        ray = raycast(self.world_position, self.down, distance=10, ignore=self.ignore, traverse_target=self.traverse_target, debug=True)
        if ray.hit:
            self.y = ray.world_point[1] + .01"""

        for key, value in kwargs.items():
            setattr(self, key, value)

        # delay gravity???
        """target_gravity = self.gravity
        self.gravity = 0
        invoke(setattr, self, 'gravity', target_gravity, delay=1/60)
        self._original_scale_x = self.scale_x

        self.min_x = -99999
        self.max_x = 99999"""

    def update(self):
        dt = time.dt
        
        # LETS USE VECTORS YAAAAAAYYY
        move_x = held_keys['d'] - held_keys['a']
        input_dir = Vec3(move_x, 0, 0)
        target_x = input_dir.x * self.speed
    
        bxc = boxcast(self.position,
                      direction=Vec3(0,0,0),
                      distance=abs(self.scale_x),
                      ignore=[self],
                      thickness=(abs(self.scale_x), self.scale_y*.9),
                      debug=True)

        """bottom_ray1 = raycast(
            self.world_position + Vec3(0.4, 0.1, 0), #slightly above feet
            direction=Vec3(0,-1,0), #down
            distance=1.2,  
            ignore=[self],
            debug=True
        )

        bottom_ray2 = raycast(
            self.world_position + Vec3(-0.4, 0.1, 0), #slightly above feet
            direction=Vec3(0,-1,0), #down
            distance=1.2, 
            ignore=[self],
            debug=True
        )"""

        dist = 0.6*self.scale_y
        b_rays=[
                raycast(
                self.world_position + Vec3(0.4*self.scale_x, 0.05*self.scale_y, 0), #slightly above feet
                direction=Vec3(0,-1,0), #down
                distance=dist,  
                ignore=[self],
                debug=True
            ),
                raycast(
                self.world_position + Vec3(-0.4*self.scale_x, 0.05*self.scale_y, 0), #slightly above feet
                direction=Vec3(0,-1,0), #down
                distance=dist, 
                ignore=[self],
                debug=True
            ),
            #raycast(self.position+ Vec3(0,0.1,0),  Vec3(0,-1,0), distance=dist, ignore=[self], debug=True)


            #---------------------------------------------------
            # add boxcast for to resolve the spike collision on a slope
            # ---------------------------------------------------
        ]

        """if bottom_ray1.hit:
            # snap to the ground
            if self.velocity.y < 0:
                self.velocity.y = 0
                self.y = bottom_ray1.world_point.y + 1
            self.grounded = True
        else:
            self.grounded = False"""

        


        top_ray = raycast(
            self.world_position + Vec3(0, -0.1, 0), #slightly above feet
            direction=Vec3(0,1,0), #down
            distance=dist, 
            ignore=[self],
            debug=True
        )

        if top_ray.hit:
            self.hitting_head = True
            if self.velocity.y > 0:
                self.velocity.y = 0
                self.y += 0.05 * self.scale_y
        else: self.hitting_head = False

# ------- My way -------------------
        # check if on slope:
        """
        for ray in b_rays:
            if ray.hit:
                if self.velocity.y < 0:
                    self.velocity.y = 0
                    self.y = ray.world_point.y + 1
                self.grounded = True
            else:
                self.grounded = False
            
        xor = b_rays[0].hit != b_rays[1].hit
        both = b_rays[0].hit and b_rays[1].hit

        if xor or both:
            #self.onslope = False
            for ray in b_rays:
                #if bottom_ray2.hit: print("ray2hit")
                if ray.hit and ray.normal.y < 0.7:
                        self.onslope = True
                        #print("self.onslope")
        else:
            self.onslope = False
            #print("not self.onslope")"""

# -------- Claude way -----------------------
        """xor = b_rays[0].hit != b_rays[1].hit
        both = b_rays[0].hit and b_rays[1].hit

        if xor or both:"""
        hit_rays = [r for r in b_rays if r.hit]

        if hit_rays:
            self.grounded = True

            most_sloped = min(hit_rays, key=lambda r: r.normal.y) # looks for the ray with lover normal value, in other words, looks for the bigest angle with a surface. a_slope > a_flat==0
            self.onslope = most_sloped.normal.y < 0.9 # checks if really on slope

            if self.velocity.y < 0:
                self.velocity.y = 0
                self.y = max(r.world_point.y for r in hit_rays) + 0.5*self.scale_y
                
        else:
            self.onslope = False
            self.grounded= False


        if bxc.hit and not self.onslope: # bug: when hitting a head, bxc stops working properly
            self.velocity.x = 0
            n = bxc.normal.x
            if not self.hitting_head:
                if n > 0.5: # left side
                    self.x += 0.02
                elif n < 0.5: # right sideddddddddddddd
                    self.x -= 0.02
            # movement witn aceleration USING LEEERRRPPPP
            # lerp - transition from one value to another during determined time (instead of using for :P)
        elif input_dir.x != 0:
            """if self.hitwall:
                self.x += 1 * input_dir.x
                self.hitwall = False"""
            self.velocity.x = lerp(self.velocity.x, target_x, self.acel*dt)
        else:
            self.velocity.x = lerp(self.velocity.x, 0, self.friction*dt)

        # gravity (maybe this will be moved )
        self.velocity.y -= self.gravity * time.dt

        # movement
        self.position += self.velocity * dt

        
                

        # animations
        #if not self.grounded:
        #    self.animator.state = 'jump'
        #else:
        #    if self.walking:
        #        self.animator.state = 'walk'
        #    else:
        #        self.animator.state = 'idle'

        # lets try instead of using raycasts, use distance between ground and player

    def input(self, key):
        if key == 'space' and self.grounded:
            self.jump()

    def jump(self):
        self.velocity.y = self.jump_force


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


    player_controller = Player(x=3, y=20, scale_y=2)
    ec = EditorCamera()
    ec.add_script(SmoothFollow(target=player_controller, offset=[0,1,0], speed=4))

    app.run()
            
