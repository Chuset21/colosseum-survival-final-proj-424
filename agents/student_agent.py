# Student agent: Add your own agent here
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
        self.valid_moves_set = set()

    def is_pos_in_valid_moves_set(self,  x: int, y: int) -> bool:
        """

        Parameters
        ----------
        cur_pos     a tuple of (x, y) being the current position

        Returns
        -------
        bool        True if the position is in the set, False otherwise
        """
        for i in range(4):
            if (x, y, i) in self.valid_moves_set:
                return True
        return False

    @staticmethod
    def is_within_board_boundaries(chess_board: object, x: int, y: int) -> bool:
        """

        Parameters
        ----------
        chess_board     a numpy array of shape (x_max, y_max, 4)
        cur_pos         a tuple of (x, y) being the current position

        Returns
        -------
        bool            True if the position is within the board bounds, False otherwise
        """
        max_bound = chess_board.shape[0]
        return 0 <= x < max_bound and 0 <= y < max_bound

    def update_valid_moves(self, chess_board: object, cur_pos: (int, int), adv_pos: (int, int), cur_step: int,
                           max_step: int):
        """

        Parameters
        ----------
        chess_board     a numpy array of shape (x_max, y_max, 4)
        cur_pos         a tuple of (x, y) being the current position
        adv_pos         a tuple of (x, y) being the adversary's position
        cur_step        an int being the current number of steps from the original position
        max_step        an int being the max number of steps that can be taken
        """
        x, y = cur_pos
        if cur_pos == adv_pos or not self.is_within_board_boundaries(chess_board, x, y) \
                or self.is_pos_in_valid_moves_set(x, y):
            return

        for i in range(4):
            if not chess_board[x, y, i]:
                self.valid_moves_set.add(((x, y), i))

        cur_step += 1
        if cur_step <= max_step:
            if not chess_board[x, y, 0]:
                self.update_valid_moves(chess_board, (x - 1, y), adv_pos, cur_step, max_step)

            if not chess_board[x, y, 1]:
                self.update_valid_moves(chess_board, (x, y + 1), adv_pos, cur_step, max_step)

            if not chess_board[x, y, 2]:
                self.update_valid_moves(chess_board, (x + 1, y), adv_pos, cur_step, max_step)

            if not chess_board[x, y, 3]:
                self.update_valid_moves(chess_board, (x, y - 1), adv_pos, cur_step, max_step)

        return

    def step(self, chess_board, my_pos, adv_pos, max_step):
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
        # getting valid moves
        self.valid_moves_set.clear()
        self.update_valid_moves(chess_board, my_pos, adv_pos, 0, max_step)
        # now valid_moves_set contains all valid moves

        # dummy return
        return self.valid_moves_set.pop()
