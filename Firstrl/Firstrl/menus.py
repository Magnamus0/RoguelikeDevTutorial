import libtcodpy as libtcod

def menu(con,header,options,width,screen_width, screen_height):
    max_menu_options = 26
    if len(options) > max_menu_options: raise ValueError('Cannot have a menu with more than {0} options'.format(max_menu_options)) #this limits the number of total options in a given menu
    
    header_height = libtcod.console_get_height_rect(con,0,0, width,screen_height, header)
    height = len(options) + header_height

    window = libtcod.console_new(width,height)

    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    y= header_height
    letter_index = ord('a')
    for option_text in options:
        text = '('+ chr(letter_index) +')'+  option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def inventory_menu(con,header,inventory,inventory_width,screen_width,screen_height):
    if len(inventory.items) == 0:
        options = ['Your inventory is barren.']
    else:
        options = [item.name for item in  inventory.items]
    menu(con,header,options,inventory_width,screen_height,screen_width)

def main_menu(con, background_image, screen_width, screen_height):
    libtcod.image_blit_2x(background_image,0,0,0)

    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2) - 4 ,libtcod.BKGND_NONE, libtcod.CENTER, 'OHEYCOOL IT DIDNT CRASH ON STARTUP!' )
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2), libtcod.BKGND_NONE, libtcod.CENTER,
                             'Waveform Studios')

    menu(con, '', ['Play a new game', 'Continue last game', 'Quit'], 24, screen_width, screen_height)

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)
