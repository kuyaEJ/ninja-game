import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        # Allows the class to see and call the game
        # with pass by reference so that the game
        # objects are callable even if they aren't
        # initialized or declared in this file.
        self.game = game
        # The type of entity to use for helper scripts
        # so groups of entities have different
        # functionality
        self.type = e_type
        # If the position given is not already a list
        # This ensure it is convered to one
        # And makes sure that each entity has it's own
        # reference to a list so that entities do not
        # have the same positions.
        # Assume it's [x,y] where x is horzi and y is vert
        self.pos = list(pos)
        # Doesn't need to be converted into a list since
        # it will be an array in the arguments
        self.size = size
        # The variable that helps determine how fast you
        # want the character to move when you want it to
        # have a temporary boost in movement
        self.velocity = [0, 0]
        self.collisions = {'up':False, 'down':False, 'right':False, 'left':False}
        #
        #
        self.action = ''
        # Accounts for padding for animations that overflow
        # outside hitboxes of the player since the Rect
        # is smaller than the img
        self.anim_offset = (-3, -3)
        # Lets the player face right or left
        self.flip = False
        self.set_action('idle')

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        # Check if the action actually changed
        # if its set to something we dont have then
        # we want to find the new animation.
        # Ensures that the animation is already set
        # rather than checking each animation it just
        # waits to be called before updating the anims
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        # Resets collision dictionary every frame to make sure
        # that it's always updating what tiles around the player
        # are walkable on or collided on or not collided on
        self.collisions = {'up':False, 'down':False, 'right':False, 'left':False}
        # calculates how much movement every frame is doing.
        # If there's a velocity then it'll add to every
        # frame where it's moving like a small push
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        # Updates the position of the entity with
        # the calculated frame movement
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0: # moving right
                    # right edge of entity 
                    # snaps to left edge of tile
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0: # moving left
                    # left edge of entity
                    # snaps to right edge of tile
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0: # moving down
                    # bottom edge of entity 
                    # snaps to top edge of tile
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0: # moving up
                    # top edge of entity
                    # snaps to bottom edge of tile
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
    
        # Terminal velocity of 5 is max velocity you can reach
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        # Stops movement when colliding with ceiling or floor
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        # Flip image before rendering it
        # .flip(img, xaxis, yaxis)
        # xaxis set to true means facing left
        # while false faces right
        # And usually we don't have yaxis flipped
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0

        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')