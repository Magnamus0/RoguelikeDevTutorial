import libtcodpy as libtcod
from game_messages import Message


class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        if self.hp <=0:
            results.append({'dead': self.owner})

        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp


    def attack(self,target):
        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            
            results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(self.owner.name.capitalize(), target.name, str(damage)), libtcod.yellow)})
            results.extend(target.fighter.take_damage(damage))  
            ##the extend function is similar to append, but it keeps our list flat, so we don't get something like 
            ##[{'message': 'something'}, [{'message': 'something else'}]]. Instead, we would get: [{'message': 'something'}, {'message': 'something else'}]. 
            ##That will make looping through our results much simpler.
        else:
            results.append({'message': Message('{0} attacks {1} but does no damage.'.format(self.owner.name.capitalize(), target.name), libtcod.white)})

        return results