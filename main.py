import pygame, random, math
from pygame import mixer

# initializing pygame
pygame.init()

# screen
screen = pygame.display.set_mode((800, 600))  # set size of screen

background = pygame.image.load("backround.jpg")
background = pygame.transform.scale(background, (800, 600))
# title and icon
pygame.display.set_caption("Space invaders")
icon = pygame.image.load('001-space-invaders.png')  # picture of space ship
pygame.display.set_icon(icon)

# Player icon
playerImg = pygame.image.load('001-space-invaders.png')
playerx = 368
playery = 468  # set player location
playerX_change = 0

# music
mixer.music.load("ytmp3free.cc_popular-phonk-edit-audios-1-youtubemp3free.org.mp3")
mixer.music.play(-1)


def player(x, y):
    screen.blit(icon, (x, y))


# enemy
enemyImg = []  # creating list so we can have multiple enemys in different places
enemyx = []
enemyy = []
enemyX_change = []
enemyY_change = []
enemyImg1 = pygame.image.load('alien.png')  # to add picture you just need to move it into the project file
num_of_enemies = 6
change = [0.1, 0.15, 0.2, -0.1, -0.15, -0.2]  # list of possible speeds, positive is right and negative is left
for i in range(num_of_enemies):
    enemyImg.append(pygame.transform.scale(enemyImg1, (32, 32)))  # adjust size of image
    enemyx.append(random.randint(0, 768))
    enemyy.append(random.randint(0, 150))
    enemyX_change.append(change[random.randint(0, 2)])
    enemyY_change.append(100)


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


# bullet
bulletImg = pygame.image.load('rectangle.png')
bulletx = 0
bullety = 468
bulletX_change = 0
bulletY_change = 1
bullet_state = "ready"  # means bullet is yet to be fired


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def isCollision(enemyx, enemyy, bulletx, bullety):
    distance = math.sqrt((math.pow(enemyx - bulletx, 2)) + (math.pow(enemyy - bullety, 2)))
    if distance < 27:
        return True
    else:
        return False


# score
score = 0
font = pygame.font.Font("freesansbold.ttf", 32)  # importing the font and the size

textX = 10
textY = 10


def show_score(x, y):
    score_value = font.render("score: " + str(score), True, (255, 255, 255))  # renders text and color
    screen.blit(score_value, (x, y))  # displays it  on screen


game_over = pygame.font.Font("freesansbold.ttf", 96)


def game_over_text():
    over_text = game_over.render("GAME OVER", True, (0, 0, 0))
    screen.blit(over_text, (100, 250))


# game loop
running = True
while running:  # infinite loop to constantly update the players location

    # RGb- red green blue
    screen.fill((0, 0, 0))
    # add background
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # if the click the x
            running = False
        if event.type == pygame.KEYDOWN:  # if they are pressing a key
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:  # if they are pressing 'a' key or left arrow
                playerX_change = -0.3
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:  # if they are pressing 'd' key or right arrow
                playerX_change = 0.3
            elif event.key == pygame.K_SPACE:
                if bullet_state == "ready":
                    bulletx = playerx
                    fire_bullet(bulletx, bullety)
        if event.type == pygame.KEYUP:  # if they are not pressing a key
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_a or event.key == pygame.K_d:
                playerX_change = 0

    playerx += playerX_change  # update players horisontal location

    if playerx <= 0:  # if player goes to far left so that there x co-ordinate =0
        playerx = 0  # makes sure player cant go off the scree
    elif playerx >= 768:  # if player to far right(not 800 because of image size)
        playerx = 768

    if bullety <= 0:  # if it goes off the screen
        bullet_state = "ready"  # can now fire again
        bullety = 468  # sets y to the sameposition as the player

    for i in range(num_of_enemies):

        if enemyy[i] > 468:
            for j in range(num_of_enemies):
                enemyy[j] = 2000  # makes each enemy dissapear
            game_over_text()
            break
        enemyx[i] += enemyX_change[i]  # update enemy's horisontal location
        if enemyx[i] >= 768:
            enemyX_change[i] = change[
                random.randint(3, 5)]  # when it hits the edge it moves the opposite way at a random speed
            enemyy[i] += enemyY_change[i]  # enemy moves down when it hits side
        elif enemyx[i] <= 0:
            enemyX_change[i] = change[random.randint(0, 2)]
            enemyy[i] += enemyY_change[i]

        collision = isCollision(enemyx[i], enemyy[i], bulletx, bullety)
        if collision:
            bullety = 468
            bullet_state = "ready"
            score += 1
            shooting = False
            enemyx[i] = random.randint(0, 768)
            enemyy[i] = random.randint(0, 150)

        enemy(enemyx[i], enemyy[i], i)

    if bullet_state == "fire":  # if fire_bullet has been run/ they have pressed spaced
        fire_bullet(bulletx, bullety)
        bullety -= bulletY_change  # moves bullet up

    show_score(textX, textY)

    player(playerx, playery)
    pygame.display.update()
