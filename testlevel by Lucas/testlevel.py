from ursina import *
app = Ursina()

from level_maker import Level
LevelList = ['textures and models/platformer_tutorial_level.png' , 'testlevel']
test_level = Level(texture=LevelList[0])
test_level.load_level()

ec = EditorCamera()
test_level.player.move = True
test_level.gun.get_weapon()

def NextLevel():
    global test_level
    test_level = Level(texture=LevelList[1])
    test_level.load_level()
    test_level.player.move = True
    test_level.gun.get_weapon()

def update():
    test_level.update()

def input(key):
    global ec
    if key == 'x':
        NextLevel()

app.run()