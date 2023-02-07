import json
import threading
import numpy as np
import argparse
from time import sleep
from base_template import BaseRobot
from glob import glob
parser = argparse.ArgumentParser()

parser.add_argument("--exp-name", type=str, default="extrovert_1")
parser.add_argument("--config", type=str, default="config_template_extrovert.json")


class MainFrame:
    def __init__(self, config: dict) -> None:
        self.robot = BaseRobot(config)
        self.no_interest=None
        self.name=""

    def small_talk_introduction(self):
        # Initial greetings
        thr = threading.Thread(target=self.robot.hello_gesture, args=(), kwargs={})
        thr.start()
        self.robot.greeting_1()
        self.robot.get_user_name()  # SPEECH RECOGNITION
        self.name = self.robot.knowledge["user_name"]
        self.robot.greeting_with_name()
        reply_how_are_you = self.robot.get_how_are_you()  # SPEECH RECOGNITION
        # interest = self.robot.analyse_interest(reply_how_are_you)
        # return interest

    def introduction(self):
        # greetings and name
        self.small_talk_introduction()

        # find feelings on scale
        self.robot.grade_feelings()


    def find_game_interest(self):
        # check if the user wants to play
        self.robot.do_you_want_to_play()
        reply_want_to_play = self.robot.get_want_to_play()  # SPEECH RECOGNITION

        self.no_interest = reply_want_to_play

        if not reply_want_to_play:
            self.robot.say_goodbye()
            self.robot.finish_interaction()
            return True, self.robot.return_knowledge()

    def rules_interaction(self):
        self.robot.check_rules()
        reply_game_rules = self.robot.get_game_rules()  # SPEECH RECOGNITION
        if not reply_game_rules:
            self.robot.explain_game()

    def play_rock_paper_scissors(self):
        play = True
        while play:
            self.robot.start_game_countdown()
            game_thread_1 = threading.Thread(
                target=self.robot.play_game_sound, args=(), kwargs={}
            )
            game_thread_1.start()
            self.robot.rps_gesture()
            sleep(1)
            self.robot.get_user_move()  # SPEECH RECOGNITION

            self.robot.analyse_rps_results()
            cheers = threading.Thread(target=self.robot.congrat_last_winner())
            self.robot.winlose_gesture()
            cheers.start()

            # Play again?
            reply_play_again = self.robot.get_play_again()  # SPEECH RECOGNITION
            if reply_play_again == False:
                play = False
                self.robot.say_goodbye_game()
                self.robot.finish_interaction()
                return True, self.robot.return_knowledge()
            self.robot.let_play_again()

            reply_play_again = self.robot.get_play_again()  # SPEECH RECOGNITION
            if reply_play_again == False:
                play = False
                self.robot.say_goodbye_game()
                self.robot.finish_interaction()
                return True, self.robot.return_knowledge()

    def main(self):

        # Initialize the robot and connect to SIC
        self.robot.init_robot()

        self.introduction()


        self.robot.gpt3()

        # initialise game
        self.find_game_interest()

        if self.no_interest==False:
            return self.robot.return_knowledge()

        self.rules_interaction()

        self.play_rock_paper_scissors()

        return self.robot.return_knowledge()


if __name__ == "__main__":
    num = len(glob(r"C:\Users\moham\Desktop\TEST_1\examples\TA-group-13-main\experiment_results\*"))+1
    args = parser.parse_args()
    # Load the configuration file
    with open(f"config\{args.config}") as json_file:
        config = json.load(json_file)

    main_frame = MainFrame(config)
    knowledge_dict = main_frame.main()
    with open(f"experiment_results\knowledge_{args.exp_name}_{main_frame.name}_{num}.json", "w") as json_file:
        json.dump(knowledge_dict, json_file)
