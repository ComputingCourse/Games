from settings import *
import sys

class Select_save():
    def __init__(self,data,ui_frames):
        '''loades in the stored data form each save file'''
        self.Data = data
        self.ui_frames = ui_frames
        self.screen =  pygame.display.get_surface()
        self.big_font = ui_frames["big_font"]
        self.font = ui_frames["font"]
        self.button = ui_frames["button"]
        self.saved_data = [{},{},{},{}]
        for i in range(1,4):
                file = open(f"save_file_{i}.txt")
                file = (file.readlines())
                for line in file:
                    splited = line.split(": ")
                    self.saved_data[i][splited[0]] = splited[1].rstrip()

    def run(self):
        '''blits all the buttons and text '''
        self.screen.fill("Black")
        self.text = self.big_font.render("Welcome to Pirate Adventure",True,"white")
        self.screen.blit(self.text,(374,100))
        self.text = self.font.render("Please select you save file:",True,"white")
        self.screen.blit(self.text,(482,200))
        #print((SCREEN_WIDTH-self.button.width)/2)
        selected = None
        while not selected:
            clicked = False
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit("Thank you for playing")
                if event.type == pygame.MOUSEBUTTONUP:
                    clicked = True
            
            for i in range(1,4):
                self.screen.blit(self.button,(362,120 +160*i))
                rect = self.button.get_frect(topleft = (362,120 +155*i))
                self.text = self.font.render(f"Save file {i}",True,"white")
                if self.saved_data[i] != {}:
                    self.info = self.font.render(f"level unlocked: {self.saved_data[i]['level unlocked']}   coins: {self.saved_data[i]['coins']}",True,"white")
                else:
                    self.info = self.font.render("Empty",True,"white")
                self.info = pygame.transform.scale_by(self.info, 0.7)

                if not rect.collidepoint(mouse_pos):
                    self.text.set_alpha(100)
                    self.info.set_alpha(100)
                else:
                    if clicked:
                        self.Data.setup(self.saved_data[i],i)
                        return i
                self.screen.blit(self.text,(581,150 +160*i))
                self.screen.blit(self.info,((SCREEN_WIDTH-self.info.width)/2,180 +160*i))
            
            pygame.display.update()
