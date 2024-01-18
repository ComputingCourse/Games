

#===============================TikTacToe====================================#
#                  By charlie Milne:  Reading England



import pygame,sys, time, random

pygame.init()
screen = pygame.display.set_mode((600,600))
#screen.fill('grey')
pygame.display.set_caption("TicTakToe")
clock = pygame.time.Clock()

def get_row( mousey):
    if mousey >= 0 and mousey <= 200:  # row 1
        grid_pos = 0
    elif mousey > 200 and mousey <= 400:  # row 2
        grid_pos = 1
    elif mousey > 400 and mousey <= 600:  # row 3
        grid_pos = 2
    return grid_pos

def get_collum(mousex):
    if mousex >= 0 and mousex <= 200: collum = 0
    elif mousex > 200 and mousex <= 400: collum = 1
    elif mousex > 400 and mousex <= 600: collum = 2
    return collum

def winnable(GRID):
    location = ""
    for row in range(3):
        for collum in range(3):
            GRID2 = GRID
            if GRID2[row][collum] == "":
                GRID2[row][collum] = "o"
                if check_win(GRID2):
                    return (row,collum)
                GRID2[row][collum] = "x"
                if check_win(GRID2):
                    return (row,collum)
                GRID2[row][collum] = ""
    return location



def check_win(GRID):
    win = False
    for i in range(3):
        if GRID[i][0] == GRID[i][1] and GRID[i][0] == GRID[i][2] and GRID[i][0] != "":
            win = True  # check horizontal win
        elif GRID[0][i] == GRID[1][i] and GRID[0][i] == GRID[2][i] and GRID[0][i] != "":
            win = True  # check vertical win
    if GRID[0][0] == GRID[1][1] and GRID[0][0] == GRID[2][2] and GRID[0][0] != "":
        win = True
    if GRID[0][2] == GRID[1][1] and GRID[0][2] == GRID[2][0] and GRID[0][2] != "":
        win = True

    return win
GRID = [["","",""],
        ["","",""],
        ["","",""]]

def start():
    global GRID,turn,win,my_font,choice
    GRID = [["","",""],
            ["","",""],
            ["","",""]]
    turn = 0
    win = False
    my_font = pygame.font.SysFont("comicsans", 25)
    screen.fill('grey')
    choice = ""
    message = my_font.render("who would you like to play against:", 1, (0, 0, 0))
    screen.blit(message, (130, 200))
    message = my_font.render("Yourself", 1, (0, 150, 0))
    screen.blit(message, (180, 300))
    message = my_font.render("or  an ", 1, (0, 0, 0))
    screen.blit(message, (300, 300))
    message = my_font.render(" AI", 1, (0, 150, 0))
    screen.blit(message, (380, 300))
    pygame.display.update()
    while not choice:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousex, mousey = pygame.mouse.get_pos()
                if (240 - mousex)**2 <=400 and (315-mousey)**2 <=400:
                    choice = "1v1"
                elif (400 -mousex)**2 <=400 and (315-mousey)**2 <=400:
                    choice = "AI"
    grid_surface = pygame.image.load("OIP.jpg")
    grid_surface = pygame.transform.scale(grid_surface, (600, 600))
    screen.blit(grid_surface, (0,0))
    my_font = pygame.font.SysFont("monospace", 50)
start()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            start()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousex, mousey = pygame.mouse.get_pos()
            row = get_row( mousey)
            collum = get_collum(mousex)
            if choice == "1v1":
                if GRID[row][collum] == "":
                    player = "x" if turn % 2 == 0 else "o"
                    GRID[row][collum] = player
                    img = "cross.jpg" if player == "x" else "circle.jpg"
                    img = pygame.image.load(img)
                    img = pygame.transform.scale(img, (150,150))
                    screen.blit(img, (collum*200 + 25, row*200 + 25))
                    turn += 1

                    win = check_win(GRID)
            else:#against AI

                #player turn
                if GRID[row][collum] == "":
                    player = "x" if turn % 2 == 0 else "o"
                    GRID[row][collum] = player
                    img = "cross.jpg" if player == "x" else "circle.jpg"
                    img = pygame.image.load(img)
                    img = pygame.transform.scale(img, (150, 150))
                    screen.blit(img, (collum * 200 + 25, row * 200 + 25))
                    turn += 1
                win = check_win(GRID)
                #AI turn
                pygame.display.update()
                if not win and turn < 9:
                    if turn %2 == 1:
                        time.sleep(0.4)
                        player = "o"
                        location = winnable(GRID)
                        if location:
                            row, collum = location
                        else:
                            valid = False
                            while not valid:
                                row, collum = random.randint(0,2), random.randint(0,2)
                                if GRID[row][collum] == "":
                                    valid = True
                        GRID[row][collum] = "o"
                        img = "circle.jpg"
                        img = pygame.image.load(img)
                        img = pygame.transform.scale(img, (150, 150))
                        screen.blit(img, (collum * 200 + 25, row * 200 + 25))
                        turn += 1

            win = check_win(GRID)
            pygame.display.update()
            if win:
                time.sleep(0.5)
                screen.fill('grey')
                victory_message =my_font.render(player+" won the game",1,(0,0,0))
                screen.blit(victory_message,(100,250))
            elif turn == 9:
                time.sleep(0.5)
                screen.fill('grey')
                victory_message = my_font.render("Its a draw", 1, (0, 0, 0))
                screen.blit(victory_message, (150, 250))

    pygame.display.update()
































    # sets frame ceilling at  60fps