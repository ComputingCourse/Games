import pygame, random
from pygame.math import Vector2 as vector
SCREEN_WIDTH, SCREEN_HEIGHT = 1280,720
TILE_SIZE = 64
ANIMATION_SPEED = 5

ORDERS = {
    "sky": 0,
    "bg": 1,
    "main": 2,
    "player":3,
    "dog":4,
    "fg": 5,
    "water": 6
    
    }
