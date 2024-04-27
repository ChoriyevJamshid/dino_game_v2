
import pygame
pygame.init()


window = pygame.display.set_mode((800, 600))

box = pygame.image.load("assets/deserttileset/Objects/Crate.png").convert_alpha()
box = pygame.transform.scale(box, (100, 100))
box1 = pygame.transform.rotate(box, 10)
rect = box.get_rect(midbottom=(350, 250))
rect1 = box.get_rect(midbottom=(450, 250))
angle = 0

run = True
ticks = pygame.time.get_ticks()
while run:
    window.fill("white")

    window.blit(box, rect)
    pygame.draw.rect(window, (0, 255, 0), rect, 1)
    window.blit(box1, rect1)
    pygame.draw.rect(window, (0, 255, 0), rect1, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
    pygame.time.Clock().tick(60)

pygame.quit()
