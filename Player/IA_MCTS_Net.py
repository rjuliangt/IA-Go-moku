import numpy as np
import copy

from Game.Board import Board
import Game.Board as BOARD
from IA.TreeSearch import MonteCarloTreeSearch
from IA.TreeNode import TreeNode
from Player.Player import Player

import time


class IA_MCTS_Net(MonteCarloTreeSearch, Player):

    def __init__(self, policy_value_function, board_to_xlabel, name="AI_MCTS_Net",
                 is_training=False, search_times=2000, greedy_value=5.0,
                 is_output_analysis=True, is_output_running=True):
        """

        :param policy_value_function:
        :param board_to_xlabel:
        :param name:
        :param is_training:
        :param search_times:
        :param greedy_value:
        :param is_output_analysis:
        :param is_output_running:
        """
        super().__init__()
        self.name = name

        self.policy_value_function = policy_value_function
        self.board_to_xlabel = board_to_xlabel
        self.is_training = is_training
        self.search_times = search_times
        self.greedy_value = greedy_value
        self.is_output_analysis = is_output_analysis
        self.is_output_running = is_output_running

    def __str__(self):
        return "----- IA -----\n" \
               "----- IA with neural network -----\n" \
               "search times: {}\n" \
               "greedy value: {}\n".format(self.search_times, self.greedy_value)

    def reset(self):
        self.root = TreeNode(prior_prob=1.0)

    def take_action(self, board: Board, is_output_action=True, running_output_function=None, is_stop=None):
        """

        :param board:
        :param is_output_action:
        :param running_output_function:
        :param is_stop:
        :return:
        """
        if is_output_action:
            print("{0} It's turn to {0}, AI player.".format(self.name))
            print("Thinking...")

        self.reset()
        self.run(board, self.search_times, running_output_function, is_stop=is_stop)

        actions, probs = self.get_action_probs()

        flatten_actions = []
        for one_action in actions:
            flatten_actions.append(one_action[0] * BOARD.board_size + one_action[1])

        if self.is_training:
            flatten_action = np.random.choice(flatten_actions,
                                              p=0.75 * probs + 0.25 * np.random.dirichlet(0.3 * np.ones(len(probs))))
        else:
            flatten_action = np.random.choice(flatten_actions, p=probs)

        # flatten_action -> action
        action = (flatten_action // BOARD.board_size, flatten_action % BOARD.board_size)

        board.step(action)

        if self.is_output_analysis:
            action_probs = np.zeros((BOARD.board_size, BOARD.board_size))
            # probs -> action_probs
            for one_action, one_prob in zip(actions, probs):
                action_probs[one_action[0], one_action[1]] = one_prob

            self.output_analysis(action_probs)

        if is_output_action:
            print("IA {0} ({1}, {2})\nAI player {0} moves ({1}, {2})".format(self.name, action[0], action[1]))

        return action

    def self_play(self, temp=1e-3):
        """
        :param temp:
        :return:
        """
        board_inputs, all_action_probs, current_player = [], [], []
        board = Board()
        self.reset()

        while True:
            self.run(board, self.search_times)

            actions, probs = self.get_action_probs(temp=temp)
            action_probs = np.zeros((BOARD.board_size, BOARD.board_size))

            for action, prob in zip(actions, probs):
                action_probs[action[0], action[1]] = prob

            board_inputs.append(self.board_to_xlabel(board))
            all_action_probs.append(action_probs)
            current_player.append(board.current_player)

            # action -> flatten_action
            flatten_actions = []
            for one_action in actions:
                flatten_actions.append(one_action[0] * BOARD.board_size + one_action[1])

            flatten_action = np.random.choice(flatten_actions,
                                              p=0.75 * probs + 0.25 * np.random.dirichlet(0.3 * np.ones(len(probs))))

            # flatten_action -> action
            action = (flatten_action // BOARD.board_size, flatten_action % BOARD.board_size)

            board.step(action)

            # 重置根节点。 Reset the root node.
            if action in self.root.children:
                self.root = self.root.children[action]
                self.root.parent = None
            else:
                self.reset()

            is_over, winner = board.result()
            if is_over:
                values = np.zeros(len(current_player))
                if winner != 0:
                    values[np.array(current_player) == winner] = 1
                    values[np.array(current_player) != winner] = -1
                return board_inputs, all_action_probs, values

    def get_action_probs(self, temp=1e-3):
        """
        :param temp:
        :return:
        """
        action_visits = [(action, node.visited_times) for action, node in self.root.children.items()]
        actions, visits = zip(*action_visits)

        def softmax(x):
            y = np.exp(x - np.max(x))
            y /= np.sum(y)
            return y

        probs = softmax(1.0 / temp * np.log(np.array(visits) + 1e-10))
        return actions, probs

    def output_analysis(self, action_probs):
        """
        :param action_probs:
        :return:
        """
        print("----------------------------\n"
              "IA： IA analysis:\n"
              "Format: [Decision probability(%) | #calculations]")
        print_array = [["" for _ in range(BOARD.board_size + 1)] for _ in range(BOARD.board_size + 1)]

        index_string = [""] + [str(i) for i in range(BOARD.board_size)]

        print_array[0] = index_string
        for row in range(BOARD.board_size):
            print_array[row + 1][0] = str(row)

        for i in range(BOARD.board_size):
            for j in range(BOARD.board_size):
                if (i, j) in self.root.children:
                    visited_times = float(self.root.children[(i, j)].visited_times)
                    print_array[i + 1][j + 1] = "{0:.1f}%".format(action_probs[i][j] * 100) + "|" + str(
                        int(visited_times))

        for i in range(BOARD.board_size + 1):
            for j in range(BOARD.board_size + 1):
                print("{:<15}".format(print_array[i][j]), end="")
            print("")
        print("----------------------------")

    def run(self, start_board: Board, times, running_output_function=None, is_stop=None):
        """
        :param start_board:
        :param times:
        :param running_output_function:
        :param is_stop:
        :return:
        """

        for i in range(times):
            board = copy.deepcopy(start_board)
            if is_stop is not None:
                if is_stop():
                    running_output_function(" Game stopped.")
                    return
            if i % 50 == 0 and running_output_function is not None:
                running_output_function("{} / {}".format(i, times))
                time.sleep(0.01)
            if i % 20 == 0 and self.is_output_running:
                print("\rrunning: {} / {}".format(i, times), end="")

            node, value = self.traverse(self.root, board)

            node.backpropagate(-value)
        print("\r                      ", end="\r")

    def traverse(self, node: TreeNode, board: Board):
        """

        :param node:
        :param board:
        :return:
        """
        while True:
            if len(node.children) == 0:
                break
            action, node = node.choose_best_child(c=self.greedy_value)
            board.step(action)

        is_over, winner = board.result()
        if is_over:
            if winner == board.current_player:
                value = 1.0
            elif winner == -board.current_player:
                value = -1.0
            else:
                value = 0.0
            return node, value

        action_probs, value = self.policy_value_function(board)

        for action, probability in action_probs:
            _ = node.expand(action, probability)

        return node, value
