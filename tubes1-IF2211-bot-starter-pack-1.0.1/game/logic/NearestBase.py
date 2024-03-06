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

        
        current_position = board_bot.position
        base = board_bot.properties.base
        

        sorted_teleport_groups = getAllTeleporterSorted(board,current_position)

        all_diamonds = [x for x in board.game_objects if (x.type=="DiamondGameObject")]
        red_button = [x for x in board.game_objects if (x.type=="DiamondButtonGameObject")]

        
        
        cluster = find_densest(all_diamonds)
        # Find the densest cluster
        densest_cluster = max(cluster, key=len, default=[])
        # Calculate the centroid of the densest cluster
        if densest_cluster:
            centroid_x = sum(d.position.x for d in densest_cluster) / len(densest_cluster)
            centroid_y = sum(d.position.y for d in densest_cluster) / len(densest_cluster)
            densest_centroid = Position(x=int(centroid_x), y=int(centroid_y))
        else:
            densest_centroid = None


        diamond_distance_base , diamond_distance_bot = findDistanceByBotAndBase(all_diamonds,base,current_position)   
        red_button_base , red_button_bot = findDistanceByBotAndBase(red_button,base,current_position)
        diamond_sorted_base = sorted(diamond_distance_base, key=lambda d: d[0])
        diamond_sorted_bot = sorted(diamond_distance_bot, key=lambda d: d[0])
    
        board_width = board.width
        board_height = board.height

        red_button_sorted_base =  sorted(red_button_base, key=lambda d: d[0])
        red_button_sorted_bot = sorted(red_button_bot, key=lambda d: d[0])
        
        base_distance = count_distance(current_position.x, current_position.y, board_bot.properties.base.x, board_bot.properties.base.y)
        

        if props.diamonds >= 4:
            # Move to 
            if(diamond_sorted_bot[0][0] <= 2 and props.diamonds + diamond_sorted_bot[0][3] <= 5):
                self.goal_position = diamond_sorted_bot[0][1]
            else:
                base = board_bot.properties.base
                self.goal_position = base
        else:

            
            # base_distance_tele = tele_sorted_list[0][0] + abs(tele_sorted_list[1][1].x - board_bot.properties.base.x) + abs(tele_sorted_list[1][1].y - board_bot.properties.base.y)
            if(base_distance == 1 and props.diamonds >= 2):
                self.goal_position = base
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
                # elif((diamond_sorted_base[0][2][0] < 0.4 * board_width) and  (diamond_sorted_base[0][2][1] <  0.4 * board_height)) :
                    if(diamond_sorted_bot[0][0] <= 2 ):
                        self.goal_position = diamond_sorted_bot[0][1]
                    else:
                        self.goal_position = diamond_sorted_base[0][1]
                elif(densest_centroid):
                    self.goal_position = densest_centroid
                else:
                    if(red_button_sorted_base != []):
                        if((red_button_sorted_base[0][2][0] < 0.4 * board_width) and (red_button_sorted_base[0][2][1] < 0.4 * board_height)):
                            self.goal_position = red_button_sorted_base[0][1]
                        elif(red_button_sorted_bot[0][0] <= 3):
                            self.goal_position = red_button_sorted_bot[0][1]
                        else:
                            self.goal_position = diamond_sorted_bot[0][1]
            else:
                if(props.diamonds >= 3):
                    self.goal_position = base
                else:
                    self.goal_position = red_button


    
        current_position = board_bot.position
        if self.goal_position:
            shortest_way = count_distance(current_position.x, current_position.y, self.goal_position.x, self.goal_position.y)
            shortest_way_position = self.goal_position

            # Iterate over each pair of teleporters
            for pair_id, teleporters in sorted_teleport_groups.items():
                closest_teleporter, distance_to_closest_teleporter = teleporters[0]
                print(closest_teleporter)
                second_teleporter = teleporters[1][0]

                # Calculate the distance from the second teleporter in the pair to the goal position
                distance_tele2_goal = count_distance(second_teleporter.x, second_teleporter.y, self.goal_position.x, self.goal_position.y)

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

        if(delta_x == 0 and delta_y == 0) :
            delta_x, delta_y = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
        return delta_x, delta_y