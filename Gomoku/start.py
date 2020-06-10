from Gomoku import Game as Game
from Gomoku.Game import ConsoleRenderer
from Gomoku.Player import IA_MCTS
from Gomoku.Player import IA_MCTS_Net

from Gomoku.console_select import select_player, select_network, set_AI_conf
from Gomoku.Player import Human
from Gomoku.configure import Configure


def start():
    conf = Configure()
    conf.get_conf()

    def player_init(player_selected, name):
        if player_selected == 1:
            return Human(name=name)
        elif player_selected == 2:
            search_times, greedy_value = set_AI_conf(search_times=2000, greedy_value=5.0)
            return IA_MCTS(name=name,
                           search_times=search_times,
                           greedy_value=greedy_value,
                           is_output_analysis=conf.conf_dict["AI_is_output_analysis"])
        elif player_selected == 3:
            network = select_network()
            search_times, greedy_value = set_AI_conf(search_times=400, greedy_value=5.0)
            return IA_MCTS_Net(name=name,
                               policy_value_function=network.predict,
                               board_to_xlabel=network.board_to_xlabel,
                               is_training=False,
                               search_times=search_times,
                               greedy_value=greedy_value,
                               is_output_analysis=conf.conf_dict["AI_is_output_analysis"])

    player1_selected, name1 = select_player("Please input first player. Press <Ctrl-C> to end\n"
                                            "1: Human\n"
                                            "2: AI with pure Monte Carlo tree search\n"
                                            "3: AI with Monte Carlo tree search & neural network\n"
                                            ": ", allowed_input=[1, 2, 3])

    player1 = player_init(player1_selected, name1)

    player2_selected, name2 = select_player("Please input second player. Press <Ctrl-C> to end\n"
                                            "1: Human\n"
                                            "2: AI with pure Monte Carlo tree search\n"
                                            "3: AI with Monte Carlo tree search & neural network\n"
                                            ": ", allowed_input=[1, 2, 3])

    player2 = player_init(player2_selected, name2)

    console_renderer = ConsoleRenderer()

    print("--------------    Game Start    ---------------")
    winner = Game.start_until_game_over(player1, player2, board_renderer=console_renderer)
    if winner == Board.o:
        print("！\"O\" Congrats! \"O\" wins.")
    elif winner == Board.x:
        print("！\"X\" Congrats! \"X\" wins.")
    else:
        print(" Draw!")
    print("---------------    Game Over    ---------------")


if __name__ == '__main__':
    try:
        start()
    except KeyboardInterrupt:
        exit(0)
