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
        self.pos = list(pos)
        # Doesn't need to be converted into a list since
        # it will be an array in the arguments
        self.size = size
        # The variable that helps determine how fast you
        # want the character to move when you want it to
        # have a temporary boost in movement
        self.velocity = [0, 0]

    def update(self, movement=(0, 0)):
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        self.pos[1] += frame_movement[1]

    def render(self, surf):
        surf.blit(self.game.assets('player'), self.pos)