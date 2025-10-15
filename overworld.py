from settings import *
from sprites import Sprite, Animated_sprite, Icon, Path
from groups import Overworld_sprites
import math

class Overworld():
    def __init__(self,tmx_map,overworld_frames,shop_frames,Data,change_stage):
        '''creates important variables and sets the speed'''
        #self.tmx_map = tmx_map
        self.overworld_frames = overworld_frames
        self.shop_frames = shop_frames
        self.Data = Data
        self.change_stage = change_stage

        self.nodes = pygame.sprite.Group()
        self.node_properties = []
        self.all_sprites = Overworld_sprites()
        self.path_sprites = pygame.sprite.Group()

        
        self.setup(tmx_map)
        self.moving = False
        self.Turning = False
        self.direction = ()
        self.speed = 200
        self.previous_turn = None

        self.state = "idle"
        self.frame_index = 0


    def setup(self,tmx_map):
        '''creates all the sprites from the map file'''
        # water ----------------------------------------------------------------------------------------
        for x in range(tmx_map.width):
            for y in range(tmx_map.height):
                Animated_sprite((x*TILE_SIZE,y*TILE_SIZE),self.overworld_frames["water"],(self.all_sprites),5,ORDERS["sky"])

        # tiles-------------------------------------------------------------------------------------
        for x,y,surf in tmx_map.get_layer_by_name("main").tiles():
            Sprite((x*TILE_SIZE,y*TILE_SIZE),surf,(self.all_sprites),ORDERS["bg"])
        for x,y,surf in tmx_map.get_layer_by_name("top").tiles():
            Sprite((x*TILE_SIZE,y*TILE_SIZE),surf,(self.all_sprites),ORDERS["bg"])
        
        # nodes and paths ------------------------------------------------------------------------------
        for node in sorted(tmx_map.get_layer_by_name("Nodes"),key = lambda node : node.properties["stage"]):
            if node.properties["stage"] == self.Data.current_level:
                self.player = Icon((node.x,node.y),self.overworld_frames["icon"],self.all_sprites)
                pos = (node.x-75,node.y-28)
                self.dog = Sprite(pos,self.shop_frames["dog_sitting"],self.all_sprites,ORDERS["dog"]) # draw player and dog
            if node.properties["stage"] <= self.Data.level_unlocked:
                self.node_properties.append(node.properties)
                pos = (node.x-TILE_SIZE/2,node.y-TILE_SIZE/2)
                Sprite(pos,self.overworld_frames["path"]["node"],(self.all_sprites,self.nodes),ORDERS["bg"])
        for path in tmx_map.get_layer_by_name("path"):
            if path.properties["path_id"] <= self.Data.level_unlocked:
                Path((path.x,path.y),self.overworld_frames["path"][path.name],(self.all_sprites,self.path_sprites),path.name)
        
        # objects -----------------------------------------------------------------------------------
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "palm":  
                Animated_sprite((obj.x,obj.y),self.overworld_frames["palm"],self.all_sprites,random.uniform(4,5))
            else:
                Sprite((obj.x,obj.y),obj.image,self.all_sprites,ORDERS["bg"])

    def check_input(self):
        '''gets inputs and sees if the can move that way'''
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            direction = "up"
            self.direction = vector(0,-1)
        elif keys[pygame.K_a]:
            direction = "left"
            self.direction = vector(-1,0)
        elif keys[pygame.K_d]:
            direction = "right"
            self.direction = vector(1,0)
        elif keys[pygame.K_s]:
            direction = "down"
            self.direction = vector(0,1)
        elif keys[pygame.K_SPACE]:
            self.change_stage(False)
        try:
            if int(self.node_properties[self.Data.current_level][direction]) <= self.Data.level_unlocked:
                self.moving = True
                self.destination = int(self.node_properties[self.Data.current_level][direction])
            else:
                self.direction = vector()
        except:
            self.direction = vector()

    def move(self,dt):
        '''moves or stops the player and calles turn method'''
        for node in self.nodes:# sees if you're at the correct node
            if self.player.rect.colliderect(node.rect):
                if (self.nodes.sprites()[self.destination] == node and 
                   self.distance((node.rect.topleft + vector(TILE_SIZE,TILE_SIZE/2 +5)),(int(self.player.rect.centerx),int(self.player.rect.centery))) <=self.speed * dt *3):
                    self.moving = False
                    self.previous_turn = None
                    self.Data.current_level = self.destination
                    self.direction = vector()
                    self.player.rect.center = (node.rect.topleft + vector(TILE_SIZE,TILE_SIZE/2 +5))

        for path in self.path_sprites:
            if self.player.rect.colliderect(path.rect) and path != self.previous_turn:
                if path.name == "tr":
                    self.turn(path,vector(0,1),vector(1,0),vector(0,-1),dt)
                elif path.name == "tl":
                    self.turn(path,vector(1,0),vector(0,-1),vector(-1,0),dt)
                elif path.name == "bl":
                    self.turn(path,vector(1,0),vector(0,1),vector(-1,0),dt)
                elif path.name == "br":
                    self.turn(path,vector(0,-1),vector(1,0),vector(0,1),dt)

        self.player.rect.topleft += self.direction * self.speed * dt
        self.dog.rect.topleft += self.direction * self.speed * dt

    def distance(self,p1,p2):
        return math.sqrt(math.pow(p1[0] - p2[0],2) + math.pow(p1[1] - p2[1],2))

    def turn(self,path,forward, new_forward, new_reverse,dt):
        '''turns if the player is near the center of the turn and isn't turning'''
        if self.distance(self.player.rect.center,(path.rect.topleft + vector(TILE_SIZE/2,5))) <= self.speed * dt:
            if not self.turning:
                self.player.rect.center = (path.rect.topleft + vector(TILE_SIZE/2,5))
                self.direction = new_forward if self.direction == forward else new_reverse
                self.turning = True
                self.previous_turn = path
        else:
            self.turning = False

    def animate(self,dt):
        '''determines what the player is doing and animates accordingly'''
        state = self.state
        if self.direction == vector(1,0):
            self.state = "right"
        elif self.direction == vector(-1,0):
            self.state = "left"
        elif self.direction == vector(0,-1):
            self.state = "up"
        elif self.direction == vector(0,1):
            self.state = "down"
        else:
            self.state = "idle"
        if self.state != state or int(self.frame_index) >= len(self.overworld_frames["icon"][self.state]):
            self.frame_index = 0
        self.player.image = self.overworld_frames["icon"][self.state][int(self.frame_index)]
        self.dog.image = self.overworld_frames["dog"][self.state][int(self.frame_index)]
        self.dog.image = pygame.transform.scale(self.dog.image, (100,100))
        self.frame_index += self.speed/20 * dt

        

    def run(self,dt):
        '''checks inupt is the player isnt moving and calls all the draw methods'''
        if not self.moving:
            self.check_input()
        else:
            self.move(dt)
            #print(self.destination)
        self.animate(dt)
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.player.rect.center,self.Data.dog)

