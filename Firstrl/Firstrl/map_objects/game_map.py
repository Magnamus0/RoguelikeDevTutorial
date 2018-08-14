import libtcodpy as libtcod
from random import randint

from components.fighter import Fighter
from components.ai import BasicMonster
from components.item import Item
from entity import Entity
from game_messages import Message
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from map_objects.rect import Rect
from map_objects.tile import Tile
from render_functions import RenderOrder


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height) ] for x in range(self.width) ]


        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room, max_items_per_room):
        rooms = []
        num_rooms = 0

        for r in range(max_rooms):
            # random size
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            #random position without leaving the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h)

            #see if any other rooms overlap this one
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means the room doesnt overlap

                self.create_room(new_room)
                (new_x, new_y) = new_room.center() #storing the center of the new room for later use

                if num_rooms == 0: #make the first room the one where the player starts
                    player.x = new_x
                    player.y = new_y
                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    (prev_x, prev_y) = rooms[num_rooms - 1].center() #grab the coords of the center of the previous room
                    if randint(0,1) == 1: #coin flip
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)
                self.place_entities(new_room, entities,max_monsters_per_room, max_items_per_room)

                rooms.append(new_room)
                num_rooms += 1


         ##############################################################       

    def create_room(self,room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 +1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) +1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) +1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
 ###################################################################################
    def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)
            ############################################################################################# enbbemy spawning
        for i in range(number_of_monsters):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y ]): # what the  FUCK is with this syntax (it's looking to see if there are any entities in that spot)
                if randint(0, 100) < 80:
                    fighter_component = Fighter(hp = 10, defense = 0, power = 3)
                    ai_component = BasicMonster()

                    monster = Entity(x, y, 'o', libtcod.desaturated_green, 'orc', blocks=True,render_order = RenderOrder.ACTOR, fighter=fighter_component, ai = ai_component) # makes mostly orcs
                else: 
                    fighter_component = Fighter(hp = 16, defense = 1, power = 4)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'T', libtcod.darker_green, 'troll', blocks=True,render_order = RenderOrder.ACTOR, fighter=fighter_component, ai = ai_component) #sometimes trolls
                entities.append(monster) #adds monster to the list of entities
#####################   ITEM GENERATION   ###############################################################################
        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not any([entity for entity in entities if entity.x == x and entity.y == y ]):
                item_chance = randint(0, 100) ### this is where the type of item is determined. sub-type is per item
# 00-70
                if item_chance >= 0 and item_chance <= 30: #################################################################################################################################
#      potions
                    type_chance = randint(0,100) ## kind of potion that spanws
                ## 00-100 lesser healing pot
                    if type_chance >= 0 and type_chance <= 100: 
                        item_component = Item(use_function=heal, amount=4)
                        item = Entity(x,y,'!', libtcod.violet, 'Lesser Healing Potion', render_order =RenderOrder.ITEM, item=item_component)
# 71-100
                else:
#      scrolls
                    type_chance = randint(0,100)
                ## 00-60 Minor lightning
                    if type_chance >= 0 and type_chance <= 60: 
                        item_component = Item(use_function=cast_lightning, damage=20, maximum_range=5)
                        item = Entity(x,y,'#', libtcod.light_yellow, 'Scroll of Minor Lightning', render_order =RenderOrder.ITEM, item=item_component)
                ## 61-80 Minor Fireball
                    if type_chance >= 61 and type_chance <= 80: 
                        item_component = Item(use_function=cast_fireball,targeting=True,targeting_message=Message('Left click to target a tile, right click to canel', libtcod.light_cyan), damage=12, radius =3)
                        item = Entity(x,y,'#', libtcod.light_red, 'Scroll of Minor Fireball', render_order =RenderOrder.ITEM, item=item_component)
                ## 81-100 Minor Fireball
                    if type_chance >= 81 and type_chance <= 100: 
                        item_component = Item(use_function=cast_confuse,targeting=True,targeting_message=Message('Left click to target a tile, right click to canel', libtcod.light_cyan), duration = 10)
                        item = Entity(x,y,'#', libtcod.light_blue, 'Scroll of Momentary Confusion', render_order =RenderOrder.ITEM, item=item_component)
                entities.append(item)
####################################################################################################
    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False