from Gomoku.Player import Player
from Gomoku.Game import Board
from Gomoku.Game import BoardRenderer


def start_until_game_over(player1: Player, player2: Player, board_renderer: BoardRenderer = None):
    """

    :param player1:
    :param player2:
    :param board_renderer:
    :return:
    """
    board = Board()
    while True:
        if board_renderer is not None:
            board.render(board_renderer)

        if board.current_player == Board.o:
            player1.take_action(board, is_output_action=board_renderer is not None)
        else:
            player2.take_action(board, is_output_action=board_renderer is not None)

        is_over, winner = board.result()
        if is_over:
            if board_renderer is not None:
                board.render(board_renderer)
            return winner
