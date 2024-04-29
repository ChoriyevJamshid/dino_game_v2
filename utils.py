from pygame import Surface
import cv2
# from app import Console
import pygame
pygame.init()

image = cv2.imread('screenshots/1.png')
print(image)


window = pygame.display.set_mode((800, 600))

surface = Surface((800, 600))
surface.fill("grey")
surface.set_alpha(200)

run = True
ticks = pygame.time.get_ticks()
while run:
    window.fill("white")
    window.blit(image, (0, 0))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
    pygame.time.Clock().tick(60)

pygame.quit()



