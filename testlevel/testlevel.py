from ursina import *
app = Ursina()

from tt import PlatformerController3
from enemy import Enemy
player = PlatformerController3(scale=1, max_jumps=1, jump_height=2)
ground = Entity(model='cube', scale_x=10, collider='box', color=color.black)

level_parent = Entity(model=Mesh(vertices=[], uvs=[]), texture='white_cube')
quad = load_model('quad', use_deepcopy=True) # load it later with any model we want

enemy = Enemy(scale=1, e_start=16, e_range=4, y=4, x=16)



def make_level(texture):
    [destroy(c) for c in level_parent.children]

    for y in range(texture.height):
        collider = None
        for x in range(texture.width):
            col = texture.get_pixel(x,y)

            # If it's black, it's solid, so we'll place a tile there.
            if col == color.black:
                # instead of creating alot of different enteties it combines them in a single mesh to optimize rendering
                level_parent.model.vertices += [Vec3(*e) + Vec3(x+.5,y+.5,0) for e in quad.generated_vertices] 
                level_parent.model.uvs += quad.uvs
                # Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), color=color.gray, texture='white_cube', visible=True)
                if not collider:
                    collider = Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), collider='box', visible=False)
                else:
                    # instead of creating a new collider per tile, stretch the previous collider right.
                    collider.scale_x += 1
            else:
                # upgrade this mechanic to combine y collumns collidersd into one , instead of doing 10 colliders per first column
                collider = None

            # If it's green, we'll place the player there. Store this in player.start_position so we can reset the plater position later.
            if col == color.green:
                player.start_position = (x, y)
                player.position = player.start_position
    
    level_parent.model.generate()

make_level(load_texture('testlevel'))

camera.orthographic = True
camera.position = (30/2,8)
camera.fov = 16

player.gravity = True

player.traverse_target = level_parent
enemy.traverse_target = level_parent




EditorCamera()
app.run()

