from IA.Network.Network import Network

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Input
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import regularizers
import tensorflow.keras.backend as K

tf.compat.v1.disable_eager_execution()

import Game.Board as BOARD
from Function import get_data_augmentation


def data_augmentation_new(x_label, y_label):

    all_action_probs, values = y_label
    extend_data = []
    for board_input, action_probs, value in zip(x_label, all_action_probs, values):
        for i in [0, 1, 2, 3]:
            new_board_input = np.array([np.rot90(one_board_input, i) for one_board_input in board_input])
            new_action_probs = np.rot90(np.flipud(action_probs.reshape(BOARD.board_size, BOARD.board_size)), i)
            extend_data.append((new_board_input,
                                np.flipud(new_action_probs).flatten(),
                                value))
            new_board_input = np.array([np.fliplr(one_board_input) for one_board_input in new_board_input])
            new_action_probs = np.fliplr(new_action_probs)
            extend_data.append((new_board_input,
                                np.flipud(new_action_probs).flatten(),
                                value))
    return extend_data


def data_augmentation(x_label, y_label):
    all_action_probs, values = y_label

    extend_xlabel = []
    extend_ylabel_action_probs = []
    extend_ylabel_value = []

    for board_input in x_label:
        augmentation_board = np.array([get_data_augmentation(one_board_input) for one_board_input in board_input])
        board_augmentation = np.array(list(zip(*augmentation_board)))
        extend_xlabel.extend(np.array([one_augmentation for one_augmentation in board_augmentation]))

    for action_probs in all_action_probs:
        extend_action_probs = get_data_augmentation(action_probs.reshape(BOARD.board_size, BOARD.board_size),
                                                    operation=lambda a: a.flatten())
        extend_ylabel_action_probs.extend(extend_action_probs)

    for value in values:
        extend_value = get_data_augmentation(np.array(value))
        extend_ylabel_value.extend(extend_value)

    return extend_xlabel, (extend_ylabel_action_probs, extend_ylabel_value)


class PolicyValueNet_ResNet(Network):

    def __init__(self, is_new_model, model_dir, model_record_path=""):
        self.l2_const = 1e-4

        self.model_dir = model_dir
        self.model_record_path = model_record_path

        if is_new_model:
            self.create_net()
        else:
            self.model = keras.models.load_model(self.model_record_path)

    def __str__(self):
        return "PolicyValueNet_ResNet"

    def create_net(self):
        def _residual_block(x_input):
            x = x_input
            x = layers.Conv2D(filters=32, kernel_size=(3, 3), strides=(1, 1), padding='same',
                              data_format="channels_first", kernel_regularizer=regularizers.l2(self.l2_const))(x)
            x = layers.BatchNormalization()(x)
            x = layers.Activation('relu')(x)
            x = layers.Conv2D(filters=32, kernel_size=(3, 3), strides=(1, 1), padding='same',
                              data_format="channels_first", kernel_regularizer=regularizers.l2(self.l2_const))(x)
            x = layers.BatchNormalization()(x)
            x = layers.add([x, x_input])
            x = layers.Activation('relu')(x)
            return x

        net = input_net = Input((4, BOARD.board_size, BOARD.board_size))
        net = layers.Conv2D(filters=32, kernel_size=(3, 3), padding="same", strides=(1, 1),
                            data_format="channels_first", kernel_regularizer=regularizers.l2(self.l2_const))(net)
        net = layers.BatchNormalization()(net)
        net = layers.Activation('relu')(net)

        for _ in range(3):
            net = _residual_block(net)

        policy_net = layers.Conv2D(filters=2, kernel_size=(1, 1), strides=(1, 1),
                                   data_format="channels_first", kernel_regularizer=regularizers.l2(self.l2_const))(net)
        policy_net = layers.BatchNormalization()(policy_net)
        policy_net = layers.Activation('relu')(policy_net)
        policy_net = layers.Flatten()(policy_net)
        policy_net = layers.Dense(BOARD.board_size * BOARD.board_size, activation="softmax",
                                  kernel_regularizer=regularizers.l2(self.l2_const))(policy_net)

        value_net = layers.Conv2D(filters=2, kernel_size=(1, 1), strides=(1, 1),
                                  data_format="channels_first", kernel_regularizer=regularizers.l2(self.l2_const))(net)
        value_net = layers.BatchNormalization()(value_net)
        value_net = layers.Activation('relu')(value_net)
        value_net = layers.Flatten()(value_net)
        value_net = layers.Dense(32, kernel_regularizer=regularizers.l2(self.l2_const))(value_net)
        value_net = layers.Activation('relu')(value_net)
        value_net = layers.Dense(1, activation="tanh", kernel_regularizer=regularizers.l2(self.l2_const))(value_net)

        self.model = keras.Model(input_net, [policy_net, value_net])
        self.model.compile(optimizer=optimizers.SGD(lr=2e-3, momentum=1e-1, nesterov=True),
                           loss=['categorical_crossentropy', 'mean_squared_error'])

    def board_to_xlabel(self, board):
        x_label = np.zeros((4, BOARD.board_size, BOARD.board_size))
        x_label[0][board.board == board.current_player] = 1
        x_label[1][board.board == -board.current_player] = 1
        if board.last_action is not None:
            x_label[2][board.last_action[0], board.last_action[1]] = 1
        if board.current_player == BOARD.start_player:
            x_label[3][:, :] = 1

        # flip
        flipped_x_label = []
        for one_board in x_label:
            flipped_x_label.append(np.flipud(one_board))
        x_label = np.array(flipped_x_label)

        return x_label

    def train(self, x_label, y_label):

        board_input = np.array(x_label)

        probs, values = y_label
        probs_output = np.array(probs)
        values_output = np.array(values)

        self.model.fit(board_input, [probs_output, values_output],
                       batch_size=len(x_label), verbose=0)

    def predict(self, board):
        board_input = self.board_to_xlabel(board)
        board_input = board_input.reshape((-1, 4, BOARD.board_size, BOARD.board_size))

        probs, value = self.model.predict_on_batch(board_input)
        probs = probs.reshape((BOARD.board_size, BOARD.board_size))

        action_probs = []
        for available_action in board.available_actions:
            action_probs.append((available_action, probs[available_action[0], available_action[1]]))

        return action_probs, value[0][0]

    def evaluate(self, x_label, y_label):
        board_input = np.array(x_label)

        probs, values = y_label
        probs_output = np.array(probs)
        values_output = np.array(values)

        return self.model.evaluate(board_input, [probs_output, values_output], batch_size=len(board_input), verbose=0)

    def get_entropy(self, x_label):
        board_input = np.array(x_label)
        probs, _ = self.model.predict_on_batch(board_input)
        return -np.mean(np.sum(probs * np.log(probs + 1e-10), axis=1))
