# Flappy Bird AI using NEAT

This project employs an artificial intelligence that is trained to play Flappy Bird through the NEAT (NeuroEvolution of Augmenting Topologies) algorithm. The game was developed using Python and Pygame, and the AI is taught to play the game through the evolution of neural networks across generations.

## Features

- **Flappy Bird Gameplay**: The classic Flappy Bird game implemented in Pygame.
- **NEAT Algorithm**: Uses the NEAT algorithm to evolve a neural network that controls the bird.
- **Generation Tracking**: Tracks the number of generations, score, and the number of birds alive.
- **Save Best Model**: Saves the best-performing model using Python's `pickle` module.

## Getting Started

### Prerequisites

To run this project, you'll need:

- Python 3.6 or higher
- Pygame
- NEAT-Python

You can install the necessary packages using pip:

```bash
pip install pygame neat-python
```

### Installation
```bash
git clone https://github.com/ddepablo13/AIFlappyBird.git
```

### Add your Flappy Bird sprites:
Place your bird, pipe, floor, and background images in the assets/ directory.
Ensure the filenames match those used in the code: sprite1.png, sprite2.png, sprite3.png, pipe.png, floor.png, and sky.png.

### Run the game:
```bash
python flappy_bird.py
```

### Configuration
The NEAT algorithm is configured via a configuration file named config-NEAT.txt. You can modify this file to adjust parameters such as the population size, mutation rates, and fitness thresholds.

## How It Works
### Flappy Bird Game: 
The game consists of a bird that must navigate through pipes by jumping to avoid hitting them. The goal is to get as far as possible without colliding with a pipe or falling to the ground.

### NEAT Algorithm:
The NEAT algorithm evolves a population of neural networks over generations. Each neural network controls a bird, and its performance is evaluated based on how far the bird progresses in the game.

### Fitness Function:
The fitness of each bird is determined by the distance it travels through the pipes. Birds that survive longer receive higher fitness scores, which increases their chances of passing their genes (neural network weights) to the next generation.

## Files
### flappy_bird.py:
Main script that runs the game and implements the NEAT algorithm.
### config-NEAT.txt:
Configuration file for the NEAT algorithm.
### assets/: 
Directory containing game sprites (bird, pipes, floor, background).

## Customization
### Adjust Difficulty:
You can adjust the game's difficulty by modifying the gap between pipes and the speed at which the pipes move.

## Future Improvements
Visualize the progression of NEAT: Incorporate a visualization tool to monitor the development of neural networks.
Experiment with various neural network structures and NEAT parameters to enhance performance of AI.
