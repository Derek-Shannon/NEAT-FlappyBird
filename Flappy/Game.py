import pygame, neat
import random

# Assume that objects.py contains classes Base, Score, Grumpy, and Pipe
from Flappy.objects import *

class Flappy:
    SCREEN = WIDTH, HEIGHT = 288, 512
    FPS = 60

    def __init__(self, window):
        self.win = window
        self.clock = pygame.time.Clock()

        # Load assets
        self.bg1 = pygame.image.load('Flappy/Assets/background-day.png')
        self.bg2 = pygame.image.load('Flappy/Assets/background-night.png')
        self.bg = random.choice([self.bg1, self.bg2])
        
        self.im_list = [pygame.image.load('Flappy/Assets/pipe-green.png'), pygame.image.load('Flappy/Assets/pipe-red.png')]
        self.pipe_img = random.choice(self.im_list)

        self.gameover_img = pygame.image.load('Flappy/Assets/gameover.png')
        self.flappybird_img = pygame.image.load('Flappy/Assets/flappybird.png')
        self.flappybird_img = pygame.transform.scale(self.flappybird_img, (200, 80))

        # Load sounds
        self.die_fx = pygame.mixer.Sound('Flappy/Sounds/die.wav')
        self.hit_fx = pygame.mixer.Sound('Flappy/Sounds/hit.wav')
        self.point_fx = pygame.mixer.Sound('Flappy/Sounds/point.wav')
        self.swoosh_fx = pygame.mixer.Sound('Flappy/Sounds/swoosh.wav')
        self.wing_fx = pygame.mixer.Sound('Flappy/Sounds/wing.wav')

        # Game objects
        self.pipe_group = pygame.sprite.Group()
        self.base = Base(self.win)
        self.score_img = Score(self.WIDTH // 2, 50, self.win)
        self.grumpy = Grumpy(self.win)

        # Game variables
        self.base_height = 0.80 * self.HEIGHT
        self.speed = 0
        self.game_started = False
        self.game_over = False
        self.restart = False
        self.score = 0
        self.start_screen = True
        self.pipe_pass = False
        self.pipe_frequency = 1600
        self.last_pipe = pygame.time.get_ticks() - self.pipe_frequency
        
    def loop(self):
        running = True
        while running:
            self.win.blit(self.bg, (0, 0))

            if self.start_screen:
                self.speed = 0
                self.grumpy.draw_flap()
                self.base.update(self.speed)
                self.win.blit(self.flappybird_img, (40, 50))
            else:
                if self.game_started and not self.game_over:
                    next_pipe = pygame.time.get_ticks()
                    if next_pipe - self.last_pipe >= self.pipe_frequency:
                        y = self.base_height // 2
                        pipe_pos = random.choice(range(-100, 100, 4))
                        height = y + pipe_pos

                        top = Pipe(self.win, self.pipe_img, height, 1)
                        bottom = Pipe(self.win, self.pipe_img, height, -1)
                        self.pipe_group.add(top)
                        self.pipe_group.add(bottom)
                        self.last_pipe = next_pipe

                self.pipe_group.update(self.speed)
                self.base.update(self.speed)
                self.grumpy.update()
                self.score_img.update(self.score)

                if pygame.sprite.spritecollide(self.grumpy, self.pipe_group, False) or self.grumpy.rect.top <= 0:
                    self.game_started = False
                    if self.grumpy.alive:
                        self.hit_fx.play()
                        self.die_fx.play()
                    self.grumpy.alive = False
                    self.grumpy.theta = self.grumpy.vel * -2

                if self.grumpy.rect.bottom >= self.base_height:
                    self.speed = 0
                    self.game_over = True

                if len(self.pipe_group) > 0:
                    p = self.pipe_group.sprites()[0]
                    if self.grumpy.rect.left > p.rect.left and self.grumpy.rect.right < p.rect.right and not self.pipe_pass and self.grumpy.alive:
                        self.pipe_pass = True

                    if self.pipe_pass:
                        if self.grumpy.rect.left > p.rect.right:
                            self.pipe_pass = False
                            self.score += 1
                            self.point_fx.play()

            if not self.grumpy.alive:
                self.win.blit(self.gameover_img, (50, 200))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_screen:
                        self.game_started = True
                        self.speed = 2
                        self.start_screen = False
                        self.game_over = False
                        self.last_pipe = pygame.time.get_ticks() - self.pipe_frequency
                        self.pipe_group.empty()
                        self.speed = 2
                        self.score = 0
                    if self.game_over:
                        self.start_screen = True
                        self.grumpy = Grumpy(self.win)
                        self.pipe_img = random.choice(self.im_list)
                        self.bg = random.choice([self.bg1, self.bg2])
            self.clock.tick(self.FPS)
            pygame.display.update()     
    def loopAI(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        running = True
        while running:
            self.win.blit(self.bg, (0, 0))
            
            # Get the closest pipes
            closest_pipe = None
            min_dist = float('inf')
            for pipe in self.pipe_group:
                dist = pipe.rect.right - self.grumpy.rect.left
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    closest_pipe = pipe
            
            if closest_pipe is not None:
                bottom_pipe_height = closest_pipe.rect.bottom
                bottom_pipe_x = closest_pipe.rect.x
            else:
                bottom_pipe_x = 1000
                bottom_pipe_height = self.HEIGHT

            # AI
            relX = bottom_pipe_x - self.grumpy.rect.x
            relY =  bottom_pipe_height+100 - self.grumpy.rect.y
            output = net.activate((
                relX,
                relY,
                self.grumpy.vel
            ))
            #print(relX,relY,self.grumpy.vel)
            decision = output[0]
        
            if decision > 0.5:
                self.grumpy.flap()
            

            if self.start_screen:
                self.speed = 0
                self.grumpy.draw_flap()
                self.base.update(self.speed)
                self.win.blit(self.flappybird_img, (40, 50))
            else:
                if self.game_started and not self.game_over:
                    next_pipe = pygame.time.get_ticks()
                    if next_pipe - self.last_pipe >= self.pipe_frequency:
                        y = self.base_height // 2
                        pipe_pos = random.choice(range(-100, 100, 4))
                        height = y + pipe_pos

                        top = Pipe(self.win, self.pipe_img, height, 1)
                        bottom = Pipe(self.win, self.pipe_img, height, -1)
                        self.pipe_group.add(top)
                        self.pipe_group.add(bottom)
                        self.last_pipe = next_pipe

                self.pipe_group.update(self.speed)
                self.base.update(self.speed)
                self.grumpy.update()
                self.score_img.update(self.score)

                if pygame.sprite.spritecollide(self.grumpy, self.pipe_group, False) or self.grumpy.rect.top <= 0:
                    genome.fitness += self.score*2
                    return #calc fitness

                if self.grumpy.rect.bottom >= self.base_height:
                    self.speed = 0
                    self.game_over = True
                    genome.fitness += self.score*2
                    return #calc fitness

                if len(self.pipe_group) > 0:
                    p = self.pipe_group.sprites()[0]
                    if self.grumpy.rect.left > p.rect.left and self.grumpy.rect.right < p.rect.right and not self.pipe_pass and self.grumpy.alive:
                        self.pipe_pass = True

                    if self.pipe_pass:
                        if self.grumpy.rect.left > p.rect.right:
                            self.pipe_pass = False
                            self.score += 1
                            self.point_fx.play()

            if not self.grumpy.alive:
                self.win.blit(self.gameover_img, (50, 200))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        genome.fitness += self.score*2
                        return #calc fitness

            if self.start_screen:
                self.game_started = True
                self.speed = 2
                self.start_screen = False
                self.game_over = False
                self.last_pipe = pygame.time.get_ticks() - self.pipe_frequency
                self.pipe_group.empty()
                self.speed = 2
                self.score = 0
            #self.clock.tick(self.FPS)                
            pygame.display.update()
            genome.fitness += 0.003

# Create an instance of the Flappy class and start the game loop
if __name__ == "__main__":
    pygame.init()
    flappy_game = Flappy(pygame.display.set_mode(Flappy.SCREEN, pygame.NOFRAME))
    flappy_game.loopAI(0)
    pygame.quit()
