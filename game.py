import sys

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
        # Loads a image into game using pygame built in library
        self.img = pygame.image.load('data/images/clouds/cloud1.png')
        # Create a collision area object rect
        self.collision_area = pygame.Rect((50, 50), (300, 50))
        # Sets the AlphaKey color as black color being transparent
        self.img.set_colorkey((0, 0, 0))
        # Specifies the image position in a 2D coordinate plane
        self.img_pos = [160, 260]
        # [UP, DOWN]
        self.movementY = [False, False]
        # [LEFT, RIGHT]
        self.movementX = [False, False]

        

    def run(self):
        # Main game loop
        while True:
            # Clears window by filling it with a sky background color
            self.window.fill((14, 219, 248))
            # Create a Rect for the cloud with its 
            # size and position being updated
            img_r = pygame.Rect(*self.img_pos, *self.img.get_size())
            # If the cloud rect collides with the
            # collision_area rect then
            # change the color of the collision 
            # area to a different shade of blue
            # else color the collision area blue 
            # with some green.
            if img_r.colliderect(self.collision_area):
                pygame.draw.rect(self.window, (0, 100, 255), self.collision_area)
            else:
                pygame.draw.rect(self.window, (0, 50, 155), self.collision_area)
            # Move image up or down in 2D coords
            self.img_pos[1] += (self.movementY[1] - self.movementY[0]) * 5
            # Move image left or right in 2D coords
            self.img_pos[0] += (self.movementX[1] - self.movementX[0]) * 5
            # Places an object on the screen, at certain 
            # x,y coordinates. For reference in a 2D 
            # coordinate the plane is defined as shown:
            # Top left is 0,0 
            # Top right is 1,0
            # Top left is 0,1
            # bottom right is 1,1
            # Blit is just a memory copy copying some section
            # of memory onto another surface and blit is the
            # terminology for that.
            # Notice I said surface.
            # In pygame a surface is basically an image.
            # The window itself has a surface which is the main
            # one you render onto that's the screen that's
            # a special type of surface but most surface
            # surfaces are kind of like this image one where
            # it's just an image in memory that doesn't 
            # necessarily represent the screen or window.
            # If you wanted you can actually blit the screen
            # onto the image like so:
            # self.image.blit(self.window, self.img_pos) bc
            # they're both surfaces we dont have a reason to
            # do that. U can blit any surface into another
            # surface at a given location so you're just
            # merging together different images. One way to
            # think of it is making a collage of different
            # images on the screen.
            self.window.blit(self.img, self.img_pos)
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
                    if event.key == pygame.K_UP:
                        self.movementY[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movementY[1] = True
                    if event.key == pygame.K_RIGHT:
                        self.movementX[1] = True
                    if event.key == pygame.K_LEFT:
                        self.movementX[0] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movementY[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movementY[1] = False
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