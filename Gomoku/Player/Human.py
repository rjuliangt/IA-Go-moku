from Gomoku.Game import Board
from Gomoku.Player import Player


class Human(Player):

    def __init__(self, name="Human"):
        self.name = name

    def __str__(self):
        return "----- Human -----"

    def take_action(self, board: Board, is_output_action=True, running_output_function=None, is_stop=None):
        """
        :param board:
        :param is_output_action:
        :param running_output_function:
        :param is_stop:
        :return:
        """
        print("{0} It's turn to {0}, human player.".format(self.name))
        while True:
            input_str = input(
                "{0}}\"...\"：\n"
                "Please input the coordinates {0} wants to move, "
                "the format is \"[Row],[Column]\":\n".format(self.name))

            try:
                if input_str.isdigit():
                    print("\nPlease enter full coordinates.\n")
                    continue
                action = [int(index) for index in input_str.split(",")]
            except:
                print("\nThe input format is incorrect. Please try again.\n")
                continue

            if not board.step(action):
                print("\nCannot move here. Please try again.\n")
                continue

            print("({1}, {2})\nHuman player {0} moves ({1}, {2})\n".format(self.name, action[0], action[1]))
            break

        return action
