import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ...util import *

class ShortestDistance(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def next_move(self, board_bot: GameObject, board: Board):

        props = board_bot.properties
        current_position = board_bot.position
        teleport = find_teleport(current_position, board)
        tele_sorted_list = sorted(teleport, key=lambda d: d[0])
        
        # Analyze new state
        if props.diamonds == 5:
            # Move to base
            base = board_bot.properties.base
            self.goal_position = base
        else:
            # Just roam around
            diamond = find_diamond(current_position, board)
            red_diamond = find_red_diamond(current_position, board)
            blue_diamond = find_blue_diamond(current_position, board)
            red_button = find_red_button(current_position,board)

            sorted_list = sorted(diamond, key=lambda d: d[0])
            sorted_blue = sorted(blue_diamond, key=lambda d: d[0])
            sorted_red = sorted(red_diamond, key=lambda d: d[0])
            sorted_button = sorted(red_button, key=lambda d: d[0])
            base_distance = abs(current_position.x - board_bot.properties.base.x) + abs(current_position.y - board_bot.properties.base.y)
            base_distance_tele = tele_sorted_list[0][0] + abs(tele_sorted_list[1][1].x - board_bot.properties.base.x) + abs(tele_sorted_list[1][1].y - board_bot.properties.base.y)


            self.goal_position = sorted_list[0][1]

            if(props.diamonds >= 3 and (base_distance <= 6 or base_distance_tele <= 6) and sorted_list[0][0] >= 5):
                self.goal_position = board_bot.properties.base
            
            elif(props.milliseconds_left < 8000 and props.diamonds != 0):
                self.goal_position = board_bot.properties.base

            elif (props.diamonds >= 3 and (base_distance <= 6 or base_distance_tele <= 6) and sorted_list[0][0] <= 5):
                if (props.diamonds == 4):
                    self.goal_position = sorted_blue[0][1]
                else :
                    self.goal_position = sorted_list[0][1]

            elif (props.diamonds == 4 and sorted_blue != []):
                self.goal_position = sorted_blue[0][1]

            elif (props.diamonds == 4 and sorted_blue == []) :
                self.goal_position = board_bot.properties.base

            elif (sorted_blue != [] and sorted_red != [] and props.diamonds < 4):
                if (sorted_red[0][0] <= sorted_blue[0][0]) :
                    self.goal_position = sorted_red[0][1]
                    
        current_position = board_bot.position
        if self.goal_position:
            if(tele_sorted_list):
                distance_tele2_goal = abs(tele_sorted_list[1][1].x - self.goal_position.x) + abs(tele_sorted_list[1][1].y - self.goal_position.y)
                way1 = tele_sorted_list[0][0] + distance_tele2_goal
                
                way = abs(current_position.x - self.goal_position.x) + abs(current_position.y - self.goal_position.y)

                if(way1 < way):
                    self.goal_position = tele_sorted_list[0][1]
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
        
        if(delta_x == 0 and delta_y == 0):
            delta_x, delta_y = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])

        return delta_x, delta_y