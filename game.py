import pygame
import boids
import time
from random import randint


class Game(object):

    def __init__(self):
        pygame.display.set_caption('Boids')
        width, height = (800, 800)
        self.screen = pygame.display.set_mode((width, height))
        self.env = boids.Environment(width, height)

    def add_boids(self, number_of_boids):
        for x in range(number_of_boids):
            self.env.add_boid(self.env, x=randint(0, 600), y=randint(0, 600), speed=10, angle=randint(0, 360), awareness=600, separation=200)

    def run_game(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif (event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.KEYDOWN):
                    if (event.type == pygame.MOUSEBUTTONDOWN):
                        print "MOUSE"
            self.env.update()
            self.screen.fill(self.env.colour)

            for p in self.env.boids:
                pygame.draw.circle(self.screen, p.colour, (int(p.x), int(p.y)), p.size, p.thickness)
            pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.add_boids(30)
    game.run_game()
