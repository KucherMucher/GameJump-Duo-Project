from ursina import *
from math import *
from weapon import *


class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'cube'
        self.texture = ""
        #self.origin_y = -.5
        self.scale_y = 1
        self.color = color.orange
        self.collider = 'box'
        

        self.animator = Animator({'idle' : None, 'walk' : None, 'jump' : None})

        self.velocity = Vec3(0,0,0) # for movement
        self.acel = 15 # for gravity and flinging
        self.speed = 8
        self.input_dir = Vec3(0,0,0)
        
        self.friction = 10

        self.gravity = 20
        self.jump_force = 8
        self.grounded = False
        self.land_y = self.y
        self.distconst = 0.6

        self.max_jumps = 2
        self.jumps = self.max_jumps
        
        self.hitwall = False
        self.hitting_head = False
        self.onslope = False

        self.traverse_target = scene
        self.ignore_list = [self] #never use self.ignore
        self.init_ignore = [self]
        self.collisions_ignore_list = []

        self.flinged = False
        # self.fling_direction = ?
        self.__fling_dir = Vec3(1, 1, 0)
        self.__fling_force = Vec3(1, 1, 0)
        self.__enemy_dir = Vec3(1, 1, 0)
        self.move = True

        self.old_y = 0

        self.bxc: boxcast = None

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
        compiled_ignore = self.ignore_list+self.collisions_ignore_list
        self.bxc = boxcast(self.position+Vec3(self.input_dir.x*dt*self.speed, 0, 0),
                        direction=Vec3(0,0,0),
                        distance=abs(self.scale_x),
                        ignore=compiled_ignore,
                        thickness=(abs(self.scale_x-self.speed*dt), self.scale_y*.9),
                        debug=True)
        if self.move:
            #print("\n\n"+str(compiled_ignore))
            self.position += self.velocity * dt
            # LETS USE VECTORS YAAAAAAYYY
            move_x = held_keys['d'] - held_keys['a']
            self.input_dir = Vec3(move_x, 0, 0)
            target_x = self.input_dir.x * self.speed
        
            

            dist = self.distconst*self.scale_y
            
            b_rays=[
                    raycast(
                    self.world_position + Vec3(0.4*self.scale_x, 0.05*self.scale_y, 0), #slightly above feet
                    direction=Vec3(0,-1,0), #down
                    distance=dist,  
                    ignore=compiled_ignore,
                    debug=True
                ),
                    raycast(
                    self.world_position + Vec3(-0.4*self.scale_x, 0.05*self.scale_y, 0), #slightly above feet
                    direction=Vec3(0,-1,0), #down
                    distance=dist, 
                    ignore=compiled_ignore,
                    debug=True
                ),
                #raycast(self.position+ Vec3(0,0.1,0),  Vec3(0,-1,0), distance=dist, ignore=[self], debug=True)


                #---------------------------------------------------
                # add boxcast for to resolve the spike collision on a slope
                # ---------------------------------------------------
            ]

            t_rays=[
                raycast(
                self.world_position + Vec3(0.4*self.scale_x, -0.05*self.scale_y, 0), #slightly above feet
                direction=Vec3(0,1,0), #down
                distance=dist, 
                ignore=compiled_ignore,
                debug=True
                ),
                raycast(
                self.world_position + Vec3(-0.4*self.scale_x, -0.05*self.scale_y, 0), #slightly above feet
                direction=Vec3(0,1,0), #down
                distance=dist, 
                ignore=compiled_ignore,
                debug=True
                )
            ]

            # top y collision logic
            hit_rays_t = [r for r in t_rays if r.hit]
            if hit_rays_t:
                #self.hitting_head = True
                if self.velocity.y > 0:
                    self.velocity.y = 0 
                    # fix
                    ceiling_y = max(r.world_point.y for r in hit_rays_t) + self.scale_y/2
                    if self.world_position.y > ceiling_y:
                        self.world_position.y = ceiling_y 
            #else: self.hitting_head = False

            # x collisions and movement logic
            if self.bxc.hit and not self.onslope: # bug: when hitting a head, bxc stops working properly
                #print(bxc.normal)
                self.velocity.x = 0
                if self.bxc.normal.x != 0:
                    sign = (self.bxc.normal.x/abs(self.bxc.normal.x))
                else:
                    sign = 1
                wall_x = self.bxc.world_point.x + (self.scale_x / 2) * sign #fix
                if abs(self.world_position.x - self.bxc.world_point.x) < self.scale_x / 2:
                    self.world_position.x = wall_x
                # movement witn aceleration USING LEEERRRPPPP
                # lerp - transition from one value to another during determined time (instead of using for :P)
                
            elif self.input_dir.x != 0:
                self.velocity.x = lerp(self.velocity.x, target_x, self.acel*dt)
            else:
                self.velocity.x = lerp(self.velocity.x, 0, self.friction*dt)

            if self.flinged:
                
                #print(self.velocity)
                self.velocity = self.__fling_dir * self.__fling_force
                #print(d)
                #print(self.velocity)
                #invoke(setattr, self, 'ignore_list', self.init_ignore, delay=100)
                self.ignore_list = self.init_ignore.copy()
                
                self.flinged = False

            # bottom y collision logic
            hit_rays_b = [r for r in b_rays if r.hit]
            if hit_rays_b:
                self.land()
                self.grounded = True # change this to somewhere else or else that logic* wont work 

                most_sloped = min(hit_rays_b, key=lambda r: r.normal.y) # looks for the ray with lover normal value, in other words, looks for the bigest angle with a surface. a_slope > a_flat==0
                self.onslope = most_sloped.normal.y < 0.9 # checks if really on slope

                # y fix
                if self.velocity.y < 0:
                    self.velocity.y = 0
                    if self.grounded: # *- this logic
                        if self.bxc.hit:
                            correct = min(r.world_point.y for r in hit_rays_b) + 0.5*self.scale_y
                        else:
                            correct = max(r.world_point.y for r in hit_rays_b) + 0.5*self.scale_y
                        self.y = correct
                
                """
                    case 1: bxc hit and not grounded - dont make offset
                    case 2: bxc hit and grounded - offset min
                    case 3: not bxc hit and grounded - offset max (for onslope) 
                """
            else:
                self.onslope = False
                self.grounded = False

           
            

            

            # gravity (maybe this will be moved )
            
            self.velocity.y -= self.gravity * time.dt
            #print(self.velocity.y)

            

        
                

        # animations
        #if not self.grounded:
        #    self.animator.state = 'jump'
        #else:
        #    if self.walking:
        #        self.animator.state = 'walk'
        #    else:
        #        self.animator.state = 'idle'

        # lets try instead of using raycasts, use distance between ground and player
    def fling_player(self, fling_dir, fling_force): #, ed
        self.flinged = True
        self.__fling_dir = fling_dir
        self.__fling_force = fling_force
        #self.__enemy_dir = ed.normalized()
        #print(self.__enemy_dir)

    def input(self, key):
        if key == 'space' and self.jumps > 0:
            self.jump()

    def jump(self):
        self.velocity.y = self.jump_force
        self.jumps -= 1

    def land(self):
        self.jumps = self.max_jumps

    def extend_ignore_list(self, ignore):
        if isinstance(ignore, list):
            self.ignore_list.extend(ignore)
        else:
            self.ignore_list.append(ignore)
    def remove_elem_ignore_list(self, ignore):
        self.ignore_list.remove(ignore)

    def extend_collisions_ignore_list(self, ignore):
        if isinstance(ignore, list):
            self.collisions_ignore_list.extend(ignore)
        else:
            self.collisions_ignore_list.append(ignore)
    def remove_elem_collisions_ignore_list(self, ignore):
        self.collisions_ignore_list.remove(ignore)

    def reset_ignore_list(self):
        self.ignore_list = self.init_ignore.copy()


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
    gun = Bazooka(parent=player_controller, weapon="bazooka")

    app.run()
            
