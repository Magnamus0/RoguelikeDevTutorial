import libtcodpy as libtcod

from components.ai import ConfusedMonster
from game_messages import Message

def heal(*args,**kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('Just drinking it for the taste? your health is full', libtcod.amber)})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Ahh, much better!', libtcod.green)})

    return results
########################################
def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'consumed': True, 'target': target, 'message': Message('A thunderous snap, a flash of light, the {0} is struck for {1} damage by lightning!'.format(target.name, damage), libtcod.light_purple)})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({'consumed': False, 'target' : None, 'message': Message('The arcane words fizzle off your tongue, but no enemies are close enough for them to reach', libtcod.amber)})

    return results

def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x,target_y):
        results.append({'consumed': False, 'message': Message('The spell cant parse the quantum entaglement here', libtcod.amber)})
        return results

    results.append({'consumed': True, 'message': Message('A small inferno erupts setting everything within {0} tiles ablaze'.format(radius),libtcod.light_purple)})

    for entity in entities:
        true_damage = damage
        if entity.distance(target_x,target_y) <= radius and entity.fighter:
            true_damage = int(damage - entity.distance(target_x,target_y))
            results.append({'message': Message('The {0} is scorched for {1} damage'.format(entity.name,true_damage),libtcod.orange)})
            results.extend(entity.fighter.take_damage(true_damage))

    return results

def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    duration = kwargs.get('duration')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x,target_y):
        results.append({'consumed': False, 'message': Message('The spell cant parse the quantum entaglement here', libtcod.amber)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai =  ConfusedMonster(entity.ai, duration)
            confused_ai.owner = entity
            entity.ai = confused_ai
  
            results.append({'consumed': True, 'message': Message('The {0}`s eyes go blank, it`s confused for {1} rounds!'.format(entity.name,duration),libtcod.light_purple)})
            break
    else:
        results.append({'consumed': False, 'message': Message('The arcane energies find no mind to latch onto', libtcod.amber)})    

    return results





