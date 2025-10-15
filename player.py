from settings import *
from pygame.math import Vector2 as vector
from timer import Timer
from sprites import Particle_effect
from math import sin

class Player(pygame.sprite.Sprite):
    def __init__(self,pos, frames,jump_frames, groups, sprites,Data):
        '''sets the player rects and other important variables'''
        super().__init__(groups)
        #setup
        self.image = frames["idle"][0]
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-76,-36)
        self.all_sprites = groups
        
        self.order = ORDERS["player"]
        self.collision_sprites = sprites[0]
        self.semi_collision_sprites = sprites[1]
        self.moving_platforms = sprites[2]
        self.enemy_sprites = sprites[3]
        self.Data = Data
        
        #movement
        self.direction = vector()
        self.gravity = 1500
        self.speed = 400
        self.jump = False
        self.jump_strength = 800
        self.double_jumped= False
        self.jump_frames = jump_frames

        self.use_ability = False

        #animation
        self.state = "idle"
        self.facing_right = True
        self.attacking = False
        self.frames,self.frame_index = frames,0

        #collisions
        self.touching = {"floor":False,"wall_left":False,"wall_right":False}
        self.platform = None
        self.timers = {
            "jump":  Timer(250),
            "wall jump": Timer(200),
            "platform fall":Timer(250),
            "hit": Timer(1000),
            "attack": Timer(500),
            "shield": Timer(100000)
            }
        self.timers["jump"].activate() # so they don't jump as they enter
        
    def input(self):
        '''checks for any inputs'''
        keys = pygame.key.get_pressed()
        input_vector = vector()
        if not self.timers["wall jump"].active:
            if keys[pygame.K_d]:
                input_vector.x +=1
                self.facing_right = True
            if keys[pygame.K_a]:
                input_vector.x -=1
                self.facing_right = False
            if keys[pygame.K_s]:
                self.timers["platform fall"].activate()
            self.direction.x = input_vector.normalize().x if input_vector else 0
            if pygame.mouse.get_pressed()[0]:
                if not self.timers["attack"].active:
                    self.attacking = True
                    self.timers["attack"].activate()
        if keys[pygame.K_SPACE]:
            self.jump = True if not self.timers["jump"].active else False
        

    def move(self, dt):
        '''applies gravity and moves the player in the right direction'''
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision("x")
        if any((self.touching["wall_left"], self.touching["wall_right"])) and not self.touching["floor"] and not self.timers["jump"].active:
            self.direction.y = 0 if not self.timers["wall jump"].active else self.direction.y
            self.hitbox_rect.y += self.gravity/10 * dt
        elif self.platform and self.direction.y >= 0 and not self.timers["platform fall"].active:
            self.direction.y = 0
        else:
            self.direction.y += self.gravity/2 *dt
            self.hitbox_rect.y += self.direction.y *dt
            self.direction.y += self.gravity/2 * dt
        
        if (self.touching["wall_left"] or self.touching["wall_right"] or self.touching["floor"]):
            self.double_jumped = False

        if self.jump:
            if self.touching["floor"]:
                self.timers["jump"].activate()
                self.direction.y = -self.jump_strength
                self.hitbox_rect.bottom -=1
                Particle_effect(self.hitbox_rect.bottomleft -vector(0,7), self.jump_frames, self.all_sprites,12)
            elif not self.touching["floor"] and (self.touching["wall_left"] or self.touching["wall_right"]) and not (self.timers["wall jump"].active or self.timers["jump"].active):
                self.timers["wall jump"].activate()
                self.direction.x = 1 if self.touching["wall_left"] else -1
                self.direction.y = -self.jump_strength
            elif not self.double_jumped and not self.timers["wall jump"].active and not self.timers["jump"].active:
                self.direction.y = -self.jump_strength
                self.double_jumped = True
                Particle_effect(self.hitbox_rect.bottomleft -vector(0,7), self.jump_frames, self.all_sprites,12)
            self.jump = False

        self.collision("y")
        self.semi_collision()
        self.rect.center = self.hitbox_rect.center
        
    def check_contact(self):
        '''sees if the player is touching anything and changes the required variables'''
        floor_rect = pygame.FRect((self.hitbox_rect.bottomleft),(self.hitbox_rect.width,2))
        right_rect = pygame.FRect((self.hitbox_rect.topright + vector(0,self.hitbox_rect.height/4)),(2,self.hitbox_rect.height/2))
        left_rect = pygame.FRect((self.hitbox_rect.topleft+vector(-2,self.hitbox_rect.height/4)),(2,self.hitbox_rect.height/2))

        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rects = [sprite.rect for sprite in self.semi_collision_sprites]
        platforms = [sprite.rect for sprite in self.moving_platforms]
        self.touching["floor"] = True if floor_rect.collidelist(collide_rects+semi_collide_rects) !=-1 else False
        self.touching["wall_left"] = True if left_rect.collidelist(collide_rects) !=-1 else False
        self.touching["wall_right"] = True if right_rect.collidelist(collide_rects) !=-1 else False
        index = floor_rect.collidelist(platforms)
        platform = self.platform
        self.platform = self.moving_platforms.sprites()[index] if index != -1 else None

        #screen = pygame.display.get_surface()
        #pygame.draw.rect(screen,"yellow",right_rect)

    def collision(self, axis):
        '''sees if the player is colliding with something and makes sure it doesnt go through it'''
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == "x":
                    #left
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.rect.right):
                        self.hitbox_rect.left = sprite.rect.right

                    #right
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                elif axis == "y":
                    #top
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        self.direction.y = 0

                    #bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                        self.direction.y = 0

    def semi_collision(self):
        '''checks for collitions with semi-collidible and allows you to fall through them'''
        if not self.timers["platform fall"].active:
            for sprite in self.semi_collision_sprites:
                if self.hitbox_rect.colliderect(sprite.rect):
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.rect.top) and self.direction.y >=0:
                        self.hitbox_rect.bottom = sprite.rect.top
                        self.direction.y = 0


    def platform_collision(self, dt):
        '''moves you if your on a moving platform'''
        if self.platform:
            if self.platform.direction == "x":
                self.hitbox_rect.x += self.platform.speed * dt
            else:
                self.hitbox_rect.y += self.platform.speed * dt

    def check_damage(self):
        '''sees if you should take damage (or have blocked it)'''
        if self.state == "attack":
            if self.facing_right:
                sword_hitbox = pygame.Rect((self.hitbox_rect.topright),(25,60))
            else:
                sword_hitbox = pygame.Rect((self.hitbox_rect.topleft)-vector(25,0),(25,60))
        elif self.state == "air_attack":
            sword_hitbox = pygame.Rect((self.hitbox_rect.bottomleft),(34,30))
        else:
            sword_hitbox = pygame.Rect((0,0),(0,0))

        for sprite in self.enemy_sprites:
            if sword_hitbox.colliderect(sprite.rect) and hasattr(sprite, "destructible"):
                sprite.die()
            elif sword_hitbox.colliderect(sprite.rect) and hasattr(sprite, "deflectable"):
                sprite.deflect()
            elif self.hitbox_rect.colliderect(sprite.rect):
                self.get_damage()
                if hasattr(sprite, "destructible"):
                    sprite.die()

    def get_damage(self):
        '''decreases players health it they haven't been hit recently'''
        if self.timers["shield"].active:
            self.timers["shield"].deactivate()
            self.timers["hit"].activate()
        elif not self.timers["hit"].active:
            self.Data.lose_health()
            self.timers["hit"].activate()

    def flicker(self):
        '''makes the player flash white to so that they've taken damage and are nw invulnerable'''
        if self.timers['hit'].active and sin(self.timers['hit'].time) >= 0:
            white_mask = pygame.mask.from_surface(self.image)
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

            

    def get_state(self):
        '''finds out what state the player is in e.g falling'''
        if self.touching["floor"] and self.direction.y>=0:
            self.state = "idle" if self.direction.x == 0 else "run"
            if self.attacking:
                self.state = "attack"
        else:
            if any((self.touching["wall_right"],self.touching["wall_left"])):
                self.state = "wall"
            else:
                self.state = "jump" if self.direction.y <0 else "fall"
                if self.attacking:
                    self.state = "air_attack"


    def animate(self,dt):
        '''draws the animations for the player'''
        state = self.state
        self.get_state()
        if state != self.state and not(self.state[-1] == "k" and state[-1] == "k"):
            #dont set index = 0 if it's changing type of attack
            self.frame_index = 0
        elif int(self.frame_index)>= len(self.frames[self.state]):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
                self.get_state()
        
        self.image = self.frames[self.state][int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image,True,False)
        self.frame_index += dt * ANIMATION_SPEED
        
    def update(self,dt):
        '''calls all the methods and updates the timers'''
        self.old_rect = self.hitbox_rect.copy()
        self.input()
        self.platform_collision(dt)
        self.move(dt)
        self.check_contact()
        self.animate(dt)
        self.flicker()
        self.check_damage()
        
        for timer in self.timers.values():
            timer.update_dt(dt)
