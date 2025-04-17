import pygame
import random

# Initialize pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("Blade of the Fallen")

# Load images
character_idle = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/idle/ELF_HOBORY.png")
walk1 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/run/Hobory_walk-1.png")
walk2 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/run/Hobory_walk-2.png")
walk3 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/run/Hobory_walk-3.png")
walk4 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/run/Hobory_walk-4.png")
#walkb1 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/Hobory_walkb-1.png")
#walkb2 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/Hobory_walkb-2.png")
#walkb3 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/Hobory_walkb-3.png")
#walkb4 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/Hobory_walkb-4.png")
punch1 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/punch/Hobory_punch1.png")
punch2 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/punch/Hobory_punch2.png")
punch3 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/punch/Hobory_punch3.png")
uppercut1 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/uppercut/Uppercut_1.png")
uppercut2 = pygame.image.load(r"C:\Users\Arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/uppercut/Uppercut_2.png")
uppercut3 = pygame.image.load(r"C:\Users\arjun\PycharmProjects\pythonPygame\NewVersCT/data/images/entities/player/uppercut/Uppercut_3.png")

# Resize images
character_idle = pygame.transform.scale(character_idle, (100, 160))
background_img = pygame.transform.scale(background_img, (1400, 850))
background_img2 = background_img.copy()
walk_frames_forward = [pygame.transform.scale(img, (120, 160)) for img in [walk1, walk2, walk3, walk4]]
walk_frames_backward = [pygame.transform.scale(img, (120, 160)) for img in [walkb1, walkb2, walkb3, walkb4]]
punch_frames = [pygame.transform.scale(img, (270, 180)) for img in [punch1, punch2, punch3]]
uppercut_frames = [pygame.transform.scale(img, (190, 150)) for img in [uppercut1, uppercut2, uppercut3]]

# Character and physics parameters
x, y = 100, 635
x_b = 0
width, height = 100, 160
vel = 3.85
gravity = 1
jump_strength = 18
y_velocity = 0
on_ground = True
was_on_ground = True
jump_count = 0
jump_key_released = True

# Particle systems
particles = []
double_jump_particles = []

# Animation parameters
walk_frame = walk_timer = punch_frame = punch_timer = uppercut_frame = uppercut_timer = 0
punch_delay, uppercut_delay, walk_delay = 85, 125, 120
moving_right = moving_left = False

# Control flags
uppercut_queue, punch_queue = [], []
uppercut = punching = False
uppercut_animation_done = punch_animation_done = True

# Clock
clock = pygame.time.Clock()
GROUND_Y = 635

# Game loop
running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k and punch_animation_done:
                punch_queue.append(True)
                punch_animation_done = False
                punch_frame = 0
            if event.key == pygame.K_l and uppercut_animation_done:
                uppercut_queue.append(True)
                uppercut_animation_done = False
                uppercut_frame = 0

    keys = pygame.key.get_pressed()
    moving = False

    if keys[pygame.K_a] and x > vel:
        x -= vel
        moving = True
    if keys[pygame.K_d] and x < 200 - width - vel:
        x += vel
        moving = True

    # Double punch logic
    if keys[pygame.K_w]:
        if jump_key_released:
            if on_ground:
                y_velocity = -jump_strength
                jump_count = 1
                on_ground = False
                jump_key_released = False
            elif jump_count == 1:
                y_velocity = -jump_strength
                jump_count += 1
                jump_key_released = False
                # Puff effect for second punch
                for _ in range(30):
                    double_jump_particles.append([
                        x + width // 2, y + height - 10,
                        random.uniform(-6, 6), random.uniform(-8, -3),
                        random.uniform(6, 10)

                    ])
    else:
        jump_key_released = True

    # Apply gravity
    y_velocity += gravity
    y += y_velocity

    # Ground collision
    if y >= GROUND_Y:
        y = GROUND_Y
        y_velocity = 0
        on_ground = True
        jump_count = 0
    else:
        on_ground = False

    # Landing dust
    if on_ground and not was_on_ground:
        for _ in range(20):
            particles.append([
                x + width // 2, GROUND_Y + height - 10,
                random.randint(-5, 5), random.randint(-10, -2),
                random.randint(4, 6)
            ])
    was_on_ground = on_ground


    # Animations
    if uppercut_queue:
        uppercut = True
        uppercut_timer += dt
        if uppercut_timer >= uppercut_delay:
            uppercut_timer = 0
            uppercut_frame += 1
            if uppercut_frame >= len(uppercut_frames):
                uppercut_frame = 0
                uppercut_queue.pop(0)
                if not uppercut_queue:
                    uppercut_animation_done = True
                uppercut = False
        current_img = uppercut_frames[uppercut_frame]

    elif punch_queue:
        punching = True
        punch_timer += dt
        if punch_timer >= punch_delay:
            punch_timer = 0
            punch_frame += 1
            if punch_frame >= len(punch_frames):
                punch_frame = 0
                punch_queue.pop(0)
                if not punch_queue:
                    punch_animation_done = True
                punching = False
        current_img = punch_frames[punch_frame]

    elif keys[pygame.K_d]:
        walk_timer += dt
        if walk_timer >= walk_delay:
            walk_timer = 0
            walk_frame = (walk_frame + 1) % len(walk_frames_forward)
        current_img = walk_frames_forward[walk_frame]

    elif keys[pygame.K_a]:
        walk_timer += dt
        if walk_timer >= walk_delay:
            walk_timer = 0
            walk_frame = (walk_frame + 1) % len(walk_frames_backward)
        current_img = walk_frames_backward[walk_frame]

    else:
        current_img = character_idle
        walk_frame = 0

    # Background scroll
    if keys[pygame.K_d] and x > 100 - width - vel:
        x_b -= vel
    screen.blit(background_img, (x_b % -1400, 0))
    screen.blit(background_img2, (1400 + x_b % -1400, 0))

    # Draw particles
    for p in particles + double_jump_particles:
        pygame.draw.circle(screen, (150, 150, 150), (int(p[0]), int(p[1])), int(p[4]))

    # Draw character
    if punching or uppercut:
        screen.blit(current_img, (x - 15, y))
    else:
        screen.blit(current_img, (x, y))

    pygame.display.update()

pygame.quit()