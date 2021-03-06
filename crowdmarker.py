"""
File: crowdmarker.py
Author: Marcos Cardenas-Zelaya
Email: marcoscz@yorku.ca
Github: https://github.com/marcoscz1995
Description: Crowdmarker takes in user defined array of comments, points and
    key codes that are set to keyboard macros to insert comments with
    associated points into the Crowdmark platform to increase marking time.
"""


from math import floor

import pyautogui as pyg
from PIL import ImageFont
from evdev import InputDevice, categorize, ecodes

font = ImageFont.truetype('arial.ttf', 14)

class CrowdMarker:
    def __init__(self, comments, next_booklet, perfect_score,
                 kybrd_event, max_score):
        self.comments = comments
        self.kybrd_event = "/dev/input/event" + str(kybrd_event)
        self.max_score = max_score
        self.next_booklet = next_booklet
        self.perfect_score = perfect_score

    def enter_comment_mode_get_click_position(self):
        # enter comment mode, left click to add comment, get click position
        pyg.press('V')
        pyg.click()
        (current_x, current_y) = pyg.position()
        return (current_x, current_y)

    def add_comment(self, comment, current_x, current_y):
        # note:long comments will change the verticle position of btns below it
        # comments is a list of size 4
        # we get only comment_content. index on a list is O(1).
        # time complx of  this function: O(1)
        comment_content = comment[0]
        x_move_comment = 12
        y_move_comment = 15
        (updated_x, update_y) = (current_x +
                                 x_move_comment, current_y +
                                 y_move_comment)
        pyg.click(updated_x, update_y)
        pyg.write(comment_content)

    def add_points(self, comment, current_x, current_y):
        # note:long comments will change the verticle position of btns below it
        # comments is a list of size 4
        # we get only comment_content. index on a list is O(1).
        # time complx of  this function: O(2*1) = O(1)
        points = comment[1]
        x_move_points = comment[2]
        y_move_points = comment[4]
        (updated_x, update_y) = (current_x +
                                 x_move_points, current_y +
                                 y_move_points)
        pyg.click(updated_x, update_y)
        pyg.write(str(points))

    def save_comment(self, comment, current_x, current_y):
        x_move_save = comment[3]
        y_move_save = comment[4]
        (updated_x, update_y) = (current_x +
                                 x_move_save, current_y +
                                 y_move_save)
        pyg.click(updated_x, update_y)

    def enter_score(self):
        pyg.press('enter')

    def enter_score_move_to_next_booklet(self):
        pyg.press('enter', presses=2)

    def enter_perfect_score(self):
        max_score = str(self.max_score)
        pyg.press(max_score)
        self.enter_score_move_to_next_booklet()

    def add_comment_points(self, comment):
        (current_x, current_y) = self.enter_comment_mode_get_click_position()
        self.add_comment(comment, current_x, current_y)
        self.add_points(comment, current_x, current_y)
        self.save_comment(comment, current_x, current_y)

    def keyboard_input(self):
        keyboard = InputDevice(self.kybrd_event)
        for event in keyboard.read_loop():
            if event.type == ecodes.EV_KEY:
                key = categorize(event)
                if key.keystate == key.key_down:
                    if key.keystate == key.key_down:
                        if key.keycode == self.next_booklet:
                            self.enter_score_move_to_next_booklet()
                        elif key.keycode == self.perfect_score:
                            self.enter_perfect_score()
                        elif key.keycode == 'KEY_ESC':
                            return False
                        else:
                            if key.keycode in self.comments:
                                comment_pnts = self.comments.get(key.keycode)
                                self.add_comment_points(comment_pnts)
                            else:
                                pass


class Comment:
    """
    Input: comment
    Output: the verticle change in pixels of a the comment
    This class finds the verticle pixel hight of a comment that will fit
    in the Crowdmark comment box as long comments will cause the box height
    to increase. This is to tell how much pyautogui needs
    to move vertically to insert commnets/points/save comments.

    """
    y_txt_area_pxls = 252
    pxls_b4_frst_ovrflow = 803
    y_default_change = 108
    x_move_point = 255
    x_move_save = 26
    y_move_overflow = 20

    def __init__(self, comments):
        self.comments = {
            comment[2]:
            [comment[0], comment[1],
             self.x_move_point, self.x_move_save,
             self.set_y_move(comment[0])]
            for comment in comments}

    def set_y_move(self, comment):
        cmnt_pxl_y = font.getsize(comment)[0]
        if cmnt_pxl_y > self.pxls_b4_frst_ovrflow:
            pxls_aftr_frst_ovrflw = cmnt_pxl_y - self.pxls_b4_frst_ovrflow
            y_ovrflw_cnt = floor(pxls_aftr_frst_ovrflw / self.y_txt_area_pxls)
            y_pxls_to_add = y_ovrflw_cnt * self.y_move_overflow
            y_ovrflow_change = self.y_default_change + y_pxls_to_add
            return y_ovrflow_change
        return self.y_default_change


if __name__ == "__main__":
    '''
    Replace the info in user_input for the comment and points you want,
    and whichever keyboard key you want to associate it with.

    Change MAX_SCORE to the max score of the question you are marking.

    Change NEXT_BOOKLET to whichever key you want to move to next umarked,
    booklet, or leave as 'KEY_F'. Recall, KEY_F saves a booklets score and
    moves to the next unmarked booklet.

    Change PERFECT_SCORE to whichever key you want to insert a perfect score,
    or leave as 'KEY_G'. Recall, KEY_G enter a perfect score and moves to
    the next unmarked booklet.


    Happy Crowdmarking!
    '''

    MAX_SCORE = enter max score here
    NEXT_BOOKLET = 'KEY_F'
    PERFECT_SCORE = 'KEY_G'
    KEYBOARD_EVENT_NUMBER = enter your keyboard event number

    user_input = [['enter your comment here.', enter point here,
                   "enter key here"]]

    comments = Comment(user_input)
    ta = CrowdMarker(comments.comments, NEXT_BOOKLET, PERFECT_SCORE,
                     KEYBOARD_EVENT_NUMBER, MAX_SCORE)
    ta.keyboard_input()
