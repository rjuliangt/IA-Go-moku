from abc import ABCMeta, abstractmethod


class Network(metaclass=ABCMeta):

    @abstractmethod
    def create_net(self):
        """
       :return:
       """

    @abstractmethod
    def train(self, x_label, y_label):
        """

       :param x_label:
       :param y_label:
       :return:
       """
