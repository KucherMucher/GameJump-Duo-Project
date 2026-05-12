from ursina import *
from new_enemy import Enemy
from new_player import Player
from math import *
from weapon import *

class Wall(Entity):
    def __init__(self, **kwargs):  # accept kwargs
        super().__init__( **kwargs)



class Level():
    def __init__(self, **kwargs):
        super().__init__()
        self.player = Entity()
        self.enemy_list = []
        self.level_parent = Entity(model=Mesh(vertices=[], uvs=[]), texture='white_cube')
        self.quad = load_model('quad', use_deepcopy=True) # load it later with any model we want
        self.texture = 'testlevel'
        self.start_position = (1,1)

        for key, value in kwargs.items(): 
            setattr(self, key, value)

    def make_level(self, texture):
        [destroy(c) for c in self.level_parent.children]

        for y in range(texture.height):
            collider = None
            for x in range(texture.width):
                col = texture.get_pixel(x,y)

                # If it's black, it's solid, so we'll place a tile there.
                if col == color.black:
                    # instead of creating alot of different enteties it combines them in a single mesh to optimize rendering
                    self.level_parent.model.vertices += [Vec3(*e) + Vec3(x+.5,y+.5,0) for e in self.quad.generated_vertices] 
                    self.level_parent.model.uvs += self.quad.uvs
                    # Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), color=color.gray, texture='white_cube', visible=True)
                    if not collider:
                        collider = Wall(parent=self.level_parent, position=(x,y), model='cube', origin=(-.5,-.5), collider='box', visible=False)
                    else:
                        # instead of creating a new collider per tile, stretch the previous collider right.
                        collider.scale_x += 1
                        
                else:
                    # upgrade this mechanic to combine y collumns collidersd into one , instead of doing 10 colliders per first column
                    collider = None

                # If it's green, we'll place the player there. Store this in player.start_position so we can reset the plater position later.
                if col == color.green:
                    self.start_position = Vec3(x, y+1, 0)

                if col == color.red:
                    print(x, y)
                    self.enemy_list.append(Enemy(name=f"enemy{x}",scale=1, e_start_pos=Vec3(x, y-0.5, 0), e_range=4, y=y, x=x, z=0, speed=3, angry_speed=9, collider='box', traverse_target = scene))
                    """for each type of enemy we can create a list of attributions to give to each enemy, also depending on a level,of which include:
                            e_start (normaly the same as x),
                            e_range (range of moving, each way having half of a value),
                            velocity (direction),
                            y, x,
                            walk_speed,
                            idle (time), 
                    """
        
        self.level_parent.model.generate() 

    def load_level(self):
        self.clear_scene()
        self.player = Player(scale=1, collider='box', move=False, max_jumps=9999999)
        self.player.update()
        ground = Entity(model='cube', scale_x=10, collider='box', color=color.black)
        self.gun = Bazooka(parent=self.player)
        
        self.player.traverse_target = scene  # don't forget this

        self.make_level(load_texture(self.texture))

        # Apply start_position to the REAL player AFTER make_level runs
        self.player.position = self.start_position
        self.player.velocity = Vec3(0, 0, 0)  # reset any velocity too

        for i, enemy in enumerate(self.enemy_list):
            #print(f"Enemy {i}: position=({enemy.x}, {enemy.y}), e_start={enemy.e_start}")
            self.player.extend_collisions_ignore_list([enemy.cone_fov])

        camera.orthographic = True
        camera.position = (30/2, 8)
        camera.fov = 16

            

    # just in case
    def get_player(self):
        return self.player
    def get_enemy_list(self):
        return self.enemy_list
    
    def clear_scene(self):
        scene.clear()
        self.level_parent = Entity(model=Mesh(vertices=[], uvs=[]), texture='white_cube')
        self.enemy_list = []
    #return player, enemy_list

    #[print("hit enemy") for enemy in enemy_list if player.intersects(enemy).hit]
    def update(self):
        # function for damaging player
        if hasattr(self, 'player'): # check if player exists
            for enemy in self.enemy_list: # goes through every enemy
                # Check if player and enemy bounding boxes overlap
                inter = self.player.intersects(enemy) or enemy.intersects(self.player) or self.player.bxc.entity == enemy
                if inter:
                    self.player.extend_ignore_list(enemy)
                    relative = self.player.get_position(relative_to=enemy)
                    relative = relative.normalized()
                    force = 10
                    self.player.fling_player(fling_dir=relative, fling_force=Vec3(force*3, force ,0))
                        
                    print("hit enemy")
                

                gocha = self.player.intersects(enemy.cone_fov)
                """if gocha[0]:
                    print("Confusion")"""
                if gocha:
                    #print("Anger")
                    enemy.see_player = True
                else:
                    enemy.see_player = False

    def get_enemy_info(self):
        for e in self.enemy_list:
            print(f"Enemy: {e.name}",
                  f"break_cycle = {e.break_cycle}",
                  f"return_to_cycle = {e.return_to_cycle}",
                  f"return_invoke = {e.return_invoke}",
                  f"see_player = {e.see_player}",
                  f"no_sight = {e.no_sight}",)

        
                    





    