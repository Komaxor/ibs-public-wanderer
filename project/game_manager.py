from random import randrange
from area import Area
from hero import Hero
from monster import Monster
from skeleton import Skeleton
from boss import Boss

class GameManager:
#TODO index error handling

    def __init__(self):
        self.area_number = 1
        self.area = Area()
        self.hero = Hero()
        self.characters = self.create_characters()
        self.monsters = self.characters[1:]

    def create_characters(self):
        characters = []
        characters.append(self.hero)
        monsters = self.create_monsters()
        for i in range(0, len(monsters)):
            characters.append(monsters[i])
        return characters

    def create_monsters(self):
        monsters = []
        boss = Boss()
        boss.level = self.area_number
        monsters.append(boss)
        skeletons = []
        number_of_skeletons = randrange(42, 50)
        for i in range(number_of_skeletons):
            skeletons.append(Skeleton('Skeleton ' + str(i + 1)))
        skeletons[0].has_key = True
        for skeleton in skeletons:
            skeleton.level = self.area_number
            monsters.append(skeleton)
        return monsters

    def get_stats(self):
        for character in self.characters:
            print(character.introduce())

    def get_tile_stats(self, tile):
        print(tile.walkable)
        print(tile.has_hero)
        print(tile.has_monster)

    def set_free_tiles(self):
        self.area.free_tiles = []
        for tile in self.area.tiles:
            #self.get_tile_stats(tile)
            if (tile[0].walkable == True and tile[0].has_hero == False
                and tile[0].has_monster == False):
                self.area.free_tiles.append((tile[0], (tile[0].x, tile[0].y)))

    def spawn_characters(self, canvas):
        self.area.character_images = {}
        self.spawn_hero(canvas)
        self.spawn_monsters(canvas)

    def spawn_hero(self, canvas):
        self.set_free_tiles()
        self.hero.image_path = self.hero.image_down
        self.area.draw_character(canvas, self.hero)
        tile = self.area.tiles[0][0]
        tile.has_hero = True

    def spawn_monsters(self, canvas):
        for monster in self.monsters:
            self.set_free_tiles()
            tile = self.area.free_tiles[randrange(len(self.area.free_tiles))]
            monster.y = tile[1][0]
            monster.x = tile[1][1]
            self.area.draw_character(canvas, monster)
            tile[0].has_monster = True

    def get_character_tile(self, character):
        return [i for i in self.area.tiles if [character.x, character.y] in i]

    def set_hero_position(self, canvas, direction):
        self.hero.turn(direction)
        self.area.draw_character(canvas, self.hero)
        destination_x, destination_y = self.calculate_destination(self.hero, direction) #NOTE how to decrease?
        is_wall = self.check_walls(destination_x, destination_y)
        if is_wall == True:
            print('Ouch! Watch where you are going!')
            return
        if self.check_map(destination_x, destination_y):
            self.get_character_tile(self.hero)[0][0].has_hero = False
            self.hero.x, self.hero.y = destination_x, destination_y
            self.area.draw_character(canvas, self.hero)
            self.get_character_tile(self.hero)[0][0].has_hero = True
        else:
            print('The edge has been reached!')
            return
        has_monster = self.check_monsters(destination_x, destination_y)
        if has_monster != False:
            self.fight(self.hero, has_monster)
            self.hero.level_up()
        self.check_monster_move(canvas)

    def check_monster_move(self, canvas):
        if self.area.turn_count % 2 != 0:
            for monster in self.monsters:
                self.set_monster_position(canvas, monster)
        self.area.increase_turn_count()

    def set_monster_position(self, canvas, monster):
        directions = self.get_possible_moves(monster)
        direction = directions[randrange(len(directions))]
        destination_x, destination_y = self.calculate_destination(monster, direction) #NOTE how to decrease?
        self.get_character_tile(monster)[0][0].has_monster = False
        monster.x, monster.y = destination_x, destination_y
        self.area.draw_character(canvas, monster)
        self.get_character_tile(monster)[0][0].has_monster = True
        if self.get_character_tile(monster)[0][0].has_hero == True:
            self.fight(monster, self.hero)
            self.hero.level_up()

    def get_possible_moves(self, monster):
        directions = ['up', 'down', 'left', 'right']
        bad_directions = []
        for direction in directions:
            destination_x, destination_y = self.calculate_destination(monster, direction) #NOTE how to decrease?
            is_wall = self.check_walls(destination_x, destination_y)
            if is_wall == True:
                bad_directions.append(direction)
                continue
            if self.check_map(destination_x, destination_y) == False:
                bad_directions.append(direction)
                continue
            has_monster = self.check_monsters(destination_x, destination_y)
            if has_monster != False:
                bad_directions.append(direction)
                continue
        if len(bad_directions) != 0:
            for item in bad_directions:
                directions.remove(item)
        if len(directions) == 0:
            #print('monster is trapped')
            self.get_character_tile(monster)[0][0].has_monster = False
            return ['stay']
        return directions

    def calculate_destination(self, character, direction):
        if direction == 'up':
            x = character.x
            y = character.y - 72
        elif direction == 'down':
            x = character.x
            y = character.y + 72
        elif direction == 'right':
            y = character.y
            x = character.x + 72
        elif direction == 'left':
            y = character.y
            x = character.x -72
        else:
            y = character.y
            x = character.x
        return (x, y)

    def check_walls(self, destination_x, destination_y):
        if (((destination_y * self.area.number_of_tiles) / self.area.tile_size)
            + (destination_x / self.area.tile_size) in self.area.walls): #NOTE linebreak OK?
            return True
        else:
            return False

    def check_map(self, destination_x, destination_y):
        if (destination_x < 0
            or destination_x > self.area.size - self.area.tile_size
            or destination_y < 0
            or destination_y > self.area.size - self.area.tile_size):
            return False
        else:
            return True

    def check_monsters(self, destination_x, destination_y):
        for monster in self.monsters:
            if monster.x == destination_x and monster.y == destination_y:
                return monster
        else:
            return False

    def fight(self, attacker, defender):
        while attacker.current_health > 0 and defender.current_health > 0:
            attacker.strike(attacker, defender)
            if self.check_death(defender) == True:
                return
            defender.strike(defender, attacker)
            self.check_death(attacker)

    def check_death(self, receiver):
        if receiver.current_health <= 0:
            print(receiver.name + " died")
            del self.area.character_images[receiver.name]
            self.kill(receiver)
            return True
        else:
            return False

    def kill(self, character):
        self.characters.remove(character)
        if isinstance(character, Monster):
            self.monsters.remove(character)
        else:
            print('game over')
        #del character #NOTE needed?

    def check_next_area(self, canvas):
        if self.check_boss() == False and self.check_key() == False:
            self.next_area(canvas)

    def check_boss(self):
        for monster in self.monsters:
            if monster.__class__.__name__ == "Boss":
                return True
        return False

    def check_key(self):
        for monster in self.monsters:
            if monster.has_key == True:
                return True
        return False

    def next_area(self, canvas):
        self.area_number += 1
        self.area = Area()
        self.hero.restore_health()
        self.characters = self.create_characters()
        self.monsters = self.characters[1:]
        self.area.draw_map(canvas)
        self.spawn_characters(canvas)