from settings import *
from timer import Timer
from sprites import Sprite
from random import randint, uniform
from Data import Data
import sys

class Menu():
    def __init__(self,ui_frames,shop_frames,change_stage,data):
        '''creates the rects for each of the buttons (and other variables)'''
        self.screen = pygame.display.get_surface()
        self.timer = Timer(400)
        self.Data = data

        self.state = "pause"
        self.ui_frames = ui_frames
        self.button = ui_frames["button"]
        self.font = ui_frames["font"]
        self.change_stage = change_stage

        self.resume_button = self.button.get_frect(topleft = (362,90))
        self.shop_button = self.button.get_frect(topleft = (362,290))
        self.overworld_button = self.button.get_frect(topleft = (362,490))
        self.shop_frames = shop_frames

    def fade(self):
        ''' makes the screen darker; by making a slightly transparent black screen and covering the previous screen'''
        fade = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        fade.fill((0,0,0))
        fade.set_alpha(200)#0 is fully see through 255 is not see-through
        self.screen.blit(fade,(0,0))

    def draw_menu(self):
        '''draws all the button and creates rects'''
        text_options = ["resume","shop","select level"]
        selected = self.check_mouse()
        for i in range(3):
            self.screen.blit(self.button,(362,90 +200*i))
            
            text = self.font.render(text_options[i],True,"white")
            if selected != i:
                text.set_alpha(100)
            pos = ((600-self.font.size(text_options[i])[0])/2 +340, (250 - self.font.size(text_options[i])[1])/2 + 25+200*i)
            self.screen.blit(text,pos)

    def check_mouse(self):
        '''checks if the mouse is over a button'''
        mouse_pos = pygame.mouse.get_pos()
        if self.resume_button.collidepoint((mouse_pos)):
            return 0
        elif self.shop_button.collidepoint((mouse_pos)):
            return 1
        if self.overworld_button.collidepoint((mouse_pos)):
            return 2
               

    def run(self,player_center,all_sprites):
        '''fades the screen check for inputs and runs the draw funcs'''
        self.timer.activate()
        self.fade()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.Data.save()
                    pygame.quit()
                    sys.exit("Thank you for playing")
                elif pygame.key.get_pressed()[pygame.K_ESCAPE] and not self.timer.active:
                    return 0 # break
                elif event.type == pygame.MOUSEBUTTONUP:
                    button = self.check_mouse()
                    if button == 0:
                        return 0 # break
                    elif button == 2:
                        self.change_stage(True)
                        return 0
                    elif button == 1: # creates and the runs and instance of the shop class
                        shop(self.screen,self.ui_frames,self.shop_frames,self.Data,self.button).run()
                        self.screen.fill("black")# now re-draws the menu and the background
                        all_sprites.draw(player_center,self.Data.dog)
                        self.fade()
                        self.timer.activate()
            
            self.draw_menu()
            self.timer.update()
            pygame.display.update()

class shop():
    def __init__(self,screen,ui_frames,images,data,button):
        '''sets the items in the shop and other variables'''
        self.items = [images["dog"]]
        self.labels = ["dog"]
        self.prices = [1]
        self.screen = screen
        self.Data = data
        self.button = pygame.transform.scale(button,(140,32))
        
        
        self.num_large_clouds = 6
        self.num_clouds = 6
        self.large_cloud = images["large_cloud"]
        self.small_clouds = images["small_clouds"]
        self.cloud_sprites = pygame.sprite.Group()
        self.small_cloud_sprites = pygame.sprite.Group()
        self.horizon_line = SCREEN_HEIGHT - 150

        self.all_sprites = pygame.sprite.Group()
        self.font = ui_frames["font"]
        self.skull = ui_frames["skull"]

        if self.Data.dog == True:
            self.prices[self.labels.index("dog")] =0

    def draw_items(self):
        '''draws the items and creates their rects'''
        self.rects = []
        for i in range(len(self.items)):
            space = SCREEN_WIDTH/len(self.items)
            mid = (space*i + space*(i+1))/2 # places the items in the middle depending on the num of items
            item_rect = pygame.FRect((mid - (250/2),100),(250,500))
            self.rects.append(item_rect)
            item_surface = pygame.Surface((250,500))
            item_surface.fill("black")
            mouse_pos = pygame.mouse.get_pos()
            if not item_rect.collidepoint((mouse_pos)):
                item_surface.set_alpha(200)

            item_image = self.items[i]      
            item_image = pygame.transform.scale_by(item_image,250/item_image.width)


            if self.labels[i] == "dog" and self.Data.dog == True:
                price = "equipped"
            else:
                price = self.prices[i]
            price_width,price_height = self.font.size(str(price))
            price_width +=10
            price_label = self.font.render(str(price),True,"black")
            skull_height,skull_width = self.skull.height,self.skull.width

            name = self.labels[i]
            label = self.font.render(name,True,"black")
            label_width,label_height = self.font.size(name)

            self.screen.blit(price_label,(mid - price_width/2,600))
            self.screen.blit(self.skull,(mid -price_width/2 + price_width,600))
            self.screen.blit(label,(mid -label_width/2,99-label_height))# 100 - (250-width)/2 = (450-width)/2
            self.screen.blit(item_surface,item_rect)
            self.screen.blit(item_image,(mid- (250/2),(700-item_image.width)/2))

    def draw_clouds(self):
        '''draws clouds and moves them back to the right when they leave the screen'''
        if len(self.cloud_sprites.sprites()) == 0:
            for x in range(0,self.num_large_clouds):#large clouds
                Sprite((x*self.large_cloud.get_width(),self.horizon_line-self.large_cloud.get_height()),self.large_cloud,(self.cloud_sprites,self.all_sprites),ORDERS["sky"])
            for i in range(0,self.num_clouds): # small clouds
                index = randint(0,len(self.small_clouds)-1)
                x = i*(SCREEN_WIDTH/self.num_clouds) + randint(-50,50)
                y = random.randint(0,self.horizon_line - self.small_clouds[index].get_height()-200)
                Sprite((x,y),self.small_clouds[index],(self.small_cloud_sprites,self.all_sprites),ORDERS["sky"])
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
                    x = SCREEN_WIDTH + randint(0,50)
                    y = random.randint(0,self.horizon_line - self.small_clouds[index].get_height()-200)
                    Sprite((x,y),self.small_clouds[index],(self.small_cloud_sprites,self.all_sprites),ORDERS["sky"])


    def draw_sky(self):
        '''draws background'''
        self.screen.fill('#ddc6a1')
        sea_rect = pygame.Rect((0,self.horizon_line),(SCREEN_WIDTH,self.horizon_line))
        pygame.draw.rect(self.screen,"#92a9ce",sea_rect)

    def draw_skulls(self):
        '''draws how many skulls you have'''
        amount = str(self.Data.get_skulls())
        text = self.font.render(amount,True,"black")
        self.screen.blit(text,(5,5))
        self.screen.blit(self.skull,(10+self.font.size(amount)[0],5))

        text = self.font.render("back",True,"white")
        self.back_rect = self.button.get_frect(topright = (SCREEN_WIDTH-5,10))
        if not self.back_rect.collidepoint(pygame.mouse.get_pos()):
            text.set_alpha(100)
        
        self.screen.blit(self.button, self.back_rect)
        self.screen.blit(text,(SCREEN_WIDTH-100,10))
        
    def click(self):
        '''purchases the item you hovering over (only called when you've clicked)'''
        mouse_pos = pygame.mouse.get_pos()
        for i in range(len(self.rects)):
            if self.rects[i].collidepoint((mouse_pos)):
                if self.Data.get_skulls() >= self.prices[i]:
                    self.Data.lose_skulls(self.prices[i])
                    self.prices[i] = 0
                    if self.labels[i] == "dog":
                        self.Data.dog = True
                    #buy item
        if self.back_rect.collidepoint((mouse_pos)):
            self.running = False

    def draw_everything(self):
        '''runs all the draw methods'''
        self.draw_clouds()
        self.draw_sky() 
        self.all_sprites.draw(self.screen)
        self.draw_skulls()
        self.draw_items()
        
    def run(self):
        '''updates display and checks inputs'''
        self.running  = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.Data.save()
                    pygame.quit()
                    sys.exit("Thank you for playing")
                if event.type == pygame.MOUSEBUTTONUP:
                    self.click()
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    self.running = False
            self.all_sprites.update()
            self.draw_everything()
            pygame.display.update()
        
