from ursina import *
app = Ursina()

ground = Entity(model='cube', scale_x=10, collider='box', color=color.black)

level_parent = Entity(model=Mesh(vertcices=[], uvs=[]), texture='white_cube')

def make_level():
    [destroy(c) for c in level_parent.children]

    for y in range(10):
        collider = None
        for x in range(20):
            # use texture methos like in tutorial, for now.