from abc import ABCMeta, abstractmethod


class BoardRenderer(metaclass=ABCMeta):

    @abstractmethod
    def render(self, board):
        """
        :param board:
        :return:
        """
