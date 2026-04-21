from ursina import *
app = Ursina()

from level_maker import Level
test_level = Level(texture='testlevel')
test_level.load_level()

ec = EditorCamera()
ec.add_script(SmoothFollow(target=test_level.player, offset=[-14.5,-8,0], speed=10))

def update():
    test_level.update()

def input(key):
    if key == 'x':
        test_level.player.move = True

app.run()