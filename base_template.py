import json
import threading
import numpy as np
from copy import copy
from time import sleep
from time import time
from pprint import pprint
from social_interaction_cloud import BasicSICConnector

from openAI import openAI


class BaseRobot:
    def __init__(self, config: json) -> None:
        self.stat_time = time()
        """
        Initializing the connection with SIC
        The config is a json file.
        """
        # pprint(config)
        self.base_config = config["Base_config"]
        self.vision_config = config["Vision_config"]
        self.speech_config = config["Speech_config"]
        self.scripted_config = config["Scripted_config"]
        self.gestures_config = config["Gestures_config"]
        self.speech_speed = self.speech_config["speed"]
        self.speech_volume = self.speech_config["volume"]

        self.server_ip = self.base_config["server_ip"]
        self.language = self.speech_config["dialogflow_language"]
        self.dialogflow_key_file = self.speech_config["dialogflow_key_file"]
        self.dialogflow_agent_id = self.speech_config["dialogflow_agent_id"]

        self.sic = BasicSICConnector(
            server_ip="127.0.0.1",
            dialogflow_language=self.language,
            dialogflow_key_file=self.dialogflow_key_file,
            dialogflow_agent_id=self.dialogflow_agent_id,
        )

        if self.vision_config["use_face_recognition"]:
            self.identifier = None

        self.knowledge = (
            {}
        )  # For now, we'll need to restart the script between experiments

        self.speech = {"intent": "default"}
        self.max_repeat_question = range(3)

    #################################################################################
    # Basic functions
    #################################################################################

    """
    These basic method are used to manage initializations and end of the interaction,
    as well as call backs for different speech recognition events and the listen method.
    """

    def init_robot(self) -> None:
        """
        Initialize the robot
        """
        self.sic.start()
        self.sic.set_language(self.language)
        self.sic.set_speech_param("speed", self.speech_speed)
        self.sic.set_speech_param("volume", self.speech_volume)
        self.sic.wake_up()

    def finish_interaction(self) -> None:
        """
        Finish the interaction
        """
        self.sic.rest()
        self.sic.stop()

    def __call_back(self, call_back_str: str = "Nothing") -> None:
        if call_back_str == None:
            self.speech = {"intent": "default"}
        else:
            self.speech = call_back_str
        print("call_back_str ", call_back_str)

    def _yes_no_with_feet(self, touch_duration=5):
        self.sic.say(self.scripted_config["explain_yes_no_with_feet"][0])
        self.sic.set_led_color(["RightFootLeds", "LeftFootLeds"], ["green", "red"])
        self.sic.say('Press my toe under the green light to select "Yes".')
        self.sic.say('Press my toe under the red light to select "No".')

        self.sic.subscribe_event_listener(
            "RightBumperPressed", self.__call_back({"intent": "answer_yes"})
        )
        self.sic.subscribe_event_listener(
            "LeftBumperPressed", self.__call_back({"intent": "answer_no"})
        )
        self.sic.wait(touch_duration, load=True)
        self.sic.run_loaded_actions(wait_for_any=True)
        self.sic.unsubscribe_event_listener("RightBumperPressed")
        self.sic.unsubscribe_event_listener("LeftBumperPressed")

    def listen(self, flag: str = "none", duration: int = 5) -> None:
        """
        This method is used to listen to the user.
        """
        self.sic.speech_recognition(
            context=flag, max_duration=duration, callback=self.__call_back
        )

    def return_knowledge(self) -> dict:
        """
        Return the knowledge of the robot
        """
        end = (time()) - self.stat_time
        self.knowledge["time"]=end
        return copy(self.knowledge)

    ##################################################################################
    # Analysis in the robot
    ##################################################################################

    def analyse_rps_results(self) -> None:
        # create a comparison table
        # User -- Rock
        if self.knowledge["user_pick"] == "rock":
            if self.knowledge["robot_move"] == "rock":
                self.knowledge["last_win"] = "draw"
            elif self.knowledge["robot_move"] == "paper":
                self.knowledge["last_win"] = "robot"
            else:  # scissor
                self.knowledge["last_win"] = "user"

        # User -- Paper
        elif self.knowledge["user_pick"] == "paper":
            if self.knowledge["robot_move"] == "rock":
                self.knowledge["last_win"] = "user"
            elif self.knowledge["robot_move"] == "paper":
                self.knowledge["last_win"] = "draw"
            else:  # scissor
                self.knowledge["last_win"] = "robot"

        # User -- scissor
        elif self.knowledge["user_pick"] == "scissor":
            if self.knowledge["robot_move"] == "rock":
                self.knowledge["last_win"] = "robot"
            elif self.knowledge["robot_move"] == "paper":
                self.knowledge["last_win"] = "user"
            else:  # scissor
                self.knowledge["last_win"] = "draw"
        # return self.knowledge["last_win"]

    def analyse_interest(self, reply) -> bool:
        """
        Analyse the user's interest in the game
        Interest is a bool. False if the user is not interested, True otherwise
        """
        if self.speech["intent"] == "positive_how_are_you":
            interest = True
        elif self.speech["intent"] == "negative_how_are_you":
            interest = False
        else:
            self.sic.say("I didn't get that. Can you say it again?")
            x = self.get_how_are_you()
            self.analyse_interest(self, x)
        return interest

    ##################################################################################
    # Movements and geastures
    ##################################################################################

    def rps_gesture(self) -> None:
        """
        Gesture to play rock paper scissor
        """
        self.sic.do_gesture("rock_paper_scissors-a962e1/behavior_1")

    def loss_gesture(self) -> None:
        self.sic.do_gesture(self.gestures_config["lose"])

    def win_gesture(self) -> None:
        print(self.gestures_config["win"])
        self.sic.do_gesture(self.gestures_config["win"])

    def hello_gesture(self) -> None:
        self.sic.do_gesture(self.gestures_config["hello"])

    def winlose_gesture(self):
        """
        Perform a gesture depending on the last winner
        """
        if self.knowledge["last_win"] == "user":
            self.loss_gesture()
        elif self.knowledge["last_win"] == "robot":
            self.win_gesture()

    ##################################################################################
    # Speech recognition
    ##################################################################################

    def grade_feelings(self):
        self.sic.say(self.scripted_config["scale_1_10"][0])
        self.listen(flag="0", duration=4)

        if self.speech["intent"] == "answer_scale":
            self.sic.say(
                f'Okay, I feel like a {int((self.speech["parameters"])["number"])} as well.'
            )
            self.knowledge["answer_scale"] = (self.speech["parameters"])["number"]
        else:
            self.sic.say("I feel exactly the same")
            self.knowledge["answer_scale"] = "I dont know"

    def check_rules(self) -> None:
        """
        Ask the user if he knows the rules
        """
        self.sic.say("Okay!")
        self.sic.say("Do you know the rules of rock paper scissors?")
        self.listen(flag="game", duration=3)

    def get_user_rps_results(self) -> bool:
        """
        Recognize the user's move and store it in the knowledge
        """
        self.listen("rock_paper_scissors", duration=3)

        if (
            self.speech["intent"] == "rock"
            or self.speech["intent"] == "paper"
            or self.speech["intent"] == "scissor"
        ):
            user_move = self.speech["entities"]["rock_paper_scissors"]
        self.knowledge["user_move"] = user_move
        return True

    def get_user_name(self) -> None:
        """
        recognize the user's name
        """
        self.listen("answer_name", duration=4)
        count = 2
        for i in range(2):
            if self.speech["intent"] == "answer_name":
                name = (self.speech["parameters"])["name"]
                self.knowledge["user_name"] = name
                break
            else:
                self.sic.say("I missed what you said. What was that?")
                self.listen("answer_name", duration=4)
                if self.speech["intent"] == "answer_name":
                    name = (self.speech["parameters"])["name"]
                    self.knowledge["user_name"] = name
                    break
                else:
                    sleep(2.0)

                    if count == 1:
                        # print(count)
                        name = "G"
                        self.knowledge["user_name"] = name
                        self.sic.say("I will call you G")
                        break
            count -= 1

    ## Im leaving this here in case we want to use it again
    # def get_user_name(self) -> None:
    #     """
    #     recognize the user's name
    #     """
    #     self.listen("answer_name", duration=3)

    #     if self.speech["intent"] == "answer_name":
    #         name = (self.speech["parameters"])["name"]
    #         self.knowledge["user_name"] = name
    #     else:
    #         self.sic.say("I missed what you said. What was that?")
    #         self.get_user_name()

    def get_how_are_you(self) -> bool:
        """
        Ask the user how he is doing
        """
        self.listen("how_are_you", duration=3)

        if self.speech["intent"] == "positive_how_are_you":
            how_are_you = self.speech["text"]
            self.sic.say(" That's good to hear")
            self.sic.say("Wonderful")

            self.knowledge["how_are_you"] = how_are_you
            sleep(1.0)
            return how_are_you

        elif self.speech["intent"] == "negative_how_are_you":
            how_are_you = self.speech["text"]
            self.sic.say("sorry to hear that")
            self.sic.say("don't worry everything will be fine")
            self.sic.say("just smile")
            self.knowledge["how_are_you"] = how_are_you
            sleep(1.0)
            return how_are_you
        else:
            self.sic.say("Sorry, I didn't get that. Can you rephrase?")
            self.get_how_are_you()

    def get_want_to_play(self) -> bool:
        """
        Ask the user if he wants to play again
        """
        temp = True
        while temp:
            if self.speech["intent"] == "answer_yes":
                self.sic.say("Great")
                self.knowledge["wants to play"] = "Yes"
                return True
            elif self.speech["intent"] == "answer_no":
                # self.sic.say("That is okay. Thanks anyways.")
                self.knowledge["wants to play"] = "No"
                return False
            else:
                self.sic.say("Sorry, I didn't get that. Can you rephrase?")
                self.do_you_want_to_play()

    def get_game_rules(self) -> bool:
        """
        Ask the user the rules of the game
        """
        if self.speech["intent"] == "answer_yes":
            self.knowledge["Know_game_rules"] = "Yes"
            return True

        elif self.speech["intent"] == "answer_no":
            self.knowledge["Know_game_rules"] = "No"
            return False

    def get_user_move(self) -> bool:
        """
        Ask the user to make a move
        """
        self.sic.say("What movement did you do?")
        self.listen(flag="answer_rps", duration=5)
        # print("knowledge after answer_rps: ", self.speech)
        if self.speech["intent"] == "answer_rps":
            user_move = (self.speech["parameters"])["rps_entity"]
            print(
                "Speech recognition -- rps answer:",
                (self.speech["parameters"])["rps_entity"],
            )
            self.knowledge["user_pick"] = user_move
            return True

        else:
            for tick in self.max_repeat_question:
                self.sic.say(self.scripted_config["i_missed_it"][tick])
                self.listen(flag="answer_rps", duration=3)
                if self.speech["intent"] == "answer_rps":
                    user_move = (self.speech["parameters"])["rps_entity"]
                    # print("Knowledge after answer_rps second try: ", self.speech)
                    self.knowledge["user_pick"] = user_move
                    return True

            self.sic.say("I believe you chose rock")
            self.knowledge["user_pick"] = "rock"

    def get_play_again(self) -> bool:
        """
        Ask the user if he wants to play again
        """
        self.sic.say(self.scripted_config["do_you_want_play_again"][0])
        self.listen(flag="get_play_again", duration=3)
        loop = True
        while loop:
            if self.speech["intent"] == "answer_yes":
                play_again = True
                self.knowledge["play_again"] = play_again
                return play_again

            elif self.speech["intent"] == "answer_no":
                play_again = False
                self.knowledge["play_again"] = play_again
                return play_again

            else:
                self.sic.say("Can you say it again?")
                self.listen(flag="get_play_again", duration=4)
        return False

    ##################################################################################
    # Scripted conversation
    ##################################################################################

    def greeting_1(self) -> None:
        """
        Greet the user with a scripted greeting
        The selection of sentences, introvert vs extrovert
        is done in the config
        """
        self.sic.say(self.scripted_config["greeting_1"][0])
        self.sic.say(self.scripted_config["greeting_1_name"][0])
        # raise NotImplementedError

    def greeting_with_name(self) -> None:
        """
        Greet the user with the name he gave
        """
        if "user_name" not in self.knowledge.keys():
            self.sic.say("Hello, how are you doing?")
        else:
            self.sic.say(f"Hello {self.knowledge['user_name']}")
            self.sic.say("How are you doing?")

    def do_you_want_to_play(self) -> None:
        """
        Ask the user if he wants to play
        """
        self.sic.say(self.scripted_config["do_you_want_play"][0])
        self.listen(flag="game", duration=3)

    def explain_game(self) -> None:
        """
        Explain the game
        """
        self.sic.say(self.scripted_config["explain_game"][0])
        self.sic.say(self.scripted_config["explain_game"][1])
        self.sic.say(self.scripted_config["explain_game"][2])
        self.sic.say(self.scripted_config["explain_game"][3])
        self.sic.say(self.scripted_config["explain_game"][4])

    def start_game_countdown(self) -> None:
        """
        Start the game countdown
        """
        self.sic.say("Okay, let's start!")

    def play_game_sound(self) -> None:
        """
        Play the sound of the game
        Randomly select a move and return it
        """
        l = ["paper", "rock", "scissor"]
        choice = np.random.choice([0, 1, 2])
        sleep(6)
        self.sic.say("Shoot")
        self.sic.say(f"I played {l[choice]}")
        self.knowledge["robot_move"] = l[choice]

    def congrat_last_winner(self) -> None:
        """
        Congratulate the last winner
        """
        if self.knowledge["last_win"] == "user":
            self.sic.say(self.scripted_config["i_lose"][np.random.randint(0, 2)])
        elif self.knowledge["last_win"] == "robot":
            self.sic.say(self.scripted_config["i_win"][np.random.randint(0, 2)])
        else:
            self.sic.say(self.scripted_config["i_lose"][np.random.randint(0, 2)])

    def let_play_again(self) -> None:
        """
        Ask the user if he wants to play again
        """
        self.start_game_countdown()
        game_thread_1 = threading.Thread(
            target=self.play_game_sound, args=(), kwargs={}
        )
        game_thread_1.start()
        self.rps_gesture()

        self.get_user_move()  # SPEECH RECOGNITION

        self.analyse_rps_results()
        self.robot.analyse_rps_results()
        cheers = threading.Thread(target=self.robot.congrat_last_winner())
        self.robot.winlose_gesture()
        cheers.start()

    def say_goodbye(self) -> None:
        self.sic.say("That's okay, thanks anyway")
        self.sic.say("Goodbye")

    def say_goodbye_game(self) -> None:
        self.sic.say("That's okay")
        self.sic.say(" I hope you still enjoyed playing the game.")
        self.sic.say("Goodbye")

    ##################################################################################
    # GPT3
    ##################################################################################

    def gpt3(self):
        self.sic.say("Do you want to ask me any question?")
        self.listen(flag="GPT3", duration=5)
        gpt3 = openAI()
        loop = True
        count=0
        while loop:
            if self.speech["intent"] == "answer_yes":
                count += 1
                self.knowledge[f"Ask GPT3 {count}"] = "answer_yes"
                self.sic.say("what is your question?")
                self.listen(flag="yes_GPT3", duration=10)

                if self.speech["intent"] != "default":
                    res = gpt3.response(self.speech["text"])
                    print(res)
                    self.sic.say(res)
            elif self.speech["intent"] == "answer_no":
                self.knowledge["Ask GPT3"] = "answer_no"
                self.sic.say("okay,Thanks")
                break
            else:
                self.sic.say("Can you say it again?")
            self.sic.say("Do you have further questions?")
            self.listen(flag="GPT3", duration=4)
