# -*- encoding: utf-8 -*-
import autopy, time


# 控制鼠标
class ControlMouse(object):
    def __init__(self, width, height):
        self.wScr, self.hScr = autopy.screen.size()
        self.width = width
        self.height = height
        self.wrate = self.wScr / self.width
        self.hrate = self.hScr / self.height
        self.movex = -1
        self.movey = -1
        self.pre_time = 0

    def move(self, clocX, clocY):
        movex = int(self.wrate * clocX)
        movey = int(self.hrate * clocY)

        if movey < 0:
            movey = 0

        if movex < 0:
            movex = 0

        if movey > self.hScr:
            movey = int(self.hScr)

        if movex > self.wScr:
            movex = int(self.wScr)

        autopy.mouse.move(movex, movey)
        self.movex = movex
        self.movey = movey
        self.pre_time = time.time()

    # 大拇指移动一定范围点击
    def click(self):
        if self.movex < 0 or self.movey < 0:
            return

        tx = float(time.time())

        if tx - self.pre_time < 0.35:
            return
        self.pre_time = tx
        autopy.mouse.move(self.movex, self.movey)
        autopy.mouse.click()
