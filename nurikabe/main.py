# To run, go up one directory and run python -m nurikabe.main

import logging
import argparse
import pygame

from .nurikabe import Nurikabe


def str_to_bool(boolean_like_string: str) -> bool:
    """
    Convert a string representation to a bool. This assumes that the user inputs one of "true", "yes", "1' to represent
    True.
    """
    first_char = boolean_like_string[0].lower()
    return first_char in ('y', 't', '1')


def parse_command_line_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Play Nurikabe')
    parser.add_argument('--level', default=1, type=int,
                        help='Which level to play (default: %(default)s)')
    parser.add_argument('--log-level', default='info', choices=('debug', 'info'),
                        help='Log level (default: %(default)s)')
    parser.add_argument('--use-solver', default=True, type=str_to_bool,
                        help='Should the solver be used (default: %(default)s)')
    parser.add_argument('--include-grid-numbers', default=False, action='store_true',
                        help='If activated, the grid numbers are displayed for easier debugging (default: %(default)s)')
    return parser.parse_args()


def main() -> None:
    args = parse_command_line_args()
    log_level = {'debug': logging.DEBUG, 'info': logging.INFO}[args.log_level]
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s:%(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    pygame.init()
    Nurikabe(level_number=args.level, should_use_solver=args.use_solver,
             should_include_grid_numbers=args.include_grid_numbers)


if __name__ == '__main__':
    main()
