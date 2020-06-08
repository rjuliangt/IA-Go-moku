import configparser

class Configure:

    def __init__(self):
        self.conf = configparser.ConfigParser(allow_no_value=True)
        self.conf.read("game.conf")
        self.conf_dict = {}

    def get_conf(self):
        self.conf_dict["o"] = self.conf.getint("Fixed", "o")
        self.conf_dict["x"] = self.conf.getint("Fixed", "x")
        self.conf_dict["empty"] = self.conf.getint("Fixed", "empty")

        self.conf_dict["n_in_a_row"] = self.conf.getint("Changeable", "n_in_a_row")
        self.conf_dict["start_player"] = self.conf.getint("Changeable", "start_player")
        self.conf_dict["board_size"] = self.conf.getint("Changeable", "board_size")
        self.conf_dict["AI_is_output_analysis"] = self.conf.getboolean("AI", "is_output_analysis")

    def set_board_size(self, size):
        self.conf.set("Changeable", "board_size", str(size))
        self.conf.write(open("game.conf", "w"))

    def set_n_in_a_row_game(self, n):
        self.conf.set("Changeable", "n_in_a_row", str(n))
        self.conf.write(open("game.conf", "w"))

    def set_AI_is_output_analysis(self, is_output_analysis):
        self.conf.set("AI", "is_output_analysis", str(is_output_analysis))
        self.conf.write(open("game.conf", "w"))


def run_configure():
    conf = Configure()
    conf.get_conf()

    size = conf.conf_dict["board_size"]
    n_in_a_row = conf.conf_dict["n_in_a_row"]
    AI_is_output_analysis = conf.conf_dict["AI_is_output_analysis"]

    while True:
        input1 = input("1: size. (size >= 3)\n"
                       "Config 1: Please input the size of board. (size >= 3)\n"
                       "size ({}) = ".format(size))
        try:
            input_int = size if len(input1) == 0 else int(input1)
            if input_int < 3:
                print("size 3 \n"
                      "size should be greater than or equal to 3. Please try again.\n")
                continue
            size = input_int
        except:
            print("The input is incorrect. Please try again.\n")
            continue
        break

    while True:
        input2 = input("2: n. (n >= 3  n <= size)\n"
                       "Config 2: Please input how many pieces in a row. (n >= 3 and n <= size)\n"
                       "n ({}) = ".format(n_in_a_row))
        try:
            input_int2 = n_in_a_row if len(input2) == 0 else int(input2)
            if input_int2 < 3:
                print("n 3.\n"
                      "n should be greater than or equal to 3. Please try again.\n")
                continue
            if input_int2 > size:
                print("n size.\n"
                      "n should be less than or equal to size. Please try again.\n")
                continue
            n_in_a_row = input_int2
        except:
            print("\n"
                  "The input is incorrect. Please try again.\n")
            continue
        break

    while True:
        input3 = input("3：[Y/y]，[N/n]\n"
                       "Config 3: Please input the AI search times. [Y/y] output, [N/n] not output.\n"
                       "AI is output analysis ({}) = ".format(AI_is_output_analysis))
        if len(input3) == 0:
            pass
        elif input3 == "n" or input3 == "N":
            AI_is_output_analysis = False
        elif input3 == "y" or input3 == "Y":
            AI_is_output_analysis = True
        else:
            print("\n"
                  "The input is incorrect. Please try again.\n")
            continue
        break

    conf.set_board_size(size)
    conf.set_n_in_a_row_game(n_in_a_row)
    conf.set_AI_is_output_analysis(AI_is_output_analysis)

    print("Success!")


if __name__ == '__main__':
    try:
        run_configure()
    except KeyboardInterrupt:
        exit(0)
