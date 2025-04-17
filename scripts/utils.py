import pygame
import os

def load_image(entity_name, filename):
    # Check if it's a background image
    if entity_name == 'Background':
        base_path = os.path.join('data', 'images', 'Background')
    else:
        base_path = os.path.join('data', 'images', 'entities', entity_name)

    full_path = os.path.join(base_path, filename)

    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"Could not find image: {full_path}")

    # Load image with alpha transparency support
    image = pygame.image.load(full_path).convert_alpha()
    return image