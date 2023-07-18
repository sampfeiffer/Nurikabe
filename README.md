# Nurikabe
## What is Nurikabe
Nurikabe is a Japanese logic puzzle. The puzzle is presented as a rectangular grid of square cells, some of which contain a number clue. Connected white cells form "gardens". Connected black cells form "walls". The goal of the game is to correctly identify each non-clue cell as a wall or a garden.

Here is an example of a Nurikabe puzzle:

![unsolved_nurikabe_example](https://github.com/sampfeiffer/nurikabe/assets/10815714/6e7fcdc0-c16d-4715-8f14-2d8796f757bc)

Each Nurikabe puzzle has a unique solution that meets the criteria below. Note that in Nurikabe, two cells are considered connected if they are horizontally or vertically adjacent; diagonal adjacency does not matter.

Solution criteria:
1. Each clue cell is a part of a garden whose size equals the clue number.
2. Each garden must contain exactly one clue.
3. All walls must be connected.
4. There cannot be a 2x2 section of walls.

For convenience, cells can be marked with a dot to represent that they are part of a garden.

Below is an example of a solved Nurikabe puzzle

![solved_nurikabe_example](https://github.com/sampfeiffer/nurikabe/assets/10815714/978f09e8-631b-402e-b343-ba7aaab93d1b)


## Features
This code is a Python implementation of Nurikabe using pygame as the user interface. This implementation also provides a solver. Note that the solver can currently handle easy to medium puzzles, but cannot yet handle all puzzles.

![nurikabe_gui](https://github.com/sampfeiffer/nurikabe/assets/10815714/e0ae11d6-b414-4397-9b50-7833b5401ffd)

## How to run the code
Using Python 3.x, run `main.py --help` to see the options
