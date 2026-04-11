from ursina import *
app = Ursina()

from level_maker import Level
test_level = Level(texture='testlevel')
test_level.load_level()

EditorCamera()

#def update():
    #test_level.update()

app.run()