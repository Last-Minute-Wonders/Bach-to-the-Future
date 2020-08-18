
BLACK= 0, 0, 0
WHITE= 255, 255, 255
GREY= 127, 127, 127

RED= 255, 0, 0
GREEN= 0, 255, 0
BLUE= 0, 0, 255

CYAN= 0, 255, 255
MAGENTA= 255, 0, 255
YELLOW= 255, 255, 0

if __name__ == "__main__":
    import pygame
    from sys import exit


    pygame.init()
    screen= pygame.display.set_mode((450, 300))
    screen.fill(YELLOW)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: exit()


