import pygame
from settings import *

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Arkanoid")
    clock = pygame.time.Clock()

    running = True
    while running:
        # Main Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # Press "close" button
                running = False

        screen.fill(BLACK)

        pygame.display.flip()   # Screen Update
        clock.tick(FPS)         # FPS (Frames Per Second)

    pygame.quit()

if __name__ == "__main__":
    main()
