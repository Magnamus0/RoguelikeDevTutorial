import libtcodpy as libtcod

from death_functions import kill_monster, kill_player
from entity import get_blocking_entities_at_location #imports the entity class
from fov_functions import initalize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu # imports the key handler from the input handler file
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from render_functions import clear_all, render_all 




####################################################################################################################################################################
def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):
    fov_recompute = True #bool so that we only update fov when we need to
    fov_map = initalize_fov(game_map)
    key  = libtcod.Key()
    mouse = libtcod.Mouse()

    previous_game_state = game_state
    targeting_item = None

########    GAME LOOP STARTS HERE   #######################################################################################################################################################
    while not libtcod.console_is_window_closed():                            # while the console window is....open??? MAIN GAME LOOP
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm']) # this is where we do the FOV stuff!

        render_all(con, panel, entities,player, game_map, fov_map, fov_recompute, message_log, constants['screen_width'], constants['screen_height'], 
                   constants['bar_width'], constants['panel_height'], constants['panel_y'] , mouse, constants['colours'], game_state)
        fov_recompute = False

        libtcod.console_flush()                                                              # this is what actually tells the window to draw I guess

        clear_all(con, entities)
        #####   Action handler   #####
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)
    
        move =              action.get('move')
        pickup =            action.get('pickup')
        show_inventory =    action.get('show_inventory')
        drop_inventory =    action.get('drop_inventory')
        inventory_index =   action.get('inventory_index')
        exit =              action.get('exit')
        fullscreen =        action.get('fullscreen')

        left_click =  mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = [] ## this is the container for the results of the players action during their turn
########################################################################################################################################
        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y): 
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True # recalculate feild of view whenver the player moves

                game_state = GameStates.ENEMY_TURN
                ##########################
        elif pickup and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
            else:
                message_log.add_message(Message('There is nothing to pick up.', libtcod.amber))

                ####################################################################################
        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY
                ####################################################################################
        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY
                ####################################################################################
        if inventory_index is not None and previous_game_state!= GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))
                ####################################################################################
        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y =left_click
                item_use_results = player.inventory.use(targeting_item, entities=entities,fov_map=fov_map, target_x=target_x,target_y=target_y)
                player_turn_results.extend(item_use_results)

            elif right_click:
                player_turn_result.append({'targeting_canceled': True})
                ####################################################################################
        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_canceled': True})

            else:
                save_game(player, entities, game_map, message_log, game_state)

                return True
                ####################################################################################
        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
########################################################################################################################################
        for player_turn_result in player_turn_results:
            message =            player_turn_result.get('message')
            dead_entity =        player_turn_result.get('dead')
            item_added =         player_turn_result.get('item_added')
            item_consumed =      player_turn_result.get('consumed')
            item_dropped =       player_turn_result.get('item_dropped')
            targeting =          player_turn_result.get('targeting')
            targeting_canceled = player_turn_result.get('targeting canceled')

            if message:
                message_log.add_message(message)
            if targeting_canceled:
                game_state =previous_game_state
                message_log.add_message(Message('Targeting canceled'))
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)
            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYER_TURN #prev is set ot player turn so that canceling targeting doesnt put you bakc into the inventory
                game_state = GameStates.TARGETING

                targeting_item =targeting

                message_log.add_message(targeting_item.item.targeting_message)
            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN
######################################################################################################
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results  = entity.ai.take_turn(player, fov_map,game_map,entities)

                    for enemy_turn_result in enemy_turn_results:
                         message = enemy_turn_result.get('message')
                         dead_entity = enemy_turn_result.get('dead')

                         if message:
                             message_log.add_message(message)
                         if dead_entity:
                             if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                             else:
                                message = kill_monster(dead_entity)

                             message_log.add_message(message)

                             if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYER_TURN
############################################################################################################################################################################################               


def main(): # yoooooo
    constants = get_constants()
    

    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)            # this sets the font
    libtcod.console_init_root(constants['screen_width'],constants['screen_height'], constants['window_title'] , False)                                       # pretty sure this is the parameters of the console window itself\

    #sets up the console window
    con = libtcod.console_new(constants['screen_width'], constants['screen_height'])
    panel = libtcod.console_new(constants['screen_width'], constants['panel_height']) 
    
    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load('menu_Background1.png')

    key  = libtcod.Key()
    mouse = libtcod.Mouse()
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE , key, mouse)
        if show_main_menu:
            main_menu(con,main_menu_background_image,constants['screen_width'], constants['screen_height'])
            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'] )
            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game =        action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game =       action.get('exit')


            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False

            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(constants)
                game_state = GameStates.PLAYER_TURN
                show_main_menu = False

            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break
            pass
        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state ,con,panel,constants) ### pogchaMP
            show_main_menu =True

    ##  Housekeeping variables







if __name__ == '__main__':
    main()