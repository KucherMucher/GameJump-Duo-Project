from ursina import *
from enemy import Enemy
from new_player import Player




class Level():
    def __init__(self, **kwargs):
        super().__init__()
        self.player = Entity()
        self.enemy_list = []
        self.level_parent = Entity(model=Mesh(vertices=[], uvs=[]), texture='white_cube')
        self.quad = load_model('quad', use_deepcopy=True) # load it later with any model we want
        self.texture = 'testlevel'

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
                        collider = Entity(parent=self.level_parent, position=(x,y), model='cube', origin=(-.5,-.5), collider='box', visible=False)
                    else:
                        # instead of creating a new collider per tile, stretch the previous collider right.
                        collider.scale_x += 1
                        
                else:
                    # upgrade this mechanic to combine y collumns collidersd into one , instead of doing 10 colliders per first column
                    collider = None

                # If it's green, we'll place the player there. Store this in player.start_position so we can reset the plater position later.
                if col == color.green:
                    self.player.start_position = (x, y)
                    self.player.position = self.player.start_position

                if col == color.red:
                    print(x, y)
                    self.enemy_list.append(Enemy(scale=1, e_start=x, e_range=4, velocity=1, y=y, x=x, walk_speed=2, z=0, collider='box', traverse_target = scene))
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
        self.player = Player(scale=1, max_jumps=1, jump_height=2, y=1, z=0, collider='box')
        ground = Entity(model='cube', scale_x=10, collider='box', color=color.black)
        
        self.player.traverse_target = scene

        self.make_level(load_texture(self.texture))

        for i, enemy in enumerate(self.enemy_list):
            print(f"Enemy {i}: position=({enemy.x}, {enemy.y}), e_start={enemy.e_start}")

        camera.orthographic = True
        camera.position = (30/2,8)
        camera.fov = 16

        self.player.gravity = True

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
    """def update(self):
        # function for damaging player
        if hasattr(self, 'player'): # check if player exists
            for enemy in self.enemy_list: # goes through every enemy
                # Check if player and enemy bounding boxes overlap
                if self.player.intersects(enemy).hit:
                    self.player.fling_player(enemy.velocity, 20)
                    self.player.ignore_list.append(enemy)
                    self.player.update()
                    print("hit enemy")"""
                    





    