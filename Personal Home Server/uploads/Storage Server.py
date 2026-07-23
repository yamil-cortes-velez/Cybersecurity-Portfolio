import pygame
import sys

# initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 480))
pygame.display.set_caption("Storage Server")
clock = pygame.time.Clock()

# change this to test upload or download until Pi arrives and I can test this on the actual Pi
mode = "download"

# load images
house_img = pygame.image.load(r"C:\Users\arcey\Desktop\Animation\House.png").convert_alpha()
server_image1 = pygame.image.load(r"C:\Users\arcey\Desktop\Animation\Server.png").convert_alpha()
server_image2 = pygame.image.load(r"C:\Users\arcey\Desktop\Animation\Server_Green.png").convert_alpha()

# load walk frames
walking_animation = [
    pygame.image.load(r"C:\Users\arcey\Desktop\Animation\walk_1.png").convert_alpha(),
    pygame.image.load(r"C:\Users\arcey\Desktop\Animation\walk_2.png").convert_alpha(),
    pygame.image.load(r"C:\Users\arcey\Desktop\Animation\walk_3.png").convert_alpha(),
    pygame.image.load(r"C:\Users\arcey\Desktop\Animation\walk_4.png").convert_alpha(),
]

# scale everything up
house_img = pygame.transform.scale(house_img, (128, 128))
server_image1 = pygame.transform.scale(server_image1, (128, 128))
server_image2 = pygame.transform.scale(server_image2, (128, 128))
walking_animation = [pygame.transform.scale(f, (128, 128)) for f in walking_animation]

# variables
if mode == "upload":
    repair_man_x = 100  # starts at house going right
else:
    repair_man_x = 600  # starts at server going left

repair_man_y  = 250
frame_index   = 0
frame_timer   = 0
flicker_timer = 0
use_green     = False
progress      = 0.0

font = pygame.font.SysFont("monospace", 22)

# game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # walk frame cycling
    frame_timer += 1
    if frame_timer >= 8:
        frame_timer = 0
        frame_index = (frame_index + 1) % 4

    # server light flicker
    flicker_timer += 1
    if flicker_timer >= 15:
        flicker_timer = 0
        use_green = not use_green

    # fake progress for now
    progress += 0.003
    if progress > 1.0:
        progress = 1.0

    # move the repair man
    if mode == "upload":
        repair_man_x += 2
        if repair_man_x >= 600:
            repair_man_x = 600
    elif mode == "download":
        repair_man_x -= 2
        if repair_man_x <= 100:
            repair_man_x = 100

    # draw background
    screen.fill((30, 30, 50))

    # draw house on the left
    screen.blit(house_img, (50, 220))

    # draw server on the right with flickering light
    if use_green:
        screen.blit(server_image2, (620, 220))
    else:
        screen.blit(server_image1, (620, 220))

    # draw the repair man, flip him if downloading
    if mode == "upload":
        screen.blit(walking_animation[frame_index], (repair_man_x, repair_man_y))
    elif mode == "download":
        flipped = pygame.transform.flip(walking_animation[frame_index], True, False)
        screen.blit(flipped, (repair_man_x, repair_man_y))

    # progress bar background then fill
    pygame.draw.rect(screen, (50, 50, 80), (50, 430, 700, 24))
    pygame.draw.rect(screen, (100, 200, 255), (50, 430, int(700 * progress), 24))

    # status text
    if mode == "upload":
        status = "Uploading...  4.2 MB/s"
    else:
        status = "Downloading...  4.2 MB/s"

    speed_text = font.render(status, True, (255, 255, 255))
    screen.blit(speed_text, (50, 400))

    pygame.display.flip()
    clock.tick(30)