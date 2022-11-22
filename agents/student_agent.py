# Student agent: Add your own agent here
from enum import Enum

from agents.agent import Agent
from store import register_agent


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

    moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

    class WinningHeuristic(Enum):
        NOT_END_GAME = 1  # better than tying?
        WIN = 20000
        LOSS = -20000
        TIE = 0

    @staticmethod
    def is_pos_in_valid_moves_set(valid_moves: set[((int, int), int)], x: int, y: int) -> bool:
        """

        Parameters
        ----------
        valid_moves a set of valid moves
        cur_pos     a tuple of (x, y) being the current position

        Returns
        -------
        bool        True if the position is in the set, False otherwise
        """
        for i in range(4):
            if ((x, y), i) in valid_moves:
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
    def get_valid_moves(chess_board: object, my_pos: (int, int), adv_pos: (int, int), max_step: int) -> \
            set[((int, int), int)]:
        """

        Parameters
        ----------
        chess_board     a numpy array of shape (x_max, y_max, 4)
        my_pos          a tuple of (x, y) being the current position
        adv_pos         a tuple of (x, y) being the adversary's position
        max_step        an int being the max number of steps that can be taken

        Returns
        -------
        set[((int, int), int)]  a set of valid moves
        """
        valid_moves_set = set()
        board_size = chess_board.shape[0]

        def update_valid_moves(cur_pos: (int, int), cur_step: int):
            x, y = cur_pos
            if cur_pos == adv_pos or not StudentAgent.is_within_board_boundaries(board_size, x, y) \
                    or StudentAgent.is_pos_in_valid_moves_set(valid_moves_set, x, y):
                return

            for i in range(4):
                if not chess_board[x, y, i]:
                    valid_moves_set.add(((x, y), i))

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
            return

        update_valid_moves(my_pos, 0)
        return valid_moves_set

    @staticmethod
    def check_endgame(board_size: int, chess_board: object, p0_pos: tuple[int, int], p1_pos: tuple[int, int]) -> int:
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
                for dir, move in enumerate(StudentAgent.moves[1:3]):  # Only check down and right
                    if chess_board[r, c, dir + 1]:
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
            return StudentAgent.WinningHeuristics.NOT_END_GAME
        if p0_score > p1_score:
            return StudentAgent.WinningHeuristics.WIN
        if p0_score < p1_score:
            return StudentAgent.WinningHeuristics.LOSS
        return StudentAgent.WinningHeuristics.TIE

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

        # get all valid moves and choose one at random
        return StudentAgent.get_valid_moves(chess_board, my_pos, adv_pos, max_step).pop()
