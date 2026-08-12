import sys
import math
import random
from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
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
        # Creates a second surface for rendering
        # that scales up to create a pixel effect
        # that makes a larger image by using half
        # the resolution of the window surface.
        self.display = pygame.Surface((320, 240))

        # Need a clock to run the game a certain amount of
        # frames per second since you do not want the game to
        # run super fast as fast as the CPU processor since pygame
        # runs on the CPU
        self.clock = pygame.time.Clock()
        # [-X (LEFT), +X (RIGHT)]
        self.movement = [False, False]
        # Load the image for the player
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump'), img_dur=5),
            'player/slide': Animation(load_images('entities/player/slide'), img_dur=5),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'), img_dur=5),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
        }
        # References
        self.clouds = Clouds(self.assets['clouds'], count=16)
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.particles = []
        
        # Camera in the top left
        self.scroll = [0, 0]

    def run(self):
        # Main game loop
        while True:
            # Clears window by filling it with a sky background color
            self.display.blit(self.assets['background'], (0,0))
            # Places player on center of the screen
            # takes 1/30 of distance from player before
            # moving camera. Distance player is
            # from camera makes camera catch up faster
            # float not whole number
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            # Fixes the jittery issue when camera moves since
            # the camera bounces a little using integers
            # Note: Theoretically you can use subpixels to
            # render the display more smoothly or subsampling.
            # This means getting a large off screen surface 
            # either 2x or 4x resolution of the WIDTH and 
            # HEIGHT. Then blit the sprite at float coords
            # (scaled up to that surface's size). Then
            # smooth-scale the surface down to the display
            # They were also using pygame.draw.circles
            # (vector-like graphics) pygame.transform
            # .smoothscale(surface, (WIDTH, HEIGHT), screen)
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            #
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            # Update and render clouds before the tilemap so
            # that they appear in the background
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            #
            self.tilemap.render(self.display, offset=render_scroll)
            # Update the player position 2d coordinates
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            # Render the player on the screen
            self.player.render(self.display, offset=render_scroll)
            # Main way to get the events in the window 
            # such as keystrokes, mouse inputs, and more
            # OOP will be used in tutorial a lot
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

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
                        self.movement[1] = True
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
            # The update() function allows the screen to be updated.
            # The screen will not update even if display is changed
            # if you do not call this function called .update()
            # Behaves like pygame.display.flip() with no arguments.
            # Flip is used in double-buffered rendering with 
            # pygame.DOUBLEBUFF swapping the back buffer with the
            # front buffer. Works with software and hardware
            # surfaces and with OpenGL it does buffer swap.
            # Ideal with redrawing the whole screen every frame
            # such as in most games with full-screen updates.
            # Update() passes a list of rects or a rect and
            # is most efficient for small areas of screen change,
            # reducing amount of pixel data sent to the display.
            # It cannot be used with OpenGL surfaces.
            pygame.display.update()
            # Scales the display surface to the same size as the window surface
            # so that the images on screen appear larger giving a pixel effect
            # to the game. It is important to use transform.scale(surface, tuple)
            # to increase the size of the surface. Tuple can use any sizes but
            # it's convienient to use get_size from the window surface here.
            self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0,0))
            # Clock.tick(60) forces the loop to run at 60 fps
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