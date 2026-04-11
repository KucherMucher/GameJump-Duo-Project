from ursina import *

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.orange,
            collider='box',
            **kwargs
        )

        # Physics
        self.velocity = Vec3(0, 0, 0)
        self.gravity = 20
        self.jump_force = 8
        self.speed = 8
        self.acceleration = 15   # how fast we reach top speed
        self.friction = 10       # how fast we decelerate when no input

        # State
        self.grounded = False

    def update(self):
        dt = time.dt

        # --- Horizontal input ---
        move_x = held_keys['d'] - held_keys['a']
        move_z = held_keys['w'] - held_keys['s']
        input_dir = Vec3(move_x, 0, move_z)

        # Normalize diagonal movement
        if input_dir.length() > 0:
            input_dir = input_dir.normalized()

        # Accelerate toward target horizontal velocity
        target_x = input_dir.x * self.speed
        target_z = input_dir.z * self.speed

        # Apply acceleration or friction
        if input_dir.x != 0:
            self.velocity.x = lerp(self.velocity.x, target_x, self.acceleration * dt)
        else:
            self.velocity.x = lerp(self.velocity.x, 0, self.friction * dt)

        if input_dir.z != 0:
            self.velocity.z = lerp(self.velocity.z, target_z, self.acceleration * dt)
        else:
            self.velocity.z = lerp(self.velocity.z, 0, self.friction * dt)

        # --- Gravity ---
        self.velocity.y -= self.gravity * dt

        # --- Move and resolve collisions ---
        self.position += self.velocity * dt

        # --- Ground check (raycast downward) ---
        ray = raycast(
            self.world_position + Vec3(0, 0.1, 0),  # slightly above feet
            direction=Vec3(0, -1, 0),
            distance=1.2,                            # half height + small buffer
            ignore=[self],
            debug=True
        )

        if ray.hit:
            # Snap to ground and reset vertical velocity
            if self.velocity.y < 0:
                self.velocity.y = 0
                self.y = ray.world_point.y + 1   # half player height
            self.grounded = True
        else:
            self.grounded = False

    def input(self, key):
        if key == 'space' and self.grounded:
            self.velocity.y = self.jump_force


if __name__ == '__main__':
    # window.vsync = False
    app = Ursina()
    camera.orthographic = True
    camera.fov = 10

    ground = Entity(model='cube', color=color.white33, origin_y=.5, scale=(20, 1, 1), collider='box', y=-1)
    wall = Entity(model='cube', color=color.azure, origin=(-.5,.5), scale=(5,10), x=10, y=.5, collider='box')
    wall_2 = Entity(model='cube', color=color.white33, origin=(-.5,.5), scale=(5,10), x=10, y=0, collider='box')
    ceiling = Entity(model='cube', color=color.white33, origin_y=-.5, scale=(1, 1, 1), y=1, collider='box')
    ceiling = Entity(model='cube', color=color.white33, origin_y=-.5, scale=(5, 5, 1), y=2, collider='box')
    ground = Entity(model='cube', color=color.white33, origin_y=.5, scale=(20, 3, 1), collider='box', y=-1, rotation_z=45, x=-5)


    player_controller = Player(x=3, y=20, scale_y = 2)
    ec = EditorCamera()
    ec.add_script(SmoothFollow(target=player_controller, offset=[0,1,0], speed=4))

    app.run()