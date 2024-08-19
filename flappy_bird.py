import pygame
import os
import time
import random
import neat
import pickle
#import visualize
pygame.font.init()
"""
Game Window
"""
WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("tahoma", 50)
END_FONT = pygame.font.SysFont("tahoma", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

"""
Loads and scales the bird sprite images used in the Flappy Bird game.
The `BIRDS_IMGS` list contains three scaled-up versions of the bird sprite images,
which are used to represent the different frames of the bird's animation.
"""
BIRD_SPRITES = ["sprite1.png", "sprite2.png", "sprite3.png"]
BIRDS_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("assets", sprite)))
              for sprite in BIRD_SPRITES]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("assets","pipe.png")))
FLOOR_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("assets","floor.png")))
SKY_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("assets","sky.png")))

'''
Generation of Flappy Birds
'''
GEN = 0


class Flappy:
    """
    Represents a bird in the Flappy Bird game.
    """
    IMGS = BIRDS_IMGS
    MAXROT = 25
    ROTV = 20
    ANITIME = 5
    
    def __init__(self, x, y):
        '''
        sets up the initial state of the bird, including its 
        position, velocity, and appearance.
        '''
        self.x, self.y = x, y
        self.tilt = self.tick_count = self.vel = self.img_count = self.height = 0
        self.height = y
        self.img = self.IMGS[0]

    def jump(self):
        """
        makes the bird jump by setting its velocity to a negative value, 
        which causes it to move upwards.
        """
        # Set the bird's velocity to a negative value to make it jump
        self.vel = -10.5
        # Set the bird's tilt to a negative value to make it tilt up
        self.tick_count = 0
        # Set the bird's height to its current position
        self.height = self.y

    def move(self):
        """
        updates the bird's position based on its current velocity and applies 
        gravity-like effects to simulate realistic movement.        
        """
        self.tick_count += 1
        
        # Calculate displacement using physics equation
        d = self.vel * self.tick_count + 0.5 * 3 * self.tick_count**2
        
        # Apply terminal velocity
        if d >= 16:
            d = 16 * (1 if d > 0 else -1)
        
        # Add extra downward acceleration
        if d < 0:
            d -= 2

        self.y += d

        # Update bird's tilt
        if d < 0 or self.y < self.height + 50:
            self.tilt = min(self.tilt + self.ROTV, self.MAXROT)
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTV
                       
    def draw(self, win):
        """
        handles the visual representation of the bird, 
        including animation and rotation effects.
        """
        self.img_count += 1
        
        # Determine which image to use based on animation time
        img_index = (self.img_count // self.ANITIME) % 4
        self.img = self.IMGS[img_index if img_index != 3 else 1]
        
        # Reset animation counter if needed
        if self.img_count >= self.ANITIME * 4:
            self.img_count = 0
  
        # Override image if bird is falling rapidly
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANITIME * 2

        # Rotate and position the bird
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)
        
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANITIME * 2
            
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)
        
    def get_mask(self):
        """
        Returns a mask representing the bird's shape.
        """
        return pygame.mask.from_surface(self.img)


class Pipe:
    """
    Represents a pipe in the Flappy Bird game.
    """
    GAP = 200
    VEL = 5
    
    def __init__(self, x):
        """
        Initializes a new Pipe object.
            Args:
            x (int): The initial x-coordinate of the pipe.
            
        Attributes:
            x (int): The current x-coordinate of the pipe.
            height (int): The height of the pipe.
            top (int): The y-coordinate of the top of the pipe.
            bot (int): The y-coordinate of the bottom of the pipe.
            TPIPE (pygame.Surface): The image of the top part of the pipe.
            BPIPE (pygame.Surface): The image of the bottom part of the pipe.
            passed (bool): Whether the bird has passed through the pipe.
        Methods:
            set_height(): Sets the height of the pipe randomly.
        """
        self.x = x
        self.height = 0
        
        self.top = 0
        self.bot = 0
        
        self.TPIPE = pygame.transform.flip(PIPE_IMG, False, True)
        self.BPIPE = PIPE_IMG
        
        self.passed = False
        self.set_height()
        
    def set_height(self):
        """
        Sets the height of the pipe randomly.
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.TPIPE.get_height()
        self.bot = self.height + self.GAP
        
    def move(self):
        """
        Moves the pipe to the left.
        """
        self.x -= self.VEL
        
    def draw(self, win):
        """
        Draws the pipe on the game window.
        Args:
            win (pygame.Surface): The game window surface.
        """
        win.blit(self.TPIPE, (self.x, self.top))
        win.blit(self.BPIPE, (self.x, self.bot))

    def collide(self, flappy, win):
        """
        Checks if the bird has collided with the pipe.
        
        Args:
            flappy (Bird): The bird object.
            win (pygame.Surface): The game window surface.
        
        Returns:
            bool: True if the bird has collided with the pipe, False otherwise.
        """
        flappy_mask = flappy.get_mask()
        top_mask = pygame.mask.from_surface(self.TPIPE)
        bot_mask = pygame.mask.from_surface(self.BPIPE)
        top_offset = (self.x - flappy.x, self.top - round(flappy.y))
        bot_offset = (self.x - flappy.x, self.bot - round(flappy.y))

        top_point = flappy_mask.overlap(top_mask, top_offset)
        bot_point = flappy_mask.overlap(bot_mask, bot_offset)
        
        if top_point or bot_point:
            return True
        
        return False
    
class Floor:
    """
    Represents the floor of the game window, which scrolls horizontally to create the illusion of movement.
    
    The `Floor` class is responsible for managing the position and drawing of the floor image on the game window. 
    It uses two copies of the floor image, which are moved horizontally to create a continuous scrolling effect.
    """
    VEL = 5
    WIDTH = FLOOR_IMG.get_width()
    IMG = FLOOR_IMG
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        Moves the base to the left.
        """
        # Move the first image to the left
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        # Reset the position of the base if it goes off the screen
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        # Reset the position of the base if it goes off the screen
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
            
    def draw(self, win):
        """
        Draws the base on the game window.
        Args:
            win (pygame.Surface): The game window surface.
        """
        # Draw the first image
        win.blit(self.IMG, (self.x1, self.y))
        # Draw the second image
        win.blit(self.IMG, (self.x2, self.y))
        
def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)
    
def draw_window(win, flappys, pipes, floor, score, gen, indpipe):
    """
    Draws the game window, including the flappy birds, pipes, floor, score, and generation information.
    
    Args:
        win (pygame.Surface): The game window surface to draw on.
        flappys (list): A list of Flappy objects representing the birds in the game.
        pipes (list): A list of Pipe objects representing the pipes in the game.
        floor (Floor): The floor object.
        score (int): The current score of the game.
        gen (int): The current generation of the game.
        indpipe (int): The index of the current pipe that the flappy birds are approaching.
    """
    #Flappy generation
    if gen == 0:
        gen = 1
    win.blit(SKY_IMG, (0, 0))
    
    # Draw the pipes
    for pipe in pipes:
        pipe.draw(win)
        
    # Draw the floor
    floor.draw(win)
    
    # Draw the flappys
    for flappy in flappys:
        # Draw lines from flappy to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), 
                                 (flappy.x+flappy.img.get_width()/2, flappy.y + flappy.img.get_height()/2), 
                                 (pipes[indpipe].x + pipes[indpipe].TPIPE.get_width()/2, pipes[indpipe].height), 5)
                pygame.draw.line(win, (255,0,0), 
                                 (flappy.x+flappy.img.get_width()/2, flappy.y + flappy.img.get_height()/2), 
                                 (pipes[indpipe].x + pipes[indpipe].BPIPE.get_width()/2, pipes[indpipe].bottom), 5)
            except IndexError:
                pass
        # Draw flappy
        flappy.draw(win)
        
    # Draw the score
    score_txt = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_txt, (WIN_WIDTH - 10 - score_txt.get_width(), 10))
    
    # Draw the generation
    score_txt = STAT_FONT.render("Generation: " + str(gen-1),1,(255,255,255))
    win.blit(score_txt, (10, 10))
    
    # Draw alive flappys
    score_txt = STAT_FONT.render("Alive: " + str(len(flappys)),1,(255,255,255))
    win.blit(score_txt, (10, 725))
    
        
    # Update the display
    pygame.display.update()
    

def fitness(genomes, config):
    """
    Evaluates the fitness of a population of Flappy Bird agents using a NEAT neural network.
    
    This function is the main loop of the Flappy Bird game simulation. 
    It creates a population of Flappy Bird agents, each controlled by a NEAT neural network. 
    The agents are evaluated based on their ability to navigate through the pipes, 
    with the goal of maximizing their score. 
    The function updates the agents' positions, checks for collisions, and adds new pipes as the game progresses. 
    The fitness of each agent is updated based on their score, and the function continues to 
    run until all agents have died or a high enough score is achieved.
    
    Args:
        genomes (list): A list of NEAT genome objects, each representing an individual agent.
        config (neat.Config): The NEAT configuration object.
    """
    global WIN, GEN
    GEN += 1
    nets = []
    ge = []
    flappys = []
    
    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        flappys.append(Flappy(230, 350))
        ge.append(g)
    
    floor = Floor(FLOOR)
    pipes = [Pipe(700)]
    score = 0
    
    clock = pygame.time.Clock()
    
    run = True
    while run and len(flappys) > 0:
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
                
        indpipe = 0
        if len(flappys) > 0:
            if len(pipes) > 1 and flappys[0].x > pipes[0].x + pipes[0].TPIPE.get_width():
                indpipe = 1

        for x, flappy in enumerate(flappys):
            # Move the bird
            ge[x].fitness += 0.1
            flappy.move()
            
            # Get the output from the neural network
            output = nets[x].activate((flappy.y, abs(flappy.y - pipes[indpipe].height), 
                                                abs(flappy.y - pipes[indpipe].bot)))
            # Make the bird jump
            if output[0] > 0.5:
                flappy.jump()
        
        floor.move()
        
        rem = []
        addpipe = False
        for pipe in pipes:
            pipe.move()
            # Check if the bird has collided with the pipe
            for flappy in flappys:
                if pipe.collide(flappy, WIN):
                    ge[flappys.index(flappy)].fitness -= 1
                    nets.pop(flappys.index(flappy))
                    ge.pop(flappys.index(flappy))
                    flappys.pop(flappys.index(flappy))
                
                if pipe.x + pipe.TPIPE.get_width() < 0:
                    rem.append(pipe)
                    
                if  not pipe.passed and pipe.x < flappy.x:
                    pipe.passed = True
                    addpipe = True
        
        if addpipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))
        
        for r in rem:
            if r in pipes:  # Ensure the pipe is still in the list
                pipes.remove(r)
        
        for flappy in flappys:
            if flappy.y + flappy.img.get_height() - 10 >= FLOOR or flappy.y < 0:
                nets.pop(flappys.index(flappy))
                ge.pop(flappys.index(flappy))
                flappys.pop(flappys.index(flappy))
        
        draw_window(WIN, flappys, pipes, floor, score, GEN, indpipe)

        # break if score gets large enough
        if score > 20:
            pickle.dump(nets[0],open("bestFlappy.pickle", "wb"))
            break

def run(config_path):
    """
    Runs the NEAT algorithm to evolve a population of agents to play the Flappy Bird game.
    
    The function loads the NEAT configuration from the specified path, creates a NEAT population, 
    adds reporters to display progress, and runs the NEAT algorithm for up to 50 generations, 
    using the `fitness` function to evaluate the agents. The winning genome is then displayed.
    """
    # Load configuration.
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    # Run for up to 50 generations.
    winner = p.run(fitness, 50)
    
    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    """
    Runs the NEAT algorithm to evolve a population of agents to play the Flappy Bird game.
    """
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-NEAT.txt')
    run(config_path)