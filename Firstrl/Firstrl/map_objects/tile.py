class Tile:
# a tile on the map
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False
        # by default if a tile is blocked it also blocks line of sight
        if block_sight is None:
            block_sight = blocked
            
        self.block_sight = block_sight


