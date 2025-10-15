from settings import *
from sprites import *
import random
from timer import Timer
from player import Player
from groups import All_sprites

class Level():
    def __init__(self,tmx_map, level_frames,shop_frames, Data,change_stage):
        '''creates all the sprite groups and variables'''
        self.screen = pygame.display.get_surface()
        self.width = tmx_map.width * TILE_SIZE
        self.bottom = tmx_map.height * TILE_SIZE
        self.shop_frames = shop_frames
        self.item_frames = level_frames["items"]

        self.abilities = []
        self.swap = Timer(250)
        self.ability_timer = Timer(200)
        self.current_ability = None
        self.slow_motion = Timer(15000)

        self.Data = Data
        level_data = tmx_map.get_layer_by_name("Data")[0].properties
        self.death_border = self.bottom - level_data["death_border"]
        self.change_stage = change_stage
        
        self.all_sprites = All_sprites(self.width,self.bottom,level_data,level_frames)
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collidable = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.moving_platforms = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        
        self.setup(tmx_map, level_frames)
        

    def setup(self,tmx_map, level_frames):
        '''creates sprites for all the elements in the map file'''
        #tiles ---------------------------------------------------------------
        for x, y, surf in tmx_map.get_layer_by_name("Terrain").tiles():
            Sprite((x*TILE_SIZE,y*TILE_SIZE),surf,(self.all_sprites,self.collision_sprites))

        for x,y, surf in tmx_map.get_layer_by_name("Platforms").tiles():
            Sprite((x*TILE_SIZE,y*TILE_SIZE),surf,(self.all_sprites,self.semi_collidable))

        for x,y, surf in tmx_map.get_layer_by_name("Bg").tiles():
            Sprite((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites,ORDERS["bg"])

        for x,y, surf in tmx_map.get_layer_by_name("Fg").tiles():
            Sprite((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites,ORDERS["fg"])

        #water ------------------------------------------------------------

        for obj in tmx_map.get_layer_by_name("Water"):
            for i in range(0, int(obj.width / TILE_SIZE)):
                Animated_sprite((obj.x + i*TILE_SIZE, obj.y),level_frames["water_surface"],self.all_sprites,7,ORDERS["water"])
                for j in range(1, int(obj.height / TILE_SIZE)):
                    Sprite((obj.x + i*TILE_SIZE, obj.y + (j*TILE_SIZE)),level_frames["water_body"],self.all_sprites,ORDERS["water"])
            
        #objects ----------------------------------------------------------

        for obj in tmx_map.get_layer_by_name("Bg details"):
            if obj.name == "static":
                Sprite((obj.x,obj.y),obj.image,self.all_sprites,ORDERS["bg"])
            else:
                Animated_sprite((obj.x,obj.y),level_frames[obj.name],self.all_sprites,8,ORDERS["main"])
            if obj.name == "candle":
                Animated_sprite(((obj.x,obj.y)-vector(30,30)),level_frames["candle_light"],self.all_sprites,5,ORDERS["main"])
                
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "flag":
                self.end_flag = Animated_sprite((obj.x,obj.y),level_frames["flag"],self.all_sprites,5).rect
                Sprite((obj.x,obj.y)+vector(0,125),self.shop_frames["dog"],self.all_sprites,ORDERS["dog"])
            elif obj.name == "Player":
                self.player = Player(
                    pos = (obj.x,obj.y),
                    frames = level_frames["player"], 
                    jump_frames = level_frames["jump"],
                    groups = self.all_sprites,
                    sprites =(self.collision_sprites,self.semi_collidable,self.moving_platforms,self.enemy_sprites),
                    Data = self.Data)
            elif obj.name in ("barrel","crate"):
                Sprite((obj.x,obj.y),obj.image,(self.all_sprites,self.collision_sprites))
            elif "palm" in obj.name:
                if "bg" in obj.name:
                    Animated_sprite((obj.x,obj.y),level_frames["palms"][obj.name],self.all_sprites,random.uniform(4,7),ORDERS["bg"])
    
                else:
                    Animated_sprite((obj.x,obj.y),level_frames["palms"][obj.name],(self.all_sprites,self.semi_collidable),random.uniform(4,7),ORDERS["bg"])
            else:
                if obj.name == "floor_spike":
                    frames = level_frames["floor_spike"]
                    y = obj.y
                    if obj.properties['inverted']:
                        frames = [pygame.transform.flip(frame,False,True) for frame in frames]
                        y -= 32
                    Animated_sprite((obj.x,y+32),frames,(self.all_sprites,self.enemy_sprites),5)
                else:
                    Animated_sprite((obj.x,obj.y),level_frames[obj.name],self.all_sprites,5)

        #moving objects -------------------------------------------------------------
        
        for obj in tmx_map.get_layer_by_name("Moving objects"):
            if obj.name == "moving_platform":
                Moving_sprite((obj.x,obj.y),obj.width,obj.height,level_frames["moving_platform"],(self.all_sprites,self.semi_collidable,self.moving_platforms))
            elif obj.name == "saw":
                if obj.properties["speed"] >= 0:
                    Moving_sprite((obj.x,obj.y),obj.width,obj.height,level_frames["saw"],(self.all_sprites,self.enemy_sprites),obj.properties["speed"],10)
                    if obj.width>obj.height:
                        for x in range(int(obj.x),int(obj.x + obj.width),20):
                            Sprite((x,obj.y+9),level_frames["saw_chain"],self.all_sprites,ORDERS["bg"])
                else:
                    Animated_sprite((obj.x,obj.y),level_frames["saw"],(self.all_sprites,self.enemy_sprites),20)
            elif obj.name == "spiked_ball":
                Spiked_ball((obj.x,obj.y),obj.image,level_frames["spiked_chain"],obj.properties["start_angle"],obj.properties["end_angle"],obj.properties["radius"],obj.properties["speed"],(self.all_sprites,self.enemy_sprites))
            elif obj.name == "boat":
                Moving_sprite((obj.x,obj.y),obj.width,obj.height,level_frames["boat"],(self.all_sprites,self.collision_sprites,self.moving_platforms),obj.properties["speed"],0,ORDERS["main"],True)
                


        #enemies ------------------------------------------------------------------
        for obj in tmx_map.get_layer_by_name("Enemies"):
            if obj.name == "Tooth":
                Tooth((obj.x,obj.y),level_frames["Tooth"],(self.all_sprites,self.enemy_sprites),self.collision_sprites)
            elif obj.name == "clam":
                Clam((obj.x,obj.y),level_frames["Clam"],level_frames["Pearl"],(self.all_sprites,self.collision_sprites),self.enemy_sprites,self.player.hitbox_rect,obj.properties["inverted"],level_frames["particle"])

        #Items and abilities-----------------------------------------------------------------------
        for obj in tmx_map.get_layer_by_name("Items"):
            Item((obj.x,obj.y),level_frames["items"][obj.name],(self.all_sprites,self.item_sprites),obj.name)

    def check_border(self):
        '''makes sure player stays within the map'''
        if self.player.hitbox_rect.left <= 0:
            self.player.hitbox_rect.left = 0
        elif self.player.hitbox_rect.right >= self.width:
            self.player.hitbox_rect.right = self.width

    def check_items(self):
        '''sees if the player picks up an item'''
        for item in self.item_sprites:
            if self.player.hitbox_rect.colliderect(item.rect):
                match item.name:
                    case "diamond":
                        self.Data.gain_coins(50)
                    case "gold":
                        self.Data.gain_coins(20)
                    case"silver":
                        self.Data.gain_coins(5)
                    case "skull":
                        self.Data.gain_skull()
                    case "potion":
                        self.Data.gain_health()
                    case "clock":
                        self.abilities.append("clock")
                        self.current_ability = "clock"
                    case "shield":
                        self.abilities.append("shield")
                        self.current_ability = "shield"
                item.kill()
    
    def draw_abilities(self):
        '''draws the abilites you have in the bottom right'''
        self.swap.update()
        self.ability_timer.update()
        
        for i in range(len(self.abilities)):
            image = self.item_frames[self.abilities[i]][0]
            if not self.current_ability == self.abilities[i]:        
                image.set_alpha(100)
            else:
                image.set_alpha(255)
            self.screen.blit(image,(SCREEN_WIDTH-64*(i+1),SCREEN_HEIGHT-64))

        if len(self.abilities) != 0:   
            index = self.abilities.index(self.current_ability)
            keys = pygame.key.get_pressed()
            self.use_ability = True if keys[pygame.K_e] else False
            if keys[pygame.K_RIGHT] and not self.swap.active:
                index = (index+1)%len(self.abilities)
                self.current_ability = self.abilities[index]
                self.swap.activate()
            elif keys[pygame.K_LEFT] and not self.swap.active:
                index = (index-1)%len(self.abilities)
                self.current_ability = self.abilities[index]
                self.swap.activate()
            
        
        if self.current_ability == "clock" and self.use_ability and not self.ability_timer.active:
            self.slow_motion.activate()
            self.ability_timer.activate()
            self.abilities.remove("clock")
            self.current_ability = None if len(self.abilities) == 0 else self.abilities[(index-1)%len(self.abilities)]
        elif self.current_ability == "shield" and self.use_ability and not self.ability_timer.active:
            self.player.timers["shield"].activate()
            self.ability_timer.activate()
            self.abilities.remove("shield")
            self.current_ability = None if len(self.abilities) == 0 else self.abilities[(index-1)%len(self.abilities)]

        #use abilities
        if self.slow_motion.active:
            fade = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
            fade.fill((0,0,0))
            fade.set_alpha(100)#0 is fully see through 255 is not see-through
            self.screen.blit(fade,(0,0))
        if self.player.timers["shield"].active:
            #creates a surface that can accept alpha values suggested by a user on a reddit forum in order to draw a transparent curcle
            surface = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.aacircle(surface,'#5751bd50',self.player.rect.center + self.all_sprites.offset,50) # last 2 hex digits are the alpha value
            self.screen.blit(surface, (0,0))

    def check_state(self):
        '''see if play has reached the end or died'''
        if self.player.hitbox_rect.colliderect(self.end_flag):
            if self.Data.current_level == self.Data.level_unlocked:
                self.Data.level_unlocked +=1
            self.change_stage(True)
        if self.player.hitbox_rect.top >= self.death_border or self.Data.get_health() <=0:
            self.Data.lose_health()
            self.change_stage(True)
        
    def run(self, dt):
        '''runs all the methods needed'''
        self.slow_motion.update()
        if self.slow_motion.active:
            dt = dt/3
        self.all_sprites.update(dt)
        self.check_border()
        self.check_items()
        self.check_state()
        self.all_sprites.draw(self.player.rect.center,self.Data.dog)
        self.draw_abilities()
