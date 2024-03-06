import random
from typing import Optional
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

class TackleBot(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0
        self.attack_other_bots = True  # Enable tackling

    def next_move(self, board_bot: GameObject, board: Board):
        current_position = board_bot.position
        game_objects = board.game_objects
        props = board_bot.properties

        # If diamonds are full, set goal position to base
        if props.diamonds >= 4 or (props.milliseconds_left < 10000 and props.diamonds != 0):
            self.goal_position = props.base
            delta_x, delta_y = self.get_direction_to_target(current_position, self.goal_position)
            return delta_x, delta_y

        # Attack nearby enemy
        if self.attack_other_bots:
            bots = [x for x in game_objects if x.type == "BotGameObject" and x.id != board_bot.id]
            closest_bot = None
            closest_distance = float('inf')
            for bot in bots:
                distance = abs(bot.position.x - current_position.x) + abs(bot.position.y - current_position.y)
                if distance < closest_distance:
                    closest_bot = bot
                    closest_distance = distance

            if closest_bot:
                delta_x, delta_y = self.get_direction_to_target(current_position, closest_bot.position)
                return delta_x, delta_y

        delta = self.directions[self.current_direction]
        delta_x = delta[0]
        delta_y = delta[1]
        if random.random() > 0.6:
            self.current_direction = (self.current_direction + 1) % len(self.directions)

        return delta_x, delta_y

    def get_direction_to_target(self, current_position, target_position):
        dx = target_position.x - current_position.x
        dy = target_position.y - current_position.y
        if abs(dx) > abs(dy):
            return (1 if dx > 0 else -1), 0
        else:
            return 0, (1 if dy > 0 else -1)
