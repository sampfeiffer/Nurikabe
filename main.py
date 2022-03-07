import logging
import pygame

from nurikabe import Nurikabe


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    pygame.init()
    Nurikabe(level_number=1, should_use_solver=True)


if __name__ == '__main__':
    main()
