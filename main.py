import sys
from os.path import join
from settings import *
from Data import Data
from level import Level
from pytmx.util_pygame import load_pygame
from files import*
from Menu import Menu
from timer import Timer
from overworld import Overworld
from select_save import Select_save


class Game():
    def __init__(self):
        '''load everything needed'''      
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pirate adventure")
        self.import_assets()

        self.level_maps ={0:load_pygame(join("data","levels","TEST.tmx")),
                          1:load_pygame(join("data","levels","1.tmx")),
                          2:load_pygame(join("data","levels","2.tmx")),
                          3:load_pygame(join("data","levels","3.tmx")),
                          4:load_pygame(join("data","levels","TEST.tmx")),
                          5:load_pygame(join("data","levels","TEST.tmx"))
                          }

        self.Data = Data(5,self.ui_frames)
        #self.current_level = Level(load_pygame(join("data","levels","TEST.tmx")),self.level_frames,self.Data)
        self.overworld_map = load_pygame(join("data","overworld","overworld.tmx"))
        self.menu = Menu(self.ui_frames,self.shop_frames,self.change_stage,self.Data)
        self.clock = pygame.time.Clock()
        self.select_save = Select_save(self.Data,self.ui_frames)
        self.paused = False
        self.timers = {"pause": Timer(400)}

    def change_stage(self,overworld):
        '''used to swap between levels and level select'''
        if overworld:
            self.current_level = self.current_level = Overworld(self.overworld_map,self.overworld_frames,self.shop_frames,self.Data,self.change_stage)
        else:
            self.current_level = Level(self.level_maps[self.Data.current_level],self.level_frames,self.shop_frames,self.Data,self.change_stage)

    def import_assets(self):
        '''imports all the images'''
        self.level_frames = {
            "palms" : import_sub_folders("graphics","level","palms"),
            "flag" : import_folder("graphics","level","flag"),
            "boat" : import_folder("graphics","objects","boat"),
            "player" : import_sub_folders("graphics","player"),
            "floor_spike": import_folder("graphics","enemies","floor_spikes"),
            "big_chain": import_folder("graphics","level","big_chains"),
            "candle": import_folder("graphics","level","candle"),
            "candle_light": import_folder("graphics","level","candle_light"),
            "large_cloud": import_image("graphics","level","clouds","large_cloud"),
            "small_clouds": import_folder("graphics","level","clouds","small"),
            "moving_platform": import_folder("graphics","level","helicopter"),
            "small_chain": import_folder("graphics","level","small_chains"),
            "water_body": import_image("graphics","level","water","body"),
            "water_surface": import_folder("graphics","level","water","top"),
            "window": import_folder("graphics","level","window"),
            "Tooth": import_folder("graphics","enemies","tooth"),
            "Clam": import_sub_folders("graphics","enemies","shell"),
            "Pearl": import_image("graphics","enemies","bullets","pearl"),
            "particle": import_folder("graphics","effects","particle"),
            "jump":import_folder("graphics","effects","jump"),
            "items": import_sub_folders("graphics","items"),
            "saw": import_folder("graphics","enemies","saw","animation"),
            "saw_chain": import_image("graphics","enemies","saw","saw_chain"),
            "spiked_chain":import_image("graphics","enemies","spike_ball","spiked_chain"),
            "bg_tiles": import_folder_dict("graphics","level","bg","tiles")
            }
        self.ui_frames = {
            "heart": import_folder("graphics","ui","heart"),
            "coin": import_image("graphics","ui","coin"),
            "skull":import_image("graphics","ui","skull"),
            "button": import_image("graphics","ui","button"),
            "font": pygame.font.Font(join("graphics","ui","runescape_uf.ttf"),32),
            "big_font": pygame.font.Font(join("graphics","ui","runescape_uf.ttf"),50)
        }
        self.shop_frames = {
            "dog": pygame.transform.scale(import_image("graphics","shop","dog_laying"), (100,100)),
            "dog_sitting": pygame.transform.scale(import_image("graphics","shop","dog_sitting"), (100,100)),
            "large_cloud":self.level_frames["large_cloud"],
            "small_clouds": self.level_frames["small_clouds"]
            }
        self.overworld_frames = {
            "icon": import_sub_folders("graphics","overworld","icon"),
            "ojects": import_folder_dict("graphics","overworld","objects"),
            "palm": import_folder("graphics","overworld","palm"),
            "path": import_folder_dict("graphics","overworld","path"),
            "water": import_folder("graphics","overworld","water"),
            "dog" : import_sub_folders("graphics","overworld","dog")
        }


    def update_timers(self):
        '''updates all the timers'''
        for timer in self.timers:
                self.timers[timer].update()

    def lost(self):
        '''creates a game over screen'''
        fade = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        fade.fill((0,0,0))
        fade.set_alpha(180)#0 is fully see through 255 is not see-through
        self.screen.blit(fade,(0,0))

        button = pygame.transform.scale_by(self.ui_frames["button"],0.6)
        restart = self.ui_frames["font"].render("Restart level",True,"white")
        restart_rect = button.get_frect(topleft = (473.5,300))

        self.text = self.ui_frames["big_font"].render("Game over",True,"white")
        self.screen.blit(self.text,(546,200))
        while True:
            mouse_pos = pygame.mouse.get_pos()
            if not restart_rect.collidepoint(mouse_pos):
                restart.set_alpha(150)
            else:
                restart.set_alpha(255)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.Data.save()
                    pygame.quit()
                    sys.exit("Thank you for playing")
                if event.type == pygame.MOUSEBUTTONUP:
                    if restart_rect.collidepoint(mouse_pos):
                        self.Data.restart()
                        self.run()

            self.screen.blit(button,(473.5,300))
            self.screen.blit(restart,(564,320))
            pygame.display.update()

    def run(self):
        '''the main run loop, checks inputs and upadates display'''
        self.overworld = Overworld(self.overworld_map,self.overworld_frames,self.shop_frames,self.Data,self.change_stage)
        self.current_level = self.overworld
        
        running = True
        while running:
            dt = self.clock.tick() /1000
            if self.paused:
                dt = 0
                self.paused = False
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.Data.save()
                    pygame.quit()
                    sys.exit("Thank you for playing")
                elif pygame.key.get_pressed()[pygame.K_ESCAPE] and not self.timers["pause"].active:
                    self.paused = True
                    self.menu.run(self.current_level.player.rect.center,self.current_level.all_sprites)
                    self.timers["pause"].activate()

            dt = 0 if dt>0.5 else dt
            self.screen.fill("black")
            self.update_timers()
            self.current_level.run(dt)
            self.Data.draw(dt)
            pygame.display.update()

            if self.Data.get_health() <= 0:
                running = False

        # lose the game
        self.lost()

if __name__ == "__main__":
    game = Game()
    game.select_save.run()
    game.run()
