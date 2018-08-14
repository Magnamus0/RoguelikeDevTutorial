import libtcodpy as libtcod

from components.fighter import Fighter
from components.inventory import Inventory
from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from render_functions import RenderOrder

def get_constants():
    window_title = 'Im a sneaky gay tee hee c:'

    screen_width = 90
    screen_height = 50

    #this is an hp bar
    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height
    #the message bar
    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1
    #map size
    map_width = 90
    map_height = 43
    #room variables
    room_max_size = 15
    room_min_size = 6
    max_rooms = 30
    #fov algorithm variables
    fov_algorithm = 3 # the kind of algorithm libtcod uses
    fov_light_walls = True
    fov_radius = 10
    #entity variables
    max_monsters_per_room = 3
    max_items_per_room = 2
    #misc aesthetic stuff
    colours = {                                                                     #decorative bits
        'dark_wall': libtcod.Color(0,0,100),
        'dark_ground': libtcod.Color(50,50,150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50)
        }
    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,
        'colours': colours
        }

    return constants

def get_game_variables(constants):

    # creating the player + adding the player to the entity list
    fighter_component = Fighter(hp = 30,defense = 2, power = 5)
    inventory_component = Inventory(26)
    player = Entity(0, 0, '@', libtcod.white, 'Player',blocks = True,render_order = RenderOrder.ACTOR, fighter = fighter_component, inventory=inventory_component)                                                             #player stuff
    entities = [player]

    #makes our map
    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], 
                      player, entities, constants['max_monsters_per_room'], constants['max_items_per_room']) #makes the map

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYER_TURN
    return player, entities, game_map, message_log, game_state
