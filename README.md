# AIN-2023-mapf
A project implementing cooperative multi-agent pathfinding using pygame as a visualization engine.

## Setup

This program has been tested with python 3.11, though it should reasonably work for earlier python versions where pygame and graphviz are compatible since typing was introduced. Needless to say, you must have a valid version of python installed in your system.

To run this project, you'll first need to install the required python modules using pip. Notably, you will need:
* pygame - A game engine built in python used for all the rendering and user interaction in this program
* graphviz - A graph visualization library

## Running the program

To run this program, you will first need a grid data file.

Grid data files are raw text files where every row indicates a row in the grid. The hash `#` character indicates a wall, a space ` ` indicates a walkable tile. Any lowercase character indicates the starting position of an agent. Any uppercase character indicates the respective goal of the agent.

A number of examples are available in the samples folder.

Once that file has been created. Run:
`python visualizer.py -f relative/path/to/grid.txt`
Replacing the relative path with the path to your grid file.

The visualizer has a number of useful options, you can find out about them using:
`python visualizer.py -h`

The controls for interaction within the visualizer itself are always visible at the bottom of the screen.