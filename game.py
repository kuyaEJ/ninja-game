import sys
from scripts.entities import PhysicsEntity
from scripts.utils import load_image
import pygame

class Game:
    def __init__(self):
        # Initializes the python implementation for the SDL library
        # which uses C code for efficiency.
        pygame.init()
        # Sets the Window Title
        pygame.display.set_caption("My PyGame Game")
        # Sets the resolution of the display
        self.window = pygame.display.set_mode((640, 480))
        # Need a clock to run the game a certain amount of
        # frames per second since you do not want the game to
        # run super fast as fast as the CPU processor since pygame
        # runs on the CPU
        self.clock = pygame.time.Clock()
        # Specifies the image position in a 2D coordinate plane
        self.img_pos = [160, 260]
        # [-X (LEFT), +X (RIGHT)]
        self.movement = [False, False]
        # Load the image for the player
        self.assets = {
            'player': load_image('entities/player.png')
        }
        # Player in physics engine
        self.player = PhysicsEntity(self, 'player', (50, 50), (0, 15))
        

    def run(self):
        # Main game loop
        while True:
            # Clears window by filling it with a sky background color
            self.window.fill((14, 219, 248))
            # Update the player position x and y values
            self.player.update((self.movement[1] - self.movement[0], 0))
            # Render the player on the screen
            self.player.render(self.window)
            # Main way to get the events in the window 
            # such as keystrokes, mouse inputs, and more
            # OOP will be used in tutorial a lot
            for event in pygame.event.get():
                # If the exit (red icon) of the window is clicked 
                # then the window is closed
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # If a key down/pressed button triggers
                # then for movementY array update to True
                # based on what arrow keys were pressed
                # Note: The movement uses a mechanic where 
                # if two buttons that move in opposite
                # directions are pressed then the movement
                # is set to 0 while it also accounts for
                # diagonal movement when two different
                # axes of movement are pressed at the same
                # time. When the key is released or
                # key goes up then the game sets the
                # values to False to indicate they're
                # not being pressed and stop the
                # movement mechanic.
                # Note arrow keys are used since for
                # different keyboard layouts like
                # european keyboards or more
                # they're the most commonly used
                # buttons since not every layout has
                # the WASD keys next to each other
                # but they do always have arrow keys
                # and X, and C next to each other
                # which is why game developers tend
                # to commonly use those keys.
                # It can be set to have WASD movement
                # by using K_w, K_a, K_s, K_d to
                # move if you want to add it.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.movementX[1] = True
                    if event.key == pygame.K_LEFT:
                        self.movementX[0] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        self.movementX[1] = False
                    if event.key == pygame.K_LEFT:
                        self.movementX[0] = False
            # The update() function allows the screen to be updated.
            # The screen will not update even if display is changed
            # if you do not call this function called .update()
            pygame.display.update()
            # Clock.tick(6) forces the loop to run at 60 fps
            # It also returns the last time that the function
            # was last called from. This means that it basically
            # waits for 1/60th of a frame before continuing 
            # in the next iteration. It can be adjusted for
            # different refresh rates but for now we keep it at 60.
            # Note: use pygame.display.get_desktop_refresh_rates()
            # to get a list of all connected monitor refresh rates.
            # Use pygame.display.get_current_refresh_rate()
            # to get the refresh rate on the window screen for the
            # game in order to adjust to each monitor setting and
            # enable or disable certain settings.
            self.clock.tick(60)


Game().run()