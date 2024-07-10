import pygame
from game import Game


def main():
    game = Game()

    while game.running:
        game.main_loop()


if __name__ == "__main__":
    main()
