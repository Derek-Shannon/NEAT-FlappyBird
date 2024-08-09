from Flappy import Game
import pygame
import neat
import os
import time
import pickle

class GameDriver:
    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode(Game.Flappy.SCREEN, pygame.NOFRAME)
        self.game = Game.Flappy(self.win)
    def train_ai(self, genome, config):
        start_time = time.time()
        
        self.game.loopAI(genome)

        duration = time.time() - start_time

def eval_genomes(genomes, config):
    """
    Run each genome against eachother one time to determine the fitness.
    """
    win = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))  

    for i, (genome_id1, genome) in enumerate(genomes):
        genome.fitness = 0
        game = Game.Flappy(pygame.display.set_mode(Game.Flappy.SCREEN, pygame.NOFRAME))
        game.loopAI(genome, config)
        print(i, genome.fitness)

def train_ai(config):
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-85')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(1))
    #DLS
    node_names = {-1:'A', -2: 'B'}
    winner = p.run(eval_genomes, 50)

    
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)



def play_best_ai(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    #DLS


    game = Game.Flappy(pygame.display.set_mode(Game.Flappy.SCREEN, pygame.NOFRAME))
    winner.fitness = 0
    game.loopAI(winner, config)
def play_game():
    game = Game.Flappy(pygame.display.set_mode(Game.Flappy.SCREEN, pygame.NOFRAME))
    game.loop()

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    print("1)play solo")
    print("2) play Best AI")
    print("3) train AI")
    #input = input("Mode Selection: ")
    input = 2
    if input is 1:
        play_game()
    elif input is 2:
        play_best_ai(config)
    else:
        train_ai(config)