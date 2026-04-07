from ursina import *
app = Ursina()

from level_maker import Level
test_level = Level('testlevel')
test_level.load_level()

EditorCamera()
mouse.visible = True


"""def update():
    # This checks if the player is hitting ANY collider in the scene
    hit_info = player.intersects()
    
    if hit_info.hit:
        # Check if the thing we hit is actually an enemy
        if hit_info.entity in enemy_list:
            print(f"Hit enemy")
            # Optional: destroy(hit_info.entity)"""

app.run()