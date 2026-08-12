import pygame

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0,), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'} # This is a set, 
# where order is not important, no dupes, lookup in set is more efficient than in a list
# lookup value in dictionary is also very fast and takes roughly
# same time to lookup value if you know the key
class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}# dictionary for maps system
        self.offgrid_tiles = []# list for level editor?
        # we map each tile based on it's
        # location.
        # Our tile method:
        # {(0,0): 'grass', (0,1): 'dirt', (9999, 0): 'grass'}
        # better than needing to specify that certain positiions
        # are 'air'
        # He made a system to turn tuples into something else
        # in case he doesn't want to use tuples

        # Created tiles for grass and stone blocks
        for i in range(10):
            self.tilemap[str(3 + i) + ';10'] = {'type': 'grass', 'variant': 1, 'pos': (3 + i, 10)}
            self.tilemap['10;' + str(5 + i)] = {'type': 'stone', 'variant': 1, 'pos': (10, 5 + i)}

    def tiles_around(self, pos):
        # Integeter truncates and doesn't do proper integer
        # division the way double slash does
        # E.g -3/2 = -1.5
        # E.g int(-3/2) = -1
        # -3 //2 = -2
        # int(0.9) = 0
        # int(-0.9) = 0
        # int just chops off the decimal points but double slash
        # actually rounds up
        # The negative numbers are handled differently
        # and integer conversions for decimals need to be handled
        # carefully.
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    # converting tiles with physics to have rects
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def render(self, surf, offset=(0, 0)):
        # Not optimized and isn't setup.
        # The offgrid_tiles are empty so
        # currently this doesn't do
        # anything.
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
        # find top left tiles coordinates x position
        # optimization for tile renders to work with big maps
        # for infinite world might need offgrid tiles separated in a set of quads.
        # Each quad could be a list of all the tiles in it like the tiles we
        # have now except instead of mapping the for loop tiles to tilemap
        # we map them to for i in range(10): 
        # offgrid_tiles[] = {type, variant, pos, 
        # loaded?idk fourth var he would put}. 
        # need to map list of offgrid tiles to locations and sometimes quads
        # would be 4 times larger than on grid tiles. But you can get away with
        # a lot using on grid tiles before you need to start optimizing them
        # so in this project the offgrid tiles are not optimized especially 
        # since we're making the levels by hand and not with a autogenerator
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))