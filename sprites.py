from settings import *
from random import randint
from timer import Timer
import math

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, order = ORDERS["main"]):
        '''joins the sprite group and sets a rect and image'''
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.order = order
        
class Path(Sprite):
    def __init__(self, pos, surf, groups, name):
        '''runs sprite.init and sets a name'''
        super().__init__(pos, surf, groups, ORDERS["bg"])
        self.name = name

class Animated_sprite(Sprite):
    def __init__(self, pos, frames, groups,animation_speed, order = ORDERS["main"]):
        '''sets animation related variables'''
        super().__init__(pos,frames[0],groups,order)
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = animation_speed

    def animate(self,dt):
        '''cycles through the frames'''
        self.frame_index += self.animation_speed * dt
        if int(self.frame_index) >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self,dt):
        '''calls animate method'''
        self.animate(dt)

class Moving_sprite(Animated_sprite):
    def __init__(self,pos,width,height,frames,groups,speed = 50,animation_speed = 6, order = ORDERS["main"],flip = False):
        '''calculates start pos and creates sets other important attributes'''
        super().__init__(pos,frames,groups,animation_speed, order)
        self.flip = flip
        self.start_pos  = pos
        self.width = width
        self.height = height
        if self.width > self.height:
            self.start_pos += vector(0,self.height/2)
            self.rect.center = self.start_pos
        else:
            self.start_pos += vector(self.width/2,0)
            self.rect.center = self.start_pos
        self.speed = speed
        self.direction = "x" if width>height else "y"

    def flip_frames(self,x=False,y=False):
        '''flips the frames about the y axis'''
        if self.flip:
            self.frames = [pygame.transform.flip(frame,x,y) for frame in self.frames]

    def update(self,dt):
        '''moves the sprite and flips its direction if needed'''
        #moving
        if self.direction == "x":
            self.rect.x += self.speed * dt
            #check to see if it should turn around
            if self.rect.centerx < self.start_pos[0]:
                self.rect.center = self.start_pos
                self.speed *=-1
                self.flip_frames(True)
            elif self.rect.centerx > (self.start_pos[0] + self.width):
                self.rect.center = self.start_pos + vector(self.width,0)
                self.speed *=-1
                self.flip_frames(True)
        else:
            self.rect.y += self.speed * dt
            if self.rect.centery < self.start_pos[1]:
                self.rect.center = self.start_pos
                self.speed *= -1
                self.flip_frames(False,True)
            elif self.rect.centery > (self.start_pos[1] + self.height):
                self.rect.center = self.start_pos + vector(0,self.height)
                self.speed *= -1
                self.flip_frames(False,True)

        #Animate
        self.animate(dt)

class Spiked_ball(Sprite):
    def __init__(self,pos,ball_image,chain,start_angle,end_angle,radius,speed,groups,order = ORDERS["main"]):
        '''set start point and other attributes'''
        super().__init__(pos,ball_image,groups,order)
        self.center = pos + vector(self.rect.width/2,self.rect.height/2)
        self.angle = start_angle
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.radius = radius
        self.speed = speed
        self.chain_image = chain
        self.all_sprites = groups[0]
        
        self.rect.centerx =  self.center[0] + self.radius * math.cos(math.radians(self.angle))
        self.rect.centery =  self.center[1] - self.radius * math.sin(math.radians(self.angle))
        self.chain = pygame.sprite.Group()
        self.draw_chain()

    def draw_chain(self):
        '''draws chains every 20 pixel from the center'''
        for chain in self.chain:
            chain.kill()

        for radius in range(10,self.radius-20,20):
            x =  self.center[0] + radius * math.cos(math.radians(self.angle))
            y =  self.center[1] + radius * math.sin(math.radians(self.angle))
            Sprite((x,y),self.chain_image,(self.all_sprites,self.chain),order = ORDERS["bg"])
            
    def update(self,dt):
        '''uses trig to draw the ball traversing an arc'''
        if self.angle >= self.end_angle:
            self.speed *=-1
            self.angle = self.end_angle
        elif self.angle <= self.start_angle:
            self.speed *=-1
            self.angle = self.start_angle
        self.angle += dt * self.speed
        
        self.rect.centerx =  self.center[0] + self.radius * math.cos(math.radians(self.angle))
        self.rect.centery =  self.center[1] + self.radius * math.sin(math.radians(self.angle))
        self.draw_chain()
        


                         
class Tooth(Animated_sprite):
    def __init__(self,pos, frames, groups,collision_sprites, animation_speed = random.uniform(4,6), order = ORDERS["main"]):
        '''inherits from the animated sprite class and sets other attributes'''
        super().__init__(pos,frames,groups,animation_speed,order)
        self.pos = pos
        self.frames_right = frames
        self.frames_left = [pygame.transform.flip(frame,True,False) for frame in frames]
        self.speed = 60
        self.direction = 1
        self.collision_sprites = collision_sprites
        self.deflectable = True
        self.deflected = Timer(500)

    def move(self,dt):
        '''moves them and turns them around if needed'''
        right_rect = pygame.FRect((self.rect.topright),(5,self.rect.height-5))
        left_rect = pygame.FRect((self.rect.topleft-vector(5,0)),(5,self.rect.height-5))
        bottom_right = pygame.FRect((self.rect.bottomright),(5,5))
        bottom_left = pygame.FRect((self.rect.bottomleft-vector(5,0)),(5,5))

        collisions = [sprite.rect for sprite in self.collision_sprites]
        if right_rect.collidelist(collisions) != -1 or bottom_right.collidelist(collisions) == -1:
            self.direction = -1 # turn them around
        if left_rect.collidelist(collisions) != -1 or bottom_left.collidelist(collisions) == -1:
            self.direction = 1

        self.rect.x += self.direction * dt * self.speed

    def deflect(self):
        if not self.deflected.active:
            self.direction *= -1
            self.deflected.activate()

    def update(self,dt):
        self.deflected.update()
        self.move(dt)
        if self.direction ==1:
            self.frames = self.frames_right
        else:
            self.frames = self.frames_left
        self.animate(dt)
            
class Clam(Animated_sprite):
    def __init__(self,pos,frames,pearl_image,groups,enemies,player_rect,inverted,partice_frames,order = ORDERS["main"]):
        super().__init__(pos,frames["idle"],groups,6,order)
        self.pos = pos
        self.frames = frames
        self.player = player_rect
        self.inverted = inverted
        if self.inverted:
            self.frames = self.flip_frames()
        self.shooting = False
        self.wait_timer = Timer(3000)
        
        self.pearl_image = pearl_image
        self.enemy_sprites = enemies # enemy sprite group  to the pearl can also be in the group
        self.collision_sprites = groups[1]
        self.all_sprites = groups[0]
        self.particle_frames = partice_frames

    def see_player(self):
        '''sees if the player is in the clam's view'''
        if self.inverted:
            if self.player.right >= self.pos[0] -500 and self.player.right < self.pos[0]:
                if (self.player.center[1]-self.pos[1])**2 <= (self.player.height/2)**2:
                    return True

        else:   
            if self.player.left <= self.pos[0] +576 and self.player.left > self.pos[0]+76:#76 is pixel width of the clam
                if (self.player.center[1]-self.pos[1])**2 <= (self.player.height/2)**2:
                    return True
        return False

    def flip_frames(self):
        '''flips the frames along the vertical axis if the clam is facing the other way'''
        frames = {}
        frames["fire"] = [pygame.transform.flip(frame,True,False) for frame in self.frames["fire"]]
        frames["idle"] = [pygame.transform.flip(frame,True,False) for frame in self.frames["idle"]]
        return frames
                               
        
    def update(self,dt):
        '''updates the Clam : shoots a pearl and animates when neccessary'''
        if self.see_player() and not self.shooting and not self.wait_timer.active:
            self.shooting = True
            self.wait_timer.activate()
            direction = -1 if self.inverted ==True else 1
            Pearl(self.pos,direction,self.pearl_image,(self.enemy_sprites,self.all_sprites),self.collision_sprites,self.player,self.rect,self.particle_frames)#creates and shoots a pearl
        if self.shooting:
            self.frame_index += dt * self.animation_speed
            if int(self.frame_index) >= len(self.frames["fire"]):
                self.frame_index = 0
                self.shooting = False
            else:
                self.image = self.frames["fire"][int(self.frame_index)]
        else:
            self.image = self.frames["idle"][0]
        self.wait_timer.update()


class Pearl(Sprite):
    def __init__(self,pos,direction,image,groups,collision_sprites,player,clam,particle_frames):
        '''creates a pearl at the mouth of the clam and sets other imortant attributes'''
        self.clam_rect = clam
        self.direction = direction
        self.all_sprites = groups[1]
        if self.direction == 1:
            self.pos = pos + vector(20,22)
        else:
            self.pos = pos + vector(40,22)
        super().__init__(self.pos,image,groups, order = ORDERS["bg"])


        self.particle_frames = particle_frames
        self.collision_sprites = collision_sprites
        self.player = player
        self.speed = 50
        self.timer = Timer(350)
        self.timer.activate()

        self.destructible = True # so it dies when it hits something

    def update(self,dt):
        '''moves the pearl in the right diection and kills it it it hits something'''  
        if self.rect.collidelist([sprite.rect for sprite in self.collision_sprites]) != -1:
            if not self.rect.colliderect(self.clam_rect):
                return self.die() # returns it so that class update method ends (saves on unnecessary computation)
        if not self.timer.active:
            self.speed = 150
        else:
            self.timer.update()
        self.rect.x += dt * self.speed * self.direction
    
    def die(self):
        '''kills the sprite and plays a particle effect'''
        self.kill()
        Particle_effect(self.rect.topleft,self.particle_frames,self.all_sprites)

class Particle_effect(Sprite):
    def __init__(self, pos, frames, groups,animation_speed = 7):
        super().__init__(pos, frames[0], groups, order = ORDERS["main"])
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = animation_speed

    def update(self,dt):
        '''animates the image and kills the sprite when the animation finishes'''
        self.frame_index += self.animation_speed * dt
        if int(self.frame_index)>= len(self.frames):
            self.kill()# ends update method
            return None
        self.image = self.frames[int(self.frame_index)]

class Item(Animated_sprite):
    def __init__(self,pos,frames,groups,name):
        '''sets a name and random animation speed'''
        animation_speed = random.uniform(6,9)
        super().__init__(pos,frames,groups,animation_speed)
        self.name = name

class Icon(pygame.sprite.Sprite):
    def __init__(self,pos,frames,groups):
        '''creates a basic class for the player that stores an image and rect'''
        super().__init__(groups)
        self.order = ORDERS["main"]
        self.image = frames["idle"][0] # image is changed in the overworld file
        pos = pos + vector(TILE_SIZE/2,5)
        self.rect = self.image.get_frect(center = pos)
