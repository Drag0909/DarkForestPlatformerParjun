import pygame
import os
import random

# Dust particle class
class Particle:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.size = random.randint(2, 4)
        self.life = random.randint(8, 15)
        self.velocity = [random.randint(-2, 2), random.randint(-4, -1)]
        self.alpha = 255

    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.velocity[1] += 0.1
        self.life -= 1
        self.alpha = max(self.alpha - 20, 0)

    def render(self, surf):
        if self.life > 0:
            particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (150, 150, 150, self.alpha), (self.size, self.size), self.size)
            surf.blit(particle_surf, (self.pos[0] - self.size, self.pos[1] - self.size))

# Goblin with physics
class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.gravity = 0.5
        self.jump_speed = -8
        self.ground_level = 790 - self.size[1]
        self.on_ground = True
        self.jumping = False
        self.health = 100
        self.particles = []

        self.direction = random.choice([-1, 1])
        self.walk_speed = random.randint(1, 4)
        self.jump_frequency = random.uniform(0.01, 0.05)

        self.image = pygame.transform.scale(self.game.assets[self.type], self.size)
        self.original_image = self.image
        self.flipped = False

    def spawn_landing_particles(self):
        for _ in range(8):
            px = self.pos[0] + self.size[0] // 2 + random.randint(-10, 10)
            py = self.pos[1] + self.size[1] - 5
            self.particles.append(Particle(px, py))

    def update_automated(self):
        self.pos[0] += self.direction * self.walk_speed

        if self.pos[0] < 0:
            self.pos[0] = 0
            self.direction = 1
        elif self.pos[0] + self.size[0] > 1400:
            self.pos[0] = 1400 - self.size[0]
            self.direction = -1

        if self.direction == -1 and not self.flipped:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.flipped = True
        elif self.direction == 1 and self.flipped:
            self.image = self.original_image
            self.flipped = False

        if random.random() < self.jump_frequency and self.on_ground:
            self.velocity[1] = self.jump_speed
            self.on_ground = False
            self.jumping = True

        self.velocity[1] += self.gravity
        self.pos[1] += self.velocity[1]

        if self.pos[1] >= self.ground_level:
            if not self.on_ground:
                self.on_ground = True
                self.pos[1] = self.ground_level
                self.velocity[1] = 0
                self.jumping = False
                self.spawn_landing_particles()
            else:
                self.pos[1] = self.ground_level
                self.velocity[1] = 0
        else:
            self.on_ground = False

        if random.random() < 0.01:
            self.direction = random.choice([-1, 1])

        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def render(self, surf):
        surf.blit(self.image, self.pos)
        for particle in self.particles:
            particle.render(surf)

# Dragon entity
class FlyingEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.direction = 1
        self.speed = 2
        self.frame_index = 0
        self.frame_timer = 0
        self.animation_speed = 0.15
        self.fireball_timer = 0
        self.fireball_frequency = 150

        self.frames = [pygame.transform.scale(img, size) for img in self.game.assets[self.type + 'Frames']]
        self.frames_b = [pygame.transform.scale(img, size) for img in self.game.assets[self.type + 'Frames_b']]
        self.current_frames = self.frames

        self.fireballs = []

    def update_automated(self):
        self.pos[0] += self.direction * self.speed

        # Bounce off screen edges
        if self.pos[0] <= 0:
            self.pos[0] = 0
            self.direction = 1
        elif self.pos[0] + self.size[0] >= 1400:
            self.pos[0] = 1400 - self.size[0]
            self.direction = -1

        # Fireball launching
        self.fireball_timer += 1
        if self.fireball_timer > self.fireball_frequency:
            self.fireball_timer = 0
            fireball_pos = (self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2)
            fireball = Fireball(self.game, fireball_pos, self.direction)
            self.fireballs.append(fireball)

        for fireball in self.fireballs[:]:
            fireball.update()
            if fireball.exploded:
                self.fireballs.remove(fireball)

        self.current_frames = self.frames if self.direction == 1 else self.frames_b

        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)

    def render(self, surf):
        surf.blit(self.current_frames[self.frame_index], self.pos)
        for fireball in self.fireballs:
            fireball.render(surf)

# Fireball
# Fireball
class Fireball:
    def __init__(self, game, dragon_pos, direction, speed=5):
        self.game = game
        self.pos = list(dragon_pos)
        self.direction = direction
        self.speed = speed
        self.size = (30, 30)
        self.image = pygame.transform.scale(self.game.assets['Fireball'], self.size)
        self.exploded = False

    def update(self):
        if not self.exploded:
            self.pos[0] += self.direction * self.speed

            # Explode if off-screen
            if self.pos[0] < 0 or self.pos[0] > 1400:
                self.explode()
                return

            # Check collision with goblins
            for goblin in self.game.goblins:
                if goblin.pos[0] < self.pos[0] < goblin.pos[0] + goblin.size[0] and \
                   goblin.pos[1] < self.pos[1] < goblin.pos[1] + goblin.size[1]:
                    self.explode(goblin)
                    break

    def render(self, surf):
        if not self.exploded:
            surf.blit(self.image, self.pos)

    def explode(self, target=None):
        self.exploded = True
        explosion = Explosion(self.game, self.pos)
        self.game.explosions.append(explosion)

        if target:
            target.health -= 20

# Explosion visual
class Explosion:
    def __init__(self, game, pos):
        self.game = game
        self.pos = pos
        self.size = (50, 50)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 69, 0), (self.size[0] // 2, self.size[1] // 2), 25)
        self.life = 10

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.game.explosions.remove(self)

    def render(self, surf):
        surf.blit(self.image, self.pos)

# Player class
class Player:
    def __init__(self, game, pos, size):
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.vel = [0, 0]
        self.on_ground = False
        self.gravity = 0.5
        self.jump_strength = -10

        self.animations = {
            'idle': [self.game.assets['PlayerFrames'][0]],
            'punch': self.game.assets['PlayerFrames'][1:4],
            'walk': self.game.assets['PlayerFrames'][4:8],
            'uppercut': self.game.assets['PlayerFrames'][8:11]
        }

        self.state = 'idle'
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.15
        self.flipped = False

        self.jumping = False
        self.attack_cooldown = 0
        self.particles = []

        # Inputs for attack
        self.punch_requested = False
        self.uppercut_requested = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.punch_requested = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_x:
            self.uppercut_requested = True

    def update(self, keys, mouse_pressed):
        speed = 4
        dx = 0

        if keys[pygame.K_a]:
            dx -= speed
            self.flipped = True
        elif keys[pygame.K_d]:
            dx += speed
            self.flipped = False

        self.pos[0] += dx

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel[1] = self.jump_strength
            self.on_ground = False

        # Apply gravity
        self.vel[1] += self.gravity
        self.pos[1] += self.vel[1]

        # Floor collision
        if self.pos[1] + self.size[1] >= 790:
            self.pos[1] = 790 - self.size[1]
            self.vel[1] = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Determine state
        if self.state not in ['punch', 'uppercut']:  # Don’t interrupt attacks
            if dx != 0:
                self.state = 'walk'
            else:
                self.state = 'idle'

        # Handle punch or uppercut if requested
        if self.punch_requested and self.state not in ['punch', 'uppercut']:
            self.state = 'punch'
            self.anim_index = 0
            self.anim_timer = 0
            self.spawn_particles()
            self.punch_requested = False

        if self.uppercut_requested and self.state not in ['punch', 'uppercut']:
            self.state = 'uppercut'
            self.anim_index = 0
            self.anim_timer = 0
            self.spawn_particles()
            self.uppercut_requested = False

        # Animate
        self.anim_timer += self.anim_speed
        if self.anim_timer >= 1:
            self.anim_timer = 0
            self.anim_index += 1
            if self.anim_index >= len(self.animations[self.state]):
                self.anim_index = 0
                if self.state in ['punch', 'uppercut']:
                    self.state = 'idle'

        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def spawn_particles(self):
        for _ in range(8):
            px = self.pos[0] + self.size[0] // 2 + random.randint(-10, 10)
            py = self.pos[1] + self.size[1] // 2 + random.randint(-5, 5)
            self.particles.append(Particle(px, py))

    def render(self, surf):
        frame = self.animations[self.state][self.anim_index]
        img = pygame.transform.scale(frame, self.size)
        if self.flipped:
            img = pygame.transform.flip(img, True, False)
        surf.blit(img, self.pos)

        for p in self.particles:
            p.render(surf)