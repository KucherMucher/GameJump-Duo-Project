from ursina import *
import random
app = Ursina()

import tt
player = tt.PlatformerController3(y=1, z=.01, scale=1, max_jumps=2, model = 'maincaractere.obj', texture='texture', rotation_y = 45)
#player = Entity(position=Vec3(0,1,.01), scale=1, model='cube', collider='box', color=color.orange)

quad = load_model('quad', use_deepcopy=True)

level_parent = Entity(model=Mesh(vertices=[], uvs=[]), )
def make_level(texture):
    # destroy every child of the level parent.
    # This doesn't do anything the first time the level is generated, but if we want to update it several times
    # this will ensure it doesn't just create a bunch of overlapping entities.
    [destroy(c) for c in level_parent.children]

    for y in range(texture.height):
        collider = None
        for x in range(texture.width):
            col = texture.get_pixel(x,y)

            # If it's black, it's solid, so we'll place a tile there.
            if col == color.black or col == color.cyan or col == color.peach or col == color.olive:
                level_parent.model.vertices += [Vec3(*e) + Vec3(x+.5,y+.5,0) for e in quad.generated_vertices] # copy the quad model, but offset it with Vec3(x+.5,y+.5,0)
                level_parent.model.uvs += quad.uvs
                level_parent.color = color.clear
                if col == color.black:
                    roll = random.randint(0, 100)
                    if 0 < roll < 90:
                        Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), visible=True, texture="wall1.jpg")
                    elif roll >= 90:
                        Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), visible=True, texture="wall1b.jpg")
                    elif roll == 0:
                        Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), visible=True, texture="wall1c.jpg")
                elif col == color.cyan:
                    Entity(parent=level_parent, position=(x,y), model='modelBloko.gltf', origin=(-.5,0), visible=True)
                elif col == color.peach:
                    Entity(parent=level_parent, position=(x,y), model='modelBloko2.gltf', origin=(-.5,0), visible=True)
                elif col == color.olive:
                    Entity(parent=level_parent, position=(x,y), model='modelBloko3.gltf', origin=(-.5,0), visible=True)

                if not collider:
                    collider = Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), collider='box', visible=False)
                else:
                    # instead of creating a new collider per tile, stretch the previous collider right.
                    collider.scale_x += 1
            else:
                collider = None

            # If it's green, we'll place the player there. Store this in player.start_position so we can reset the plater position later.
            if col == color.green:
                player.start_position = (x, y)
                player.position = player.start_position
            
            if col == color.salmon:
                    Flag = Entity(parent=level_parent, position=(x,y), collider='mesh', model='FLAGER.gltf', origin=(-.5,0), visible=True)
                    if player.intersects(Flag).hit:
                        print('level Up')
                        player.position = player.start_position


    level_parent.model.generate()

make_level(load_texture('platformer_tutorial_level'))   # generate the level

camera.orthographic = True
camera.position = (30/2,8)
camera.fov = 16


player.traverse_target = level_parent
enemy = Entity(collider='mesh', position=(16,5,-.1), model='termite.obj', texture='texture_termite.png', rotation_y = 135)
def update():
    if player.intersects(enemy).hit:
        print('die')
        player.position = player.start_position
    


EditorCamera()
app.run()
