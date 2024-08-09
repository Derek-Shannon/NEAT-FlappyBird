import pygame, neat
import random

# Assume that objects.py contains classes Base, Score, Grumpy, and Pipe
from Flappy.objects import *

class Flappy:
    SCREEN = WIDTH, HEIGHT = 288, 512
    FPS = 60 #default 60tps

    def __init__(self, window):
        self.win = window
        self.cycles = 0
        self.clock = pygame.time.Clock()

        # Load assets
        self.bg1 = pygame.image.load('Flappy/Assets/background-day.png')
        self.bg2 = pygame.image.load('Flappy/Assets/background-night.png')
        self.bg = self.bg1 #random.choice([self.bg1, self.bg2])
        
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
        self.grumpys = []
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
        self.pipe_frequency = 100
        self.last_pipe = self.cycles - self.pipe_frequency
    def reset_game(self):
        self.cycles = 0
        self.pipe_group = pygame.sprite.Group()
        self.base = Base(self.win)
        self.grumpys = []
        self.game_started = True
        self.speed = 2
        self.start_screen = False
        self.game_over = False
        self.last_pipe = self.cycles - self.pipe_frequency
        self.pipe_group.empty()
        self.speed = 2
        self.score = 0
        print("restart!!!")
    def start_AI(self, genomes, config):
        for i, (genome_id1, genome) in enumerate(genomes):
            self.grumpys.append(Grumpy(self.win))
            genome.fitness = 0
        running = True
        while running:
            self.win.blit(self.bg, (0, 0))
            aliveCount = 0
            for i, (genome_id1, genome) in enumerate(genomes):
                if self.grumpys[i].alive:
                    self.loopAI(genome, config, self.grumpys[i])
                    aliveCount += 1
            if aliveCount is 0 or self.score > 99:
                running = False
            
            self.pipe_group.update(self.speed)
            self.base.update(self.speed)
            self.score_img.update(self.score)

            self.clock.tick(self.FPS)                
            pygame.display.update()
            self.cycles += 1
        self.reset_game()
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
                    next_pipe = self.cycles
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
                        self.cycles = 0
                        self.last_pipe = self.cycles - self.pipe_frequency
                        self.pipe_group.empty()
                        self.speed = 2
                        self.score = 0
                    if self.game_over:
                        self.start_screen = True
                        self.grumpy = Grumpy(self.win)
                        self.pipe_img = random.choice(self.im_list)
                        self.bg = self.bg1 #random.choice([self.bg1, self.bg2])
            self.clock.tick(self.FPS)
            self.cycles += 1
            pygame.display.update()     
    def loopAI(self, genome, config, grumpy):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        # Get the closest pipes
        closest_pipe = None
        min_dist = float('inf')
        for pipe in self.pipe_group:
            dist = pipe.rect.right - grumpy.rect.left
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
        relX = bottom_pipe_x - grumpy.rect.x + 50
        relY =  bottom_pipe_height+100 - grumpy.rect.y
        output = net.activate((
            relX,
            relY
        ))
        #print(relX,relY)
        decision = output[0]
    
        if decision > 0.5:
            grumpy.flap()
        
        if self.game_started:
            next_pipe = self.cycles
            time_since_last_pipe = next_pipe - self.last_pipe

            if time_since_last_pipe >= self.pipe_frequency:
                y = self.base_height // 2
                pipe_pos = random.choice(range(-100, 100, 4))
                height = y + pipe_pos

                top = Pipe(self.win, self.pipe_img, height, 1)
                bottom = Pipe(self.win, self.pipe_img, height, -1)
                self.pipe_group.add(top)
                self.pipe_group.add(bottom)
                self.last_pipe = next_pipe
            grumpy.update()

            if pygame.sprite.spritecollide(grumpy, self.pipe_group, False) or grumpy.rect.top <= 0:
                genome.fitness += self.score*2
                grumpy.alive = False

            if grumpy.rect.bottom >= self.base_height:
                genome.fitness += self.score*2
                grumpy.alive = False

            if len(self.pipe_group) > 0:
                p = self.pipe_group.sprites()[0]
                if grumpy.rect.left > p.rect.left and grumpy.rect.right < p.rect.right and not self.pipe_pass and grumpy.alive:
                    self.pipe_pass = True

                if self.pipe_pass:
                    if grumpy.rect.left > p.rect.right:
                        self.pipe_pass = False
                        self.score += 1
                        self.point_fx.play()
        if self.score >= 100:
            grumpy.alive = False
        if not grumpy.alive:
            genome.fitness += self.score*2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    genome.fitness += self.score*2
                    grumpy.alive = False

        if self.start_screen:
            self.game_started = True
            self.speed = 2
            self.start_screen = False
            self.game_over = False
            self.last_pipe = self.cycles - self.pipe_frequency
            self.pipe_group.empty()
            self.speed = 2
            self.score = 0
        genome.fitness += 0.003

# Create an instance of the Flappy class and start the game loop
if __name__ == "__main__":
    pygame.init()
    flappy_game = Flappy(pygame.display.set_mode(Flappy.SCREEN, pygame.NOFRAME))
    flappy_game.loopAI(0)
    pygame.quit()
