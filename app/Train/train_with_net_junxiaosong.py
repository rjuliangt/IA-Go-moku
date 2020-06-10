import collections
import datetime
import os
import random

import numpy as np

import Game.Board as BOARD
from IA.Network.PolicyValueNet_from_junxiaosong import PolicyValueNet_from_junxiaosong, data_augmentation_new
from Game.Game import start_until_game_over
from Player.IA_MCTS import IA_MCTS
from Player.IA_MCTS_Net import IA_MCTS_Net
from console_select import select_yes_or_no


def train_with_net_junxiaosong(network: PolicyValueNet_from_junxiaosong, allow_user_input=True, round_times=0):
    batch_size = 512
    temp = 1
    learning_rate = 2e-3
    lr_multiplier = 1.0
    num_train_steps = 5
    kl = 0
    kl_targ = 0.02

    pure_mcts_search_times = 1000

    AI_mcts_search_times = 400

    win_ratio = 0
    check_point = 50

    all_play_data = collections.deque(maxlen=10000)
    all_play_data_count = 0
    player = IA_MCTS_Net(policy_value_function=network.predict,
                         board_to_xlabel=network.board_to_xlabel,
                         is_training=True,
                         search_times=AI_mcts_search_times,
                         greedy_value=5.0,
                         is_output_analysis=False,
                         is_output_running=False)

    is_output_log = select_yes_or_no("Please choose whether to output the training log file. "
                                     "[Y/y] output，[N/n] not output.\n"
                                     "(y): ", default=True) if allow_user_input else True

    log_file = open(network.model_dir + "out.log", mode="a", encoding="utf-8")
    if is_output_log:
        log_file.write("\n\n-------------------------------------------")
        print("The training log file will be saved to: {}".format(network.model_dir + "out.log"))

    try:
        i = 1
        print("Latest model record saving...")
        network.model.save(network.model_dir + "latest.h5")
        print("The latest model record saved to: \'{}\'".format(network.model_dir + "latest.h5"))
        print("Training start time: {0},\n"
              "Training model path: {1}\n".
              format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), network.model_dir))
        if is_output_log:
            log_file.write("Training start time: {0},\n"
                           "Training model path: {1}\n\n".
                           format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), network.model_dir))

        print("The training is about to begin. Press <Ctrl-C> to end the training.\n"
              "-----------------------------------------------")
        while True:

            print("Self playing...")
            board_inputs, all_action_probs, values = player.self_play(temp=temp)

            print("Round: {},Step: {}, ".format(i, len(values)), end="")
            if is_output_log:
                log_file.write("Round: {}, Step: {}, ".format(i, len(values)))

            play_data = \
                data_augmentation_new(x_label=board_inputs, y_label=(all_action_probs, values))

            # play_data = list(zip(board_inputs, new_action_probs, values))
            all_play_data.extend(play_data)
            all_play_data_count += len(play_data)

            print("Total board data collection: {}".format(all_play_data_count))
            if is_output_log:
                log_file.write("Total board data collection: {}\n".format(all_play_data_count))

            if len(all_play_data) > batch_size:

                print(" Neural network training...")
                if is_output_log:
                    log_file.write("Neural network training...\n")

                will_train_play_data = random.sample(all_play_data, batch_size)

                board_inputs, all_action_probs, values = [], [], []
                for board_input, all_action_prob, value in will_train_play_data:
                    board_inputs.append(board_input)
                    all_action_probs.append(all_action_prob)
                    values.append(value)

                old_probs, old_value = network.model.predict_on_batch(np.array(board_inputs))

                loss = network.evaluate(x_label=board_inputs, y_label=(all_action_probs, values))
                loss = loss[0]

                entropy = network.get_entropy(x_label=board_inputs)

                for train_step in range(num_train_steps):

                    network.train(x_label=board_inputs, y_label=(all_action_probs, values),
                                  learning_rate=learning_rate * lr_multiplier)

                    new_probs, new_value = network.model.predict_on_batch(np.array(board_inputs))

                    kl = np.mean(np.sum(old_probs * (np.log(old_probs + 1e-10) - np.log(new_probs + 1e-10)), axis=1))
                    if kl > kl_targ * 4:
                        break

                if kl > kl_targ * 2 and lr_multiplier > 0.1:
                    lr_multiplier /= 1.5
                elif kl < kl_targ / 2 and lr_multiplier < 10:
                    lr_multiplier *= 1.5

                print("[ KL divergence: {:.5f}, lr_multiplier: {:.3f}, "
                      "loss: {:.3f}, entropy: {:.3f} ]".format(kl, lr_multiplier, loss, entropy))
                if is_output_log:
                    log_file.write("[ KL divergence: {:.5f}, lr_multiplier: {:.3f}, "
                                   "loss: {:.3f}, entropy: {:.3f} ]\n".format(kl, lr_multiplier, loss, entropy))

            if i % check_point == 0:
                print(" Neural network evaluating...")
                if is_output_log:
                    log_file.write("Neural network evaluating...\n")

                pure_mcts = IA_MCTS(name="evaluate", greedy_value=5.0, search_times=pure_mcts_search_times,
                                    is_output_analysis=False, is_output_running=False)
                training_mcts = IA_MCTS_Net(name="training", policy_value_function=network.predict,
                                            board_to_xlabel=network.board_to_xlabel,
                                            search_times=AI_mcts_search_times, greedy_value=5.0,
                                            is_output_analysis=False, is_output_running=False)
                win_times, lose_times, draw_times = 0, 0, 0
                for j in range(10):
                    if j % 2 == 0:
                        winner = start_until_game_over(training_mcts, pure_mcts)
                        if winner == BOARD.o:
                            win_times += 1
                        elif winner == BOARD.x:
                            lose_times += 1
                        else:
                            draw_times += 1
                    else:
                        winner = start_until_game_over(pure_mcts, training_mcts)
                        if winner == BOARD.x:
                            win_times += 1
                        elif winner == BOARD.o:
                            lose_times += 1
                        else:
                            draw_times += 1
                    print("{0} games, {1} wins, {2} loses, {3} draws".
                          format(j + 1, win_times, lose_times, draw_times))
                    if is_output_log:
                        log_file.write("{0} games, {1} wins, {2} loses, {3} draws\n".
                                       format(j + 1, win_times, lose_times, draw_times))

                current_win_ratio = win_times / 10.0
                if current_win_ratio > win_ratio:
                    win_ratio = current_win_ratio
                    print("New record of win rate!")
                    print("Best model record saving...")
                    if is_output_log:
                        log_file.write("New record of win rate!\n")

                    best_model_path = network.model_dir + "best_" + "{}_{}.h5".format(pure_mcts_search_times, win_times)
                    network.model.save(best_model_path)
                    print("The best model record saved to: \'{}\'".format(best_model_path))

                    for old_win_times in range(win_times):
                        old_model = network.model_dir + "best_{}_{}.h5".format(pure_mcts_search_times, old_win_times)
                        if os.path.exists(old_model):
                            os.remove(old_model)

                    if is_output_log:
                        log_file.write("The best model record saved to: \'{}\'\n".format(best_model_path))

                if current_win_ratio == 1.0 and pure_mcts_search_times < 5000:
                    pure_mcts_search_times += 1000
                    win_ratio = 0
                    print("MCTS AI {}".format(pure_mcts_search_times))
                else:
                    print("{}, MCTS AI {}".format(current_win_ratio, pure_mcts_search_times))

                print("Latest model record saving...")
                network.model.save(network.model_dir + "latest.h5")
                print("The latest model record saved to: \'{}\'".format(network.model_dir + "latest.h5"))
                if is_output_log:
                    log_file.write("The latest model record saved to: \'{}\'\n".format(network.model_dir + "latest.h5"))
                    log_file.write("[{}]\n\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            if i == round_times:
                raise KeyboardInterrupt
            i += 1
    except KeyboardInterrupt:
        print("Exit training.")
        print("Latest model record saving...")
        network.model.save(network.model_dir + "latest.h5")
        print("The latest model record saved to: \'{}\'".format(network.model_dir + "latest.h5"))
        if is_output_log:
            log_file.write("Exit training.\n"
                           "The latest model record saved to: \'{}\'".format(network.model_dir + "latest.h5"))
        log_file.close()
