import pygame
import sys
from scripts.utils import load_image
from scripts.Entities import PhysicsEntity, FlyingEntity



class Player:
    def __init__(self, game, pos, size):
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.speed = 5
        self.gravity = 0.5
        self.jump_speed = -12
        self.on_ground = False
        self.direction = 1  # 1 for right, -1 for left

        self.frames = game.assets['PlayerFrames']
        self.idle_frame = self.frames[0]
        self.walk_frames = self.frames[4:8]
        self.punch_frames = self.frames[1:4]
        self.uppercut_frames = self.frames[8:11]

        self.action = 'idle'
        self.frame_index = 0
        self.frame_timer = 0
        self.animation_speed = 0.2
        self.flipped = False

        self.image = pygame.transform.scale(self.idle_frame, self.size)
        self.ground_level = 790 - self.size[1]

    def update(self, keys, mouse_buttons):
        self.velocity[0] = 0

        if keys[pygame.K_a]:
            self.velocity[0] = -self.speed
            self.direction = -1
        elif keys[pygame.K_d]:
            self.velocity[0] = self.speed
            self.direction = 1

        if keys[pygame.K_w] and self.on_ground:
            self.velocity[1] = self.jump_speed
            self.on_ground = False

        if mouse_buttons[0]:  # Left click
            self.action = 'punch'
            self.frame_index = 0
        elif keys[pygame.K_x]:
            self.action = 'uppercut'
            self.frame_index = 0
        elif self.velocity[0] != 0:
            self.action = 'walk'
        else:
            self.action = 'idle'

        self.velocity[1] += self.gravity
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # Ground collision
        if self.pos[1] >= self.ground_level:
            self.pos[1] = self.ground_level
            self.velocity[1] = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Update image
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index += 1

        if self.action == 'walk':
            frames = self.walk_frames
        elif self.action == 'punch':
            frames = self.punch_frames
        elif self.action == 'uppercut':
            frames = self.uppercut_frames
        else:
            frames = [self.idle_frame]

        if self.frame_index >= len(frames):
            if self.action in ['punch', 'uppercut']:
                self.action = 'idle'
            self.frame_index = 0

        current_frame = pygame.transform.scale(frames[self.frame_index], self.size)
        self.image = pygame.transform.flip(current_frame, True, False) if self.direction == -1 else current_frame

    def render(self, surf):
        surf.blit(self.image, self.pos)


class Game:
    def __init__(self):
        pygame.init()
        self.explosions = []
        pygame.display.set_caption('CT GAME')
        self.screen = pygame.display.set_mode((1400, 800))
        self.clock = pygame.time.Clock()

        background_image = load_image('Background', 'DarkForestPixelated.png')
        self.background = pygame.transform.scale(background_image, (1400, 800))

        self.assets = {
            'NormalGoblin': load_image('NormalGoblin', 'NormalGoblin2.png'),
            'Fireball': load_image('Fireball', 'fireball.png'),
        }

        self.goblin1 = PhysicsEntity(self, 'NormalGoblin', (100, 50), (70, 70))
        self.goblin2 = PhysicsEntity(self, 'NormalGoblin', (400, 50), (70, 70))
        self.goblin2.walk_speed = 1
        self.goblin3 = PhysicsEntity(self, 'NormalGoblin', (700, 50), (80, 80))
        self.goblins = [self.goblin1, self.goblin2, self.goblin3]

        self.assets['RedDragonFrames'] = [
            load_image('RedDragon', 'dragontile003Fly1.png'),
            load_image('RedDragon', 'dragontile004Fly2.png'),
            load_image('RedDragon', 'dragontile005Fly3.png')
        ]
        self.assets['RedDragonFrames_b'] = [
            load_image('RedDragon', 'dragontile009Fly3b.png'),
            load_image('RedDragon', 'dragontile010Fly2b.png'),
            load_image('RedDragon', 'dragontile011Fly3b.png')
        ]

        self.dragon = FlyingEntity(self, 'RedDragon', (600, 455), (240, 210))

        self.assets['PlayerFrames'] = [
            load_image('player', 'ELF_HOBORY.png'),         # idle
            load_image('player', 'Hobory_punch1.png'),      # punch 1
            load_image('player', 'Hobory_punch2.png'),      # punch 2
            load_image('player', 'Hobory_punch3.png'),      # punch 3
            load_image('player', 'Hobory_walk-1.png'),      # walk 1
            load_image('player', 'Hobory_walk-2.png'),      # walk 2
            load_image('player', 'Hobory_walk-3.png'),      # walk 3
            load_image('player', 'Hobory_walk-4.png'),      # walk 4
            load_image('player', 'Uppercut_1.png'),         # uppercut 1
            load_image('player', 'Uppercut_2.png'),         # uppercut 2
            load_image('player', 'Uppercut_3.png'),         # uppercut 3
        ]

        self.player = Player(self, (300, 300), (100, 120))

    def run(self):
        while True:
            self.screen.blit(self.background, (0, 0))

            for goblin in self.goblins:
                goblin.update_automated()
                goblin.render(self.screen)

            self.dragon.update_automated()
            self.dragon.render(self.screen)

            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            self.player.update(keys, mouse_buttons)
            self.player.render(self.screen)

            for explosion in self.explosions[:]:
                explosion.update()
                explosion.render(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()