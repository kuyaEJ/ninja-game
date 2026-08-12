import os
import sys
import math
import random
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
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
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        # Need a clock to run the game a certain amount of
        # frames per second since you do not want the game to
        # run super fast as fast as the CPU proces since pygame
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
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump'), img_dur=5),
            'player/slide': Animation(load_images('entities/player/slide'), img_dur=5),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'), img_dur=5),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png')
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)

        # References
        self.clouds = Clouds(self.assets['clouds'], count=16)
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        self.level = 0
        self.load_level(self.level)
        self.screenshake = 0



    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8,15)))
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        # Camera in the top left
        self.scroll = [0, 0]
        self.dead = 0
        # for circle open and close transition on death
        self.transition = -30
        

    def run(self):
        # Loads music where .wav is best for loading
        # them well without issues. mp3s have
        # weird compression so certain file types
        # can be more restrictive
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        # Main game loop
        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background'], (0, 0))

            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            # death count
            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)

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
            self.clouds.render(self.display_2, offset=render_scroll)
            #
            self.tilemap.render(self.display, offset=render_scroll)
            #
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            # if player isn't dead then you can move and render around
            if not self.dead:
                # Update the player position 2d coordinates
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                # Render the player on the screen
                self.player.render(self.display, offset=render_scroll)

            # [[x,y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:# 6 seconds
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
            #
            #
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)

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
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False

            # * 8 to ensure circle expands to proper size of 180 = 30 * 8
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))
            # for screenshake you can modify the camera scroll value so it moves suddenly
            # the other technique is to change the number of the window blit position so
            # that it shakes
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            # Scales the display surface to the same size as the window surface
            # so that the images on screen appear larger giving a pixel effect
            # to the game. It is important to use transform.scale(surface, tuple)
            # to increase the size of the surface. Tuple can use any sizes but
            # it's convienient to use get_size from the window surface here.
            self.window.blit(pygame.transform.scale(self.display_2, self.window.get_size()), screenshake_offset)
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