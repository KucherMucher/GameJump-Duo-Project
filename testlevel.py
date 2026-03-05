from ursina import *
app = Ursina()

from ursina.prefabs.platformer_controller_2d import PlatformerController2d
#player = Entity(position=Vec3(2,2,0), scale=1, model='cube', collider='box', color=color.orange)


ground = Entity(model='cube', scale_x=10, collider='box', color=color.black)

level_parent = Entity(model=Mesh(vertices=[], uvs=[]), texture='white_cube')

def make_level():
    [destroy(c) for c in level_parent.children]

    for y in range(10):
        collider = None
        for x in range(20):
            # use texture methos like in tutorial, for now.
            if y == 1 or y == 10:
                Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), color=color.gray, texture='white_cube', visible=True)

            else:
                if x == 1 or x == 20:
                    Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), color=color.gray, texture='white_cube', visible=True)

                elif x == 3 and y == 3:
                    player.position = (x, y)
    
    level_parent.model.generate()

make_level()

camera.orthographic = True
camera.position = (30/2,8)
camera.fov = 16

player.gravity = True
                
def update():
    if held_keys['d']:
        player.x += .1
    if held_keys['a']:
        player.x -= .1

    


EditorCamera()
app.run()