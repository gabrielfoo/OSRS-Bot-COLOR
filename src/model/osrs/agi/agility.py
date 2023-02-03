import time
import numpy as np
from abc import abstractmethod
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from typing import Callable, List
import pyautogui
import inspect
import utilities.game_launcher as launcher
import pathlib
import utilities.imagesearch as imsearch
import cv2

kMark_of_grace=clr.RED
kObstacle_next=clr.Color([0, 255, 0])
kObstacle_next_uavai = clr.Color([0xC8,0xFF,0])
kMark_of_grace_raw = clr.Color([0xA5, 0x8C, 0x0B]) #816C07
TIMEOUT = 40

class OSRSAgility(OSRSBot, launcher.Launchable):
    Obstacle: List = []
    Mouseover_Text: List = []
    DropPoints: List = []

    def __init__(self, bot_title, description):
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.bHighAlch = False
        self.running_time = 360
        self.api_m = MorgHTTPSocket()
        self.options_set = True

    def launch_game(self):
        if launcher.is_program_running("RuneLite"):
            self.log_msg("RuneLite is already running. Please close it and try again.")
            return
        settings = pathlib.Path(__file__).parent.joinpath("custom_settings.properties")
        launcher.launch_runelite_with_settings(self, settings)

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)
        self.options_builder.add_checkbox_option("bHighAlch","High Alch?",[" "])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "bHighAlch":
                self.bHighAlch = True if len(options[option]) else False
            elif option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"High Alchemy activated: {str(self.bHighAlch)}.")


    def main_loop(self):
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        state = self.Obstacle[0]

        while time.time() - start_time < end_time:   
            # -- Perform bot actions here --
            self.log_msg(f"Current Obstacle: {state}")

            if self.get_run_energy() >= 50:
                self.toggle_run(toggle_on=True)

            self.GoNextWithTimeout("Failed to go next Obstacle")

            if self.bHighAlch:
                self.DoHighAlch()
                self.GoNextWithTimeout("Failed to go next Obstacle after High Alchemy")

            ## the below if else statement will need to change between obstacles
            if state in self.DropPoints:
                if self.CheckDrop():
                    time.sleep(rd.fancy_normal_sample(0.777,0.999))
                    self.BackToStart(state)
                    state = self.Obstacle[0]
                    continue
            elif state == self.Obstacle[-1]:
                self.mouse.move_to(self.win.minimap.random_point(), mouseSpeed='fastest') #hover at minimap
                self.DoTaskWhileCheckAgi([], 10, "Back to start..")
                time.sleep(rd.fancy_normal_sample(0.8,0.9))
                self.BackToStart(state)                
            else:
                self.DoTaskWhileCheckAgi([self.HoverNextTarget, self.ForceForward], TIMEOUT, "Checking for xp gain..")
                
            state = self.GetNextObstacle(state)
            
            self.GoNextWithTimeout("Fail to get Mark of Grace")
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
    
    def bAgiXpGain(self) -> int:
        #self.log_msg(f"Agility xp: {self.api_m.get_skill_xp_gained('Agility')}")
        return self.api_m.get_skill_xp("Agility")

    def GoNext(self, forced = False) -> bool:
        if next_point := self.get_nearest_tag(kObstacle_next) or self.get_nearest_tag(kMark_of_grace):
            self.mouse.move_to(next_point.random_point(), mouseSpeed='champion')
            if forced or self.mouseover_text(contains=self.Mouseover_Text) or self.mouseover_text(contains="Mark"):
                if not self.mouse.click(check_red_click=True):
                    return False
                return True
        return False
    
    def GoNextWithTimeout(self, error_msg: str) -> None:
            start_time = time.time()
            halfway_timeout = start_time + TIMEOUT / 2
            timeout = start_time+ TIMEOUT

            while not self.GoNext(forced=True if time.time() > halfway_timeout else False) and time.time() < timeout:
                time.sleep(rd.fancy_normal_sample(0.2, 0.3))

            if(time.time() > timeout):
                self.FailSafe(error_msg)   
    
    def HoverNextTarget(self) -> None:
        if nextTgt := self.get_nearest_tag(kObstacle_next_uavai) \
             or self.get_nearest_tag(kMark_of_grace) \
             or self.get_nearest_tag(kObstacle_next):
            self.mouse.move_to(nextTgt.random_point(), mouseSpeed='fastest')


    def ForceForward(self) -> None:
        temp = time.time() % 5
        if temp >= 0.0 and temp <= 0.1 and self.api_m.get_is_player_idle(0.1):
            self.log_msg("Idle timeout detected: Force go to next point")
            self.GoNext(forced = True)

            
    def DoTaskWhileCheckAgi(self, tasks: List[Callable], timeoutSecs: float, log_msg: str):
        self.log_msg(log_msg)

        startAgiXp = self.bAgiXpGain()
        start = time.time()

        while startAgiXp == self.bAgiXpGain():
            for task in tasks:
                task()
            if(time.time() >= start + timeoutSecs):
                self.FailSafe(f"Failed at {inspect.stack()[0][3]}")
            time.sleep(0.01)

    def FailSafe(self, log_msg: str = "Failsafe activated") -> None:
        self.log_msg(log_msg)
        self.logout()
        self.stop()
        
    def CheckDrop(self) -> bool:
        startHp = self.api_m.get_hitpoints()[0]
        startAgiXp = self.bAgiXpGain()

        timeout = time.time() + TIMEOUT

        self.log_msg("Player is moving, check if player drop.")
        
        while startAgiXp == self.bAgiXpGain() and time.time() < timeout:
            self.HoverNextTarget()
            if(startHp > self.api_m.get_hitpoints()[0]):
                self.log_msg("Player has dropped from the course.")
                return True
            time.sleep(0.02)
        
        if(time.time() > timeout):
            self.FailSafe(f"Failed at {inspect.stack()[0][3]}")
        self.log_msg("Player did not drop")
        return False

    def GetNextObstacle(self, currentObstacle: str) -> str:
        for i, v in enumerate(self.Obstacle): 
            if v == currentObstacle:
                return self.Obstacle[i + 1] if i < len(self.Obstacle) - 1 else self.Obstacle[0]

        return ""

    def Moving(self) -> bool:
        xyz = self.api_m.get_player_position()
    
    def DoHighAlch(self) -> None:
        pyautogui.press("F6")
        self.mouse.move_to(self.win.spellbook_normal[34].random_point(), mouseSpeed='fastest')
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[11].random_point(), mouseSpeed='fast')
        self.mouse.click()


    def BackToStart(self, state) -> None:
        if state in self.DropPoints:
            self.log_msg(f"Fell at: {state}")
        else:
            self.log_msg("Back to start")

        minimap_rect = self.win.minimap
        if rectAgiIcon := imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("minimap", "agility.png"), minimap_rect):
            self.mouse.move_to(rectAgiIcon.random_point(), mouseSpeed='fastest')
            self.mouse.click()
        else:
            self.log_msg("Unable to find Agility icon! Check if the minimap is zoomed out. Failsafe activated.")
            self.FailSafe()

        time.sleep(0.333)
        timeout = time.time() + TIMEOUT

        while not self.api_m.get_is_player_idle(0.1) and time.time() < timeout:
            self.HoverNextTarget()
            time.sleep(rd.fancy_normal_sample(0.04, 0.06))

        if(time.time() > timeout):
            self.FailSafe(f"Failed at {inspect.stack()[0][3]}")

        self.log_msg("Next obstacle found or player stopped.") 


        
