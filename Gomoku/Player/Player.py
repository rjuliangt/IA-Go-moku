from abc import ABCMeta, abstractmethod
from Gomoku.Game import Board


class Player(metaclass=ABCMeta):

    @abstractmethod
    def take_action(self, board: Board, is_output_action=True, running_output_function=None, is_stop=None):
        """
        :param board:
        :param is_output_action:
        :param running_output_function:
        :param is_stop:
        :return:
        """
