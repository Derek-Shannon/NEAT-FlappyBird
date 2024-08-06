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
    width, height = 700, 500
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pong")
    

    for i, (genome_id1, genome1) in enumerate(genomes):
        print(round(i/len(genomes) * 100), end=" ")
        genome1.fitness = 0
        pong = PongGame(win, width, height)

        force_quit = pong.train_ai(genome1, config, draw=True)
        if force_quit:
            quit()


def run_neat(config):
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



def test_best_network(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    #DLS


    width, height = 700, 500
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pong")
    pong = Flappy(win, width, height)
    pong.test_ai(winner_net)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    #train
        #run_neat(config)
    #test_best_network(config)