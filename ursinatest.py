from ursina import *

# create a window
app = Ursina()


e = Entity(model='cube', color=color.orange, scale=1, collider='box')
e.color = rgb(.4, .1, 0) # rgb color

#def update():
    # e.x += held_keys['d'] * time.dt
    # e.x -= held_keys['a'] * time.dt
    #camera.x += held_keys['d'] * time.dt
    #camera.x -= held_keys['a'] * time.dt


def input(key):
    if key == 'space':
        e.y += 1
        invoke(setattr, e, 'y', e.y-1, delay=.25)


camera.fov = 80
# start running the game
EditorCamera()
app.run()



