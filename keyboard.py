# -*- encoding: utf-8 -*-
import cv2
import time


class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


class KeyBoard(object):
    def __init__(self, width, height):
        # 键盘
        self.keyboard_keys = [["1", "2", "3"],
                              ["4", "5", "6"],
                              ["7", "8", "9"]]

        self.buttonList = []
        for k in range(len(self.keyboard_keys)):
            for x, key in enumerate(self.keyboard_keys[k]):
                self.buttonList.append(Button([100 * x + 100, 100 * k + 150], key))

        self.text = ""
        self.active = False
        self.width = width
        self.height = height
        self.pre_time = 0

    def cleanText(self):
        self.text = ""
        self.active = False

    def update_time(self):
        self.pre_time = time.time()

    def drawAll(self, img):
        self.active = True
        for button in self.buttonList:
            x, y = button.pos
            w, h = button.size
            cv2.rectangle(img, button.pos, (x + w, y + h), ((x + w) % 255, 200, (y + h) % 255), cv2.FILLED)
            cv2.putText(img, button.text, (x + 25, y + 55), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)

        x, y = self.buttonList[0].pos  # 计算位置
        cv2.putText(img, self.text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        return img

    def event(self, img, posx, posy):
        if self.active is False:
            return img
        tx = float(time.time())
        if tx - self.pre_time > 0.8:
            # 3秒才能输入
            for button in self.buttonList:
                x, y = button.pos
                w, h = button.size
                if x + 10 <= posx <= x + w - 10 and y + 10 <= posy <= y + h - 10:
                    self.text = self.text + button.text
                    break
            self.pre_time = tx
        return img
