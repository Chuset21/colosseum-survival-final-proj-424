# Student agent: Add your own agent here
import math
from enum import Enum
from typing import Tuple

from agents.agent import Agent
from store import register_agent


def get_max_idx(heuristics: list[float]) -> int:
    result, cur_max = 0, heuristics[0]
    for i, e in enumerate(heuristics):
        if e > cur_max:
            cur_max = e
            result = i
    return result


@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }
        self.autoplay = True

    MOVES = ((-1, 0), (0, 1), (1, 0), (0, -1))
    OPPOSITES = {0: 2, 1: 3, 2: 0, 3: 1}

    class WinningHeuristic(Enum):
        NOT_END_GAME = 1.0  # better than tying?
        WIN = 100.0
        LOSS = -100.0
        TIE = 0.0

    class AntiBoxHeuristic(Enum):
        NOT_SAFE = -20
        SAFE = 0

    class AggressionHeuristic(Enum):
        AGGRESSIVE = 2
        NOT_AGGRESSIVE = 0

    @staticmethod
    def is_visited(valid_moves: dict[tuple[tuple[int, int], int], int], x: int, y: int, cur_step: int) -> bool:
        """

        Parameters
        ----------
        valid_moves a dictionary of valid moves, mapping valid moves to their step count
        x           the current x position
        y           the current y position
        cur_step    an integer denoting the current step

        Returns
        -------
        bool        True if the position is in the dictionary and the corresponding value is less than the current step.
        False otherwise
        """
        for i in range(4):
            if t := valid_moves.get(((x, y), i)):
                if t <= cur_step:
                    return True
        return False

    @staticmethod
    def is_within_board_boundaries(board_size: int, x: int, y: int) -> bool:
        """

        Parameters
        ----------
        board_size      the board size as an integer
        cur_pos         a tuple of (x, y) being the current position

        Returns
        -------
        bool            True if the position is within the board bounds, False otherwise
        """
        return 0 <= x < board_size and 0 <= y < board_size

    @staticmethod
    def get_valid_moves(chess_board: object, my_pos: tuple[int, int], adv_pos: tuple[int, int], max_step: int) -> \
            list[tuple[tuple[int, int], int]]:
        """

        Parameters
        ----------
        chess_board     a numpy array of shape (x_max, y_max, 4)
        my_pos          a tuple of (x, y) being the current position
        adv_pos         a tuple of (x, y) being the adversary's position
        max_step        an int being the max number of steps that can be taken

        Returns
        -------
        list[((int, int), int)]  a list of valid moves
        """
        valid_moves_dict = {}
        board_size = chess_board.shape[0]

        def update_valid_moves(cur_pos: Tuple[int, int], cur_step: int):
            x, y = cur_pos
            if cur_pos == adv_pos or not StudentAgent.is_within_board_boundaries(board_size, x, y) \
                    or StudentAgent.is_visited(valid_moves_dict, x, y, cur_step):
                return

            for i in range(4):
                if not chess_board[x, y, i]:
                    valid_moves_dict[((x, y), i)] = cur_step

            cur_step += 1
            if cur_step <= max_step:
                if not chess_board[x, y, 0]:
                    update_valid_moves((x - 1, y), cur_step)

                if not chess_board[x, y, 1]:
                    update_valid_moves((x, y + 1), cur_step)

                if not chess_board[x, y, 2]:
                    update_valid_moves((x + 1, y), cur_step)

                if not chess_board[x, y, 3]:
                    update_valid_moves((x, y - 1), cur_step)

        # call the backtracking algorithm to get all the valid moves
        update_valid_moves(my_pos, 0)

        return list(valid_moves_dict.keys())

    @staticmethod
    def get_endgame_heuristic(board_size: int, chess_board: object, p0_pos: tuple[int, int], p1_pos: tuple[int, int]) \
            -> float:
        """
        Adapted from world.py.
        Check if the game ends and compute the current score of the agents.

        Returns
        -------
        A winning heuristic value.
        """
        # Union-Find
        father = dict()
        for r in range(board_size):
            for c in range(board_size):
                father[(r, c)] = (r, c)

        def find(pos):
            if father[pos] != pos:
                father[pos] = find(father[pos])
            return father[pos]

        def union(pos1, pos2):
            father[pos1] = pos2

        for r in range(board_size):
            for c in range(board_size):
                for direction, move in enumerate(StudentAgent.MOVES[1:3]):  # Only check down and right
                    if chess_board[r, c, direction + 1]:
                        continue
                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)

        for r in range(board_size):
            for c in range(board_size):
                find((r, c))
        p0_r = find(p0_pos)
        p1_r = find(p1_pos)
        p0_score = list(father.values()).count(p0_r)
        p1_score = list(father.values()).count(p1_r)
        if p0_r == p1_r:
            return StudentAgent.WinningHeuristic.NOT_END_GAME.value
        if p0_score > p1_score:
            return StudentAgent.WinningHeuristic.WIN.value
        if p0_score < p1_score:
            return StudentAgent.WinningHeuristic.LOSS.value
        return StudentAgent.WinningHeuristic.TIE.value

    @staticmethod
    def set_barrier_to_value(chess_board: object, x: int, y: int, direction: int, value: bool):
        """
        Adapted from world.py.
        Set a barrier to True or False.
        """
        # Set the barrier to True
        chess_board[x, y, direction] = value
        # Set the opposite barrier to True
        move = StudentAgent.MOVES[direction]
        chess_board[x + move[0], y + move[1], StudentAgent.OPPOSITES[direction]] = value

    @staticmethod
    def center_heuristic(center: float, x: float, y: float, ) -> float:
        """

        Parameters
        ----------
        center      The center coordinate of the board
        x           The current x coordinate
        y           The current y coordinate

        Returns
        -------
        A heuristic value inversely proportional to the distance to the center of the board
        """
        if x == center and x == y:
            return 1.5
        return 1 / math.sqrt((x - center) ** 2 + (y - center) ** 2)

    @staticmethod
    def anti_box_heuristic(chess_board: object, x: int, y: int) -> int:
        """

        Parameters
        ----------
        chess_board     a numpy array of shape (x_max, y_max, 4)
        x               The current x coordinate
        y               The current y coordinate

        Returns
        -------
        A heuristic value which is negative if the player has 3 or more barriers around it. 0 otherwise.
        """
        count = 0
        for i in range(4):
            if chess_board[x, y, i]:
                count += 1

        if count >= 3:
            return StudentAgent.AntiBoxHeuristic.NOT_SAFE.value
        else:
            return StudentAgent.AntiBoxHeuristic.SAFE.value

    @staticmethod
    def chasing_heuristic(x: float, y: float, adv_pos: tuple[float, float]) -> float:
        """

        Parameters
        ----------
        x               The current x coordinate
        y               The current y coordinate
        adv_pos         The adversary's position

        Returns
        -------
        A heuristic value inversely proportional to the distance between both players.
        """
        return 1 / math.sqrt((x - adv_pos[0]) ** 2 + (y - adv_pos[1]) ** 2)

    @staticmethod
    def aggression_heuristic(x: int, y: int, direction: int, adv_pos: tuple[int, int]) -> int:
        """

        Parameters
        ----------
        x               The current x coordinate
        y               The current y coordinate
        direction       The direction to put the barrier
        adv_pos         The adversary's position

        Returns
        -------
        A heuristic value that is positive if we are beside the opponent and placing a barrier towards them, 0 otherwise
        """
        op_x, op_y = adv_pos
        # we are above, to the right, below or to the left of the opponent respectively
        if (op_x - 1 == x and op_y == y and direction == 2) \
                or (op_x == x and op_y + 1 == y and direction == 3) \
                or (op_x + 1 == x and op_y == y and direction == 0) \
                or (op_x == x and op_y - 1 == y and direction == 1):
            return StudentAgent.AggressionHeuristic.AGGRESSIVE.value
        return StudentAgent.AggressionHeuristic.NOT_AGGRESSIVE.value

    def step(self, chess_board: object, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """
        board_size = chess_board.shape[0]
        # Get the center coordinate of the board
        center = (board_size - 1) / 2
        f_adv_pos = (float(adv_pos[0]), float(adv_pos[1]))
        heuristic_list = []
        valid_moves = StudentAgent.get_valid_moves(chess_board, my_pos, adv_pos, max_step)

        for (x, y), direction in valid_moves:
            StudentAgent.set_barrier_to_value(chess_board, x, y, direction, True)

            end_game_heuristic = StudentAgent.get_endgame_heuristic(board_size, chess_board, (x, y), adv_pos)
            if end_game_heuristic == StudentAgent.WinningHeuristic.WIN.value:
                return (x, y), direction

            anti_box_heuristic = StudentAgent.anti_box_heuristic(chess_board, x, y)
            fx = float(x)
            fy = float(y)
            center_heuristic = StudentAgent.center_heuristic(center, fx, fy)
            chasing_heuristic = StudentAgent.chasing_heuristic(fx, fy, f_adv_pos)
            aggression_heuristic = StudentAgent.aggression_heuristic(x, y, direction, adv_pos)
            StudentAgent.set_barrier_to_value(chess_board, x, y, direction, False)
            heuristic_list.append(
                anti_box_heuristic + center_heuristic + end_game_heuristic + chasing_heuristic + aggression_heuristic)

        # choose the move with the highest heuristic
        return valid_moves[get_max_idx(heuristic_list)]
