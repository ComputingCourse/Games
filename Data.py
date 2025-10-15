from settings import* 
import sys
import random
from timer import Timer
from math import sin

class Data():
    def __init__(self,health,frames):
        '''creates variables and sprite groups'''
        self.__health = health
        self.__coins = 0
        self.__skulls = 0
        self.current_level = 0
        self.level_unlocked = 0

        self.dog = False
        
        self.frames = frames
        self.font = frames["font"]
        self.screen = pygame.display.get_surface()
        self.heart_sprites = pygame.sprite.Group()
        self.flicker_timer = Timer(500)

        self.coin_count = Coin_count((5,30),frames["coin"],self.font)

    def setup(self,data,file):
        '''loads the data from the save file'''
        self.file_num = file
        if data != {}:
            self.__health = int(data['health'])
            self.__coins = int(data['coins'])
            self.__skulls = int(data['skulls'])
            self.current_level = int(data['current level'])
            self.level_unlocked = int(data['level unlocked'])
            self.dificulty = int(data["dificulty"])
            self.dog = True if data['dog'] == "True" else False
            self.draw_hearts()
        else:
            self.restart()
    
    def chose_dificulty(self):
        '''asks the user to chose their difficulty easy or hard'''
        self.screen.fill("black")
        self.dificulty = None
        text = self.frames["big_font"].render("Choose your dificulty:",True,"white")
        self.screen.blit(text,((SCREEN_WIDTH-text.size[0])/2,100))

        button = pygame.transform.scale_by(self.frames["button"],0.6)
        easy_rect = button.get_frect(topleft = (473.5,250))
        hard_rect = button.get_frect(topleft = (473.5,400))
        rects = [easy_rect, hard_rect]
        
        texts = [self.frames["font"].render("Easy",True,"white"),self.frames["font"].render("Hard",True,"white")]
        heart = self.frames["heart"][0]
        difficulties = [5,2]
        clicked = False
        while self.dificulty == None:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit("Thank you for playing")
                elif event.type == pygame.MOUSEBUTTONUP:
                    clicked = True

            for i in range(2):
                self.screen.blit(button,(473.5,250 + 150*i))
                if not rects[i].collidepoint(mouse_pos):
                    texts[i].set_alpha(100)
                    heart.set_alpha(100)
                else:
                    texts[i].set_alpha(255)
                    heart.set_alpha(255)
                    if clicked:
                        self.dificulty = difficulties[i]

                self.screen.blit(texts[i],(613,260 + 150*i))
                for j in range(difficulties[i]):
                    width  = heart.width * difficulties[i] +5*(difficulties[i]-1)
                    left = (SCREEN_WIDTH-width)/2
                    self.screen.blit(heart,(left + width*j/difficulties[i],295 + 150*i))

            pygame.display.update()
            heart.set_alpha(255)
        
    def restart(self):
        '''asks user to chose their dificultty and sets variables to 0'''
        self.chose_dificulty()
        self.__health = self.dificulty
        self.__coins = 0
        self.__skulls = 0
        self.current_level = 0
        self.level_unlocked = 0
        self.dog = False
        self.draw_hearts()

    def save(self):
        '''re-writes the files with the current variables(info)'''
        file = open(f"save_file_{self.file_num}.txt", "w")
        file.write(f'''current level: {self.current_level}
level unlocked: {self.level_unlocked}
coins: {self.__coins}
skulls: {self.__skulls}
health: {self.__health}
dificulty: {self.dificulty}
dog: {self.dog}''')

     
    def draw_hearts(self):
        '''creates the right amount of heart sprites'''
        for sprite in self.heart_sprites:
            sprite.kill()
        for i in range(self.__health):
            Heart((5 + 20*i,10),self.frames["heart"],self.heart_sprites)

    def lose_health(self):
        '''decreases health and re-draws hearts'''
        self.__health -= 1
        for sprite in self.heart_sprites:
            sprite.kill()
        self.draw_hearts()
        self.flicker = self.__health
        self.flicker_timer.activate()


    def lose_skulls(self,amount):
        self.__skulls -=amount

    def gain_health(self, amount = 1):
        '''increase health by given amount and re-draw hearts'''
        self.__health += amount
        self.draw_hearts()
        self.flicker = self.__health-1
        self.flicker_timer.activate()

    def get_health(self):
        return self.__health
    
    def get_skulls(self):
        return self.__skulls
 
    def gain_coins(self,amount):
        '''increases coins by amount and sees if they have enough coins to gain a heart'''
        self.__coins += amount
        if self.__coins >= 500//self.dificulty:#difficulty
            self.__coins -= 100
            self.gain_health()

    def gain_skull(self):
        self.__skulls +=1
    
    def flicker_heart(self):
        '''creates a flicker effect on the heart you just gained/lost'''
        if self.flicker_timer.active and sin(pygame.time.get_ticks() * 50) >= 0:
            white_mask = pygame.mask.from_surface(self.frames["heart"][0])
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey('black')
            self.screen.blit(white_surf,(5 + 20*self.flicker,10))
            self.flicker_timer.update()

    def draw(self,dt):
        '''draws hearts and coins'''
        self.heart_sprites.update(dt, self.screen)
        self.coin_count.update(self.__coins, self.screen)
        self.flicker_heart()


class Heart(pygame.sprite.Sprite):
    def __init__(self,pos,frames,sprites):
        '''creates necessary variables '''
        super().__init__(sprites)

        self.frames = frames
        self.frame_index = 0
        self.image = frames[0]
        self.rect = self.image.get_frect(topleft = pos)
        self.active = True
        self.animation_speed = 5

    def animate(self,dt):
        '''plays a heart animation for each on average once every 2000 frames '''
        if self.active:
            self.frame_index += self.animation_speed * dt
            if int(self.frame_index) >= len(self.frames):
                self.active = False
                self.frame_index = 0
            self.image = self.frames[int(self.frame_index)]
        else:
            self.active = True if random.randint(1,2000) == 1 else False # each heart animates on average once every 2000 frames

    def update(self, dt, screen):
        '''updates and draws itseld'''
        self.animate(dt)
        screen.blit(self.image, self.rect.topleft)

class Coin_count(pygame.sprite.Sprite):
    def __init__(self,pos,image,font):
        '''sets the necessary variables'''
        super().__init__()
        self.pos = pos
        self.image = image
        self.rect = self.image.get_frect()
        self.font = font
        
    def update(self, amount, screen):
        '''draws the number of coins and a coin image'''
        text = self.font.render(str(amount),True,"white")
        screen.blit(text, self.pos)
        width = self.font.size(str(amount))[0]
        screen.blit(self.image, (self.pos[0]+width+5,self.pos[1]+2))
