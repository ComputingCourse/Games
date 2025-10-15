from settings import *
from sprites import Sprite
from math import ceil
from random import randint,uniform

class Overworld_sprites(pygame.sprite.Group):
    def __init__(self):
        '''sets important variables'''
        super().__init__()
        self.width, self.height = SCREEN_WIDTH, SCREEN_HEIGHT
        self.screen = pygame.display.get_surface()
        self.offset = vector()

    def draw(self,player_pos,dog):
        '''draws all the overworld sprites centered arounf the players'''
        self.offset.x = -(player_pos[0] - self.width/2)
        self.offset.y = -(player_pos[1] - self.height/2)


        for sprite in sorted(self,key = lambda sprite : sprite.order):
            if sprite.order != ORDERS["main"] and not(sprite.order == ORDERS["dog"] and dog != True): # only draw the dog it they have it
                pos = sprite.rect.topleft + self.offset
                self.screen.blit(sprite.image, pos)
        # in the main layer it draws images lower on the screen on top of things higher on the screen to give the illusion of being behind someting
        for sprite in sorted(self,key = lambda sprite : sprite.rect.bottom):
            if sprite.order == ORDERS["main"]:
                pos = sprite.rect.topleft + self.offset
                self.screen.blit(sprite.image, pos)


class All_sprites(pygame.sprite.Group):
    def __init__(self,level_width, level_bottom,level_data,level_frames):
        '''creates important variables as well as all the sprite groups for the background'''
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.offset = vector()
        self.level_width, self.level_bottom = level_width, level_bottom
        self.width, self.height = SCREEN_WIDTH, SCREEN_HEIGHT

        self.level_data = level_data
        self.top_limit = self.level_data["top_limit"]
        self.bg_tiles = level_frames["bg_tiles"]
        self.large_cloud = level_frames["large_cloud"]
        self.small_clouds = level_frames["small_clouds"]
        self.cloud_sprites = pygame.sprite.Group()
        self.small_cloud_sprites = pygame.sprite.Group()

        self.num_large_clouds = ceil(self.level_width/self.large_cloud.get_width())+1
        self.num_clouds = 10


        if self.level_data["bg"] != None:
            self.draw_bg_tiles()
            self.sky = False
        else:
             self.sky = True

    def draw_clouds(self):
        '''draws clouds and moves them back to the right when they leave the screen'''
        if len(self.cloud_sprites.sprites()) == 0:
            for x in range(0,self.num_large_clouds):#large clouds
                Sprite((x*self.large_cloud.get_width(),self.level_data["horizon_line"]-self.large_cloud.get_height()),self.large_cloud,(self,self.cloud_sprites),ORDERS["sky"])
            for i in range(0,self.num_clouds): # small clouds
                index = randint(0,len(self.small_clouds)-1)
                x = i*(self.level_width/self.num_clouds) + randint(-50,50)
                y = random.randint(-self.top_limit,self.level_data["horizon_line"] - self.small_clouds[index].get_height()-200)
                Sprite((x,y),self.small_clouds[index],(self.small_cloud_sprites,self),ORDERS["sky"])
        else: #moves clouds left
            for cloud in self.cloud_sprites.sprites():
                cloud.rect.x -=0.1
                if cloud.rect.right<=0:
                    cloud.rect.left = cloud.rect.left + cloud.rect.width * self.num_large_clouds
            for small in self.small_cloud_sprites.sprites():
                small.rect.x -= uniform(0.05,0.2)
                if small.rect.right<=0:
                    small.kill()
                    index = randint(0,len(self.small_clouds)-1)
                    x = self.level_width + randint(0,50)
                    y = random.randint(-self.top_limit,self.level_data["horizon_line"] - self.small_clouds[index].get_height()-200)
                    Sprite((x,y),self.small_clouds[index],(self.small_cloud_sprites,self),ORDERS["sky"])

    def draw_bg_tiles(self):
        '''fills the background with the background tiles'''
        for x in range(0,self.level_width, TILE_SIZE):
                    for y in range(-ceil(self.top_limit/TILE_SIZE)*TILE_SIZE,self.level_bottom, TILE_SIZE):
                        Sprite((x,y),self.bg_tiles[self.level_data["bg"]],self,ORDERS["sky"])

    def draw_sky(self):
        '''draws the sky and sea'''
        self.screen.fill('#ddc6a1')
        sea_rect = pygame.Rect((0,self.level_data["horizon_line"]+self.offset.y),(self.width,self.level_bottom-self.level_data["horizon_line"]))
        pygame.draw.rect(self.screen,"#92a9ce",sea_rect)


    def camera_constraint(self,player_pos):
        '''makes sure the camera doesn't show outside the map'''
        self.offset.x = 0 if player_pos[0] <= self.width/2 else self.offset.x # too far left
        if player_pos[0] >= (self.level_width-self.width/2): # too far right
            self.offset.x = -(self.level_width - self.width)
        if player_pos[1] >= (self.level_bottom-self.height/2):#too far down
            self.offset.y = -(self.level_bottom-self.height)
        if player_pos[1] <= (self.height/2 - self.top_limit):
            self.offset.y = self.top_limit
                         
            
    
    def draw(self,player_pos,dog):
        '''draws the background and all other sprites'''
        self.offset.x = -(player_pos[0] - self.width/2)
        self.offset.y = -(player_pos[1] - self.height/2)

        self.camera_constraint(player_pos)
        #print(self.offset.x)
        if self.sky:
            self.draw_sky()
            self.draw_clouds()

        for sprite in sorted(self,key = lambda sprite : sprite.order):
            if sprite.order == ORDERS["water"]:
                self.offset.x = round(self.offset.x, 0) 
            if sprite.order ==ORDERS["dog"] and dog != True:
                pass
            else:
                pos = sprite.rect.topleft + self.offset
                self.screen.blit(sprite.image, pos)
        
