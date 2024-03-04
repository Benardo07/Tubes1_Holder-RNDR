import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import *

class NearestBase(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties

        teleport = [x for x in board.game_objects if (x.type == "TeleportGameObject")]
        current_position = board_bot.position
# Group teleporters by their pair_id
        teleport_groups = {}
        for teleporter in teleport:
            pair_id = teleporter.properties.pair_id
            if pair_id not in teleport_groups:
                teleport_groups[pair_id] = []
            teleport_groups[pair_id].append(teleporter)

        # Sort each group of teleporters by their distance to the bot and store the distance
        sorted_teleport_groups = {}
        for pair_id, teleporters in teleport_groups.items():
            sorted_teleporters = sorted([(teleporter.position, abs(current_position.x - teleporter.position.x) + abs(current_position.y - teleporter.position.y)) for teleporter in teleporters], key=lambda t: t[1])
            sorted_teleport_groups[pair_id] = sorted_teleporters

        # Sort the sorted_teleport_groups dictionary based on the distance of the nearest teleporter in each group
        sorted_teleport_groups = dict(sorted(sorted_teleport_groups.items(), key=lambda item: item[1][0][1]))
        print("ini ben")
        # b = []
        # teleport = [x for x in board.game_objects if (x.type=="TeleportGameObject")]
        # for position in teleport :
        #     distance2 = (abs(current_position.x - position.position.x) + abs(current_position.y - position.position.y))
        #     b.append([distance2,position.position])
        # tele_sorted_list = sorted(b, key=lambda d: d[0])
        # Analyze new state

        diamonds = find_diamond(current_position, board)
        base = board_bot.properties.base
        current_position = board_bot.position

        x = []
        y = []

        for position in diamonds:
            posX = abs(base.x  - position.position.x)
            posY = abs(base.y - position.position.y)
            distance = (abs(base.x  - position.position.x) + abs(base.y - position.position.y))
            x.append([distance,position.position,[posX,posY],position.properties.points])
            posX = abs(current_position.x  - position.position.x)
            posY = abs(current_position.y - position.position.y)
            distance1 = (abs(current_position.x  - position.position.x) + abs(current_position.y - position.position.y))
            y.append([distance1,position.position,[posX,posY],position.properties.points])

        diamond_distance_sums = []
        for diamond in diamonds:
            total_distance = sum(abs(diamond.position.x - other_diamond.position.x) + abs(diamond.position.y - other_diamond.position.y) for other_diamond in diamonds if other_diamond != diamond)
            diamond_distance_sums.append([total_distance, diamond.position])
            
        diamond_sorted_base = sorted(x, key=lambda d: d[0])
        diamond_sorted_bot = sorted(y, key=lambda d: d[0])
        diamond_sorted_by_density = sorted(diamond_distance_sums, key=lambda d: d[0])
        board_width = board.width
        board_height = board.height

        red_button = find_red_button(current_position, board)
        z = []
        a = []

        for position in red_button:
            distance = (abs(base.x  - position.position.x) + abs(base.y - position.position.y))
            z.append([distance,position.position])
            distance = (abs(current_position.x  - position.position.x) + abs(current_position.y - position.position.y))
            a.append([distance,position.position])
        
        red_button_sorted_base =  sorted(z, key=lambda d: d[0])
        red_button_sorted_bot = sorted(a, key=lambda d: d[0])
        base_distance = abs(current_position.x - board_bot.properties.base.x) + abs(current_position.y - board_bot.properties.base.y)
        
        bot_enemy = [x for x in board.game_objects if (x.type=="BotGameObject" and x.id != board_bot.id)]
        print(bot_enemy)
        k = []
        for position in bot_enemy:
            distance = (abs(current_position.x  - position.position.x) + abs(current_position.y - position.position.y))
            k.append([distance,position.position])

        bot_enemy_sorted =  sorted(k, key=lambda d: d[0])
        if props.diamonds >= 4:
            # Move to 
            if(diamond_sorted_bot[0][0] <= 2 and props.diamonds + diamond_sorted_bot[0][3] <= 5):
                self.goal_position = diamond_sorted_bot[0][1]
            else:
                base = board_bot.properties.base
                self.goal_position = base
        else:

            
            # base_distance_tele = tele_sorted_list[0][0] + abs(tele_sorted_list[1][1].x - board_bot.properties.base.x) + abs(tele_sorted_list[1][1].y - board_bot.properties.base.y)

            if(base_distance == 1 and props.diamonds >= 1):
                self.goal_position = base
            elif(bot_enemy_sorted and bot_enemy_sorted[0][0] <= 1 and props.diamonds < 2 ):
                self.goal_position = bot_enemy_sorted[0][1]
            elif(board_bot.properties.milliseconds_left <= 8000 and props.diamonds >= 2):
                if(diamond_sorted_bot[0][0] <= 1 ):
                    self.goal_position = diamond_sorted_bot[0][1]
                else:
                    self.goal_position = base
            elif(diamond_sorted_bot or diamond_sorted_base):
                if(props.diamonds >= 3 and base_distance <= 3):
                    self.goal_position = base
                elif(diamond_sorted_bot[0][0] <= 2) :
                    self.goal_position = diamond_sorted_bot[0][1]
                elif((diamond_sorted_base[0][2][0] < 0.5 * board_width) and  (diamond_sorted_base[0][2][1] <  0.5 * board_height)) :
                    if(diamond_sorted_bot[0][0] <= 2 ):
                        self.goal_position = diamond_sorted_bot[0][1]
                    else:
                        self.goal_position = diamond_sorted_base[0][1]

                else:
                    if(red_button_sorted_base != []):
                        if(red_button_sorted_base[0][0] < (0.5 * board_width +  0.5 * board_height)):
                            self.goal_position = red_button_sorted_base[0][1]
                        elif(red_button_sorted_bot[0][0] <= 3 and len(diamonds) < 4):
                            self.goal_position = red_button_sorted_bot[0][1]
                        elif diamond_sorted_by_density:
                            if(diamond_sorted_bot[0][0] <= 2):
                                self.goal_position = diamond_sorted_bot[0][1]
                            else:
                                self.goal_position = diamond_sorted_by_density[0][1]
                        else:
                            self.goal_position = diamond_sorted_bot[0][1]
            else:
                if(props.diamonds >= 3):
                    self.goal_position = base
                else:
                    self.goal_position = red_button


    
        current_position = board_bot.position
        if self.goal_position:
            shortest_way = abs(current_position.x - self.goal_position.x) + abs(current_position.y - self.goal_position.y)
            shortest_way_position = self.goal_position

            # Iterate over each pair of teleporters
            for pair_id, teleporters in sorted_teleport_groups.items():
                closest_teleporter, distance_to_closest_teleporter = teleporters[0]
                print(closest_teleporter)
                second_teleporter = teleporters[1][0]

                # Calculate the distance from the second teleporter in the pair to the goal position
                distance_tele2_goal = abs(second_teleporter.x - self.goal_position.x) + abs(second_teleporter.y - self.goal_position.y)

                # Calculate the total distance if using this teleporter pair
                way1 = distance_to_closest_teleporter + distance_tele2_goal

                # Compare the total distance with the shortest way found so far
                if way1 < shortest_way:
                    shortest_way = way1
                    shortest_way_position = closest_teleporter


# Update the goal position to the shortest way position
            if(current_position == shortest_way_position):
                delta_x, delta_y = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
            else:
                self.goal_position = shortest_way_position
                delta_x, delta_y = get_direction(
                    current_position.x,
                    current_position.y,
                    self.goal_position.x,
                    self.goal_position.y,
                )
            # We are aiming for a specific position, calculate delta
            
        else:
            # Roam around
            delta = self.directions[self.current_direction]
            delta_x = delta[0]
            delta_y = delta[1]
            if random.random() > 0.6:
                self.current_direction = (self.current_direction + 1) % len(
                    self.directions
                )
        print(current_position)
        print(self.goal_position)
        if(delta_x == 0 and delta_y == 0) :
            delta_x, delta_y = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
        return delta_x, delta_y