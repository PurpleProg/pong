import pygame
from game import Game


def main():
    game = Game()

    while game.running:
        game.main_loop()
        # debug stack
        for state in game.stack:
            print(' >', type(state).__name__, end='')
        print('')


if __name__ == "__main__":
    main()
