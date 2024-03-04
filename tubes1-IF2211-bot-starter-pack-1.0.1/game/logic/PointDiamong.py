from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position 
from typing import Optional
from ..util import *
import random


class PointDiamond(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def next_move(self, board_bot: GameObject, board: Board):

        props = board_bot.properties
        current_position = board_bot.position
        teleport = find_teleport(current_position, board)
        tele_sorted_list = sorted(teleport, key=lambda d: d[0])
        
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
        # Analyze new state
        if props.diamonds == 5:
            # Move to base
            base = board_bot.properties.base
            self.goal_position = base
        else:
            # Just roam around
            # red_diamond = [x for x in board.game_objects if x.type=="DiamondButtonGameObject"]
            red_diamond = find_red_diamond(current_position, board)
            blue_diamond = find_blue_diamond(current_position, board)

            sorted_blue = sorted(blue_diamond, key=lambda d: d[0])
            sorted_red = sorted(red_diamond, key=lambda d: d[0])
            
            base_distance = abs(current_position.x - board_bot.properties.base.x) + abs(current_position.y - board_bot.properties.base.y)
            base_distance_tele = tele_sorted_list[0][0] + abs(tele_sorted_list[1][1].x - board_bot.properties.base.x) + abs(tele_sorted_list[1][1].y - board_bot.properties.base.y)

            if(sorted_blue[0][0] <= 2):
                self.goal_position = sorted_blue[0][1]
            elif(sorted_red != [] and props.diamonds <=3):
                self.goal_position = sorted_red[0][1]
            elif(props.diamonds >= 3 and (base_distance <= 2 or base_distance_tele <= 3)):
                self.goal_position = board_bot.properties.base
            else:
                self.goal_position = sorted_blue[0][1]
        current_position = board_bot.position
        if self.goal_position:
            
            shortest_way = abs(current_position.x - self.goal_position.x) + abs(current_position.y - self.goal_position.y)
            shortest_way_position = self.goal_position

            # Iterate over each pair of teleporters
            for pair_id, teleporters in sorted_teleport_groups.items():
                closest_teleporter, distance_to_closest_teleporter = teleporters[0]
                second_teleporter = teleporters[1][0]

                # Calculate the distance from the second teleporter in the pair to the goal position
                distance_tele2_goal = abs(second_teleporter.position.x - self.goal_position.x) + abs(second_teleporter.position.y - self.goal_position.y)

                # Calculate the total distance if using this teleporter pair
                way1 = distance_to_closest_teleporter + distance_tele2_goal

                # Compare the total distance with the shortest way found so far
                if way1 < shortest_way:
                    shortest_way = way1
                    shortest_way_position = closest_teleporter.position

# Update the goal position to the shortest way position
            self.goal_position = shortest_way_position
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )


        else:
            # Roam around
            delta = self.directions[self.current_direction]
            delta_x = delta[0]
            delta_y = delta[1]
            if random.random() > 0.6:
                self.current_direction = (self.current_direction + 1) % len(
                    self.directions
                )
        return delta_x, delta_y

