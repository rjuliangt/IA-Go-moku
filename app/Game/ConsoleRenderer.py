from Game.BoardRenderer import BoardRenderer
import Game.Board as BOARD
from Game.Board import Board


class ConsoleRenderer(BoardRenderer):

    def render(self, board: Board):
        """

        :param board:
        :return:
        """
        print_array = [["" for _ in range(BOARD.board_size + 1)] for _ in range(BOARD.board_size + 1)]

        index_string = [""] + [str(i) for i in range(BOARD.board_size)]

        print_array[0] = index_string
        for row in range(BOARD.board_size):
            print_array[row + 1][0] = str(row)

        for i in range(BOARD.board_size):
            for j in range(BOARD.board_size):
                if board.board[i, j] == BOARD.o:
                    print_array[i + 1][j + 1] = "O"
                elif board.board[i, j] == BOARD.x:
                    print_array[i + 1][j + 1] = "X"
                else:
                    print_array[i + 1][j + 1] = "."

        for i in range(BOARD.board_size + 1):
            for j in range(BOARD.board_size + 1):
                print("{:^3}".format(print_array[i][j]), end="")
            print("")
