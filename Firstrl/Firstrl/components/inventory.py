import libtcodpy as libtcod

from game_messages import Message


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item): # adds items to the inventory 
        results = []

        if len(self.items) >= self.capacity:
            results.append({'item_added': None, 'message' : Message('OOPS, your inventory is full', libtcod.amber)})

        else:
            results.append({'item_added': item, 'message' : Message('You pick up the {0}.'.format(item.name), libtcod.light_blue)})

            self.items.append(item)

        return results

    def use(self, item_entity, **kwargs): #this allows us to use items from the inventory screen
        results = []
        item_component =  item_entity.item

        if item_component.use_function is None:
            results.append({'message': Message('The {0} cannot be used'.format(item_entity.name), libtcod.amber)})
        else:
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):
                        self.remove_item(item_entity)

                results.extend(item_use_results)
        return results

    def remove_item(self, item): # delete inventory items after they've been consumed
        self.items.remove(item)

    def drop_item(self, item):
        results = []

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({'item_dropped': item, 'message': Message('You dropped your {0}.'.format(item.name),libtcod.light_blue)})

        return results

