import pygame, sys, random, time, math

pygame.init()

WIDTH, HEIGHT = 800, 600
bar_height = 50

surface = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_INCREMENT = 400 #BIGGER NUMBER EASIER IT IS
TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 30

LIVES = 10

LABEL_FONT = pygame.font.SysFont("comicsans", 24)

class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2 #PER FRAME
    COLOR = "red"
    COLOR2 = "white"

    def __init__(self, x,y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True

    def update(self):
        if self.size+ self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False

        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

    def draw(self, surface):
        pygame.draw.circle(surface, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(surface, self.COLOR2, (self.x, self.y), self.size*0.8)
        pygame.draw.circle(surface, self.COLOR, (self.x, self.y), self.size*0.6)
        pygame.draw.circle(surface, self.COLOR2, (self.x, self.y), self.size*0.4)

    def collide(self, x , y):
        distance = math.sqrt((self.x - x)**2 + (self.y - y)**2) # pythagoras distance from cursor to centre of circle
        return distance <= self.size

def draw(surface, targets):
    surface.fill((0,25,40))

    for target in targets:
        target.draw(surface)


def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000)/10)
    seconds = int(round(secs % 60))
    minutes = int(secs // 60)

    return f"{minutes:02d}:{seconds:02d}:{milli}"

def calc_accuracy(clicks, targets_pressed):
    ret = 0 if targets_pressed == 0 else round(targets_pressed / clicks *100)
    return ret

def draw_top_bar(surface, elapsed_time, targets_pressed, misses,clicks):
    pygame.draw.rect(surface, "grey", (0,0, WIDTH, bar_height))
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")

    speed = round(targets_pressed/ elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")

    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")

    lives_label = LABEL_FONT.render(f"Lives: {LIVES- misses}", 1, "black")

    accuracy_label = LABEL_FONT.render(f"Accuracy: {calc_accuracy(clicks, targets_pressed)}%", 1, "black")

    surface.blit(time_label, (5,5))
    surface.blit(speed_label, (200, 5))
    surface.blit(hits_label, (390, 5))
    surface.blit(accuracy_label, (500, 5))
    surface.blit(lives_label, (700, 5))

def end_screen(surface, elapsed_time, targets_pressed, clicks):
    surface.fill("black")
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "white")

    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")

    lost_label = LABEL_FONT.render("Your number of lives reached zero", 1, "white")

    hits_label = LABEL_FONT.render(f"Targets hit: {targets_pressed}", 1, "white")

    accuracy_label = LABEL_FONT.render(f"Accuracy: {calc_accuracy(clicks, targets_pressed)}%", 1, "white")

    surface.blit(lost_label, (get_middle(lost_label), 5))
    surface.blit(time_label, (get_middle(time_label), 100))
    surface.blit(speed_label, (get_middle(speed_label), 200))
    surface.blit(hits_label, (get_middle(hits_label), 300))
    surface.blit(accuracy_label, (get_middle(accuracy_label), 400))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                #quit()
                sys.exit()


def get_middle(surface):
    return WIDTH/2 - surface.get_width()/2

def main():
    run = True
    targets = []
    clock = pygame.time.Clock()

    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    while run:
        clock.tick(60)
        click = False
        elaspsed_time = time.time()-start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(bar_height + TARGET_PADDING, HEIGHT - TARGET_PADDING)
                target = Target(x,y)
                targets.append(target)

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks +=1
                mouse_pos = pygame.mouse.get_pos()


        for target in targets:
            target.update()

            if target.size <= 0:
                targets.remove(target)
                misses +=1

            if click and target.collide(*mouse_pos):
                targets.remove(target)
                targets_pressed +=1

            if misses >= LIVES:
                end_screen(surface, elaspsed_time, targets_pressed, clicks)

        draw(surface, targets)
        draw_top_bar(surface, elaspsed_time, targets_pressed, misses,clicks)
        pygame.display.update()

if __name__ == "__main__":
    main()