# -*- encoding: utf-8 -*-
import cv2
import mediapipe as mp
import math, time
from common import *
from process_img import *
from utils import max_util
from keyboard import *
from pose_mp import showPose
from control_computer import *

# 使用手势模型
hands = mp.solutions.hands

draw = mp.solutions.drawing_utils
# 设置样式
styleDot = draw.DrawingSpec(color=(252, 191, 0), thickness=3)
# 线的样式
styleLine = draw.DrawingSpec(color=(255, 255, 255), thickness=2)

cap = cv2.VideoCapture(0)
width = 1536
height = 864
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cm = CircleManager(width, height)
circle4 = Circle4Manager()
fpsTime = time.time()

kb = KeyBoard(width, height)
lm = LineManager()
controlM = ControlMouse(width, height)


# 显示圆
def showCircle(img, multi_hand_landmarks):
    isShowCircle = False  # 显示圆
    if len(multi_hand_landmarks) <= 0:
        return img, False
    for hs in multi_hand_landmarks:
        # 判断左右手  x17 > x5 就是右手
        if int(hs.landmark[17].x * width) > int(hs.landmark[5].x * width):
            continue
        y16, y14 = int(hs.landmark[16].y * height), int(hs.landmark[14].y * height)
        y20, y18 = int(hs.landmark[20].y * height), int(hs.landmark[18].y * height)
        y10, y12 = int(hs.landmark[10].y * height), int(hs.landmark[12].y * height)
        if y16 - y14 - 30 > 0 and y20 - y18 - 30 > 0 and y10 > y12:
            isShowCircle = True
            # 中指和食指 靠拢
            x12 = int(hs.landmark[12].x * width)
            x8, y8 = int(hs.landmark[8].x * width), int(hs.landmark[8].y * height)
            l = (x8 - x12) * (x8 - x12) + (y8 - y12) * (y8 - y12)
            cm.active_id = 0
            if l < 1400:
                id = cm.getId(x12, y12)
                if id > 0:
                    cm.updateActiveCircle(x12, y12)
                    break

    if isShowCircle:
        img = cm.show(img, 0.6)
    return img, isShowCircle


# 显示刷新率FPS
def showFPS(img):
    global fpsTime
    cTime = time.time()
    fps_text = 1 / (cTime - fpsTime)
    fpsTime = cTime
    cv2.putText(img, "FPS: " + str(int(fps_text)), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    return img


# 剪裁图像
def showCutImg(img, multi_hand_landmarks):
    # 大拇指2 3 4
    points = []
    if len(multi_hand_landmarks) <= 0:
        return img, False
    for hs in multi_hand_landmarks:
        y12, y10 = int(hs.landmark[12].y * height), int(hs.landmark[10].y * height)
        y16, y14 = int(hs.landmark[16].y * height), int(hs.landmark[14].y * height)
        y20, y18 = int(hs.landmark[20].y * height), int(hs.landmark[18].y * height)
        # 中指， 小拇指 无名指握住
        if y16 - y14 - 30 > 0 and y20 - y18 - 30 > 0 and y12 - y10 - 30 > 0:
            # 判断大拇指和食指是否垂直  --> 近似  (2, 4)  (6, 8)
            x2, x4 = hs.landmark[2].x * width, hs.landmark[4].x * width
            y2, y4 = hs.landmark[2].y * height, hs.landmark[4].y * height
            x6, x8 = hs.landmark[6].x * width, hs.landmark[8].x * width
            y6, y8 = hs.landmark[6].y * height, hs.landmark[8].y * height
            # 向量求夹角
            x24, x68 = x2 - x4, x6 - x8
            y24, y68 = y2 - y4, y6 - y8
            t00 = x24 * x68 + y24 * y68
            t20 = x24 * x24 + y24 * y24
            t21 = x68 * x68 + y68 * y68
            if t00 * t00 >= t20 * t21 * 0.3:  # 夹角不在范围内
                return img, False
            # 使用 1 和 10
            points.append([int(hs.landmark[1].x * width), int(hs.landmark[1].y * height) + 30])
            points.append([int(hs.landmark[14].x * width), int(y8 - 40)])
        else:
            return img, False
    if len(points) < 4:
        return img, False
    # 调整points
    tmp = points[2]
    points[2] = points[3]
    points[3] = tmp
    return CutImgByPolylines(img, points), True


# 显示四个圆圈
def showCircle4Img(img, multi_hand_landmarks):
    if multi_hand_landmarks is None:
        return img, False
    for hs in multi_hand_landmarks:
        # 判断左右手  x17 > x5 就是右手
        if int(hs.landmark[17].x * width) < int(hs.landmark[5].x * width):
            continue

        x0, y0 = int(hs.landmark[0].x * width), int(hs.landmark[0].y * height)
        x3, y3 = int(hs.landmark[3].x * width), int(hs.landmark[3].y * height)
        x4, y4 = int(hs.landmark[4].x * width), int(hs.landmark[4].y * height)

        y14, y16 = int(hs.landmark[14].y * height), int(hs.landmark[16].y * height)
        y10, y12 = int(hs.landmark[10].y * height), int(hs.landmark[12].y * height)
        y6, y8 = int(hs.landmark[6].y * height), int(hs.landmark[8].y * height)
        y18, y20 = int(hs.landmark[18].y * height), int(hs.landmark[20].y * height)

        if x0 <= int(width / 2) + 30 or y18 + 5 <= y20 or y6 + 5 <= y8 or y10 + 5 <= y12 or y14 + 5 <= y16:
            return img, False

        root = (x0, y0)
        h = max_util([y0 - y8, y0 - y12, y0 - y16, y0 - y20])
        if x4 > x3 and circle4.active_id > 0:
            circle4.drawRunCircle(img, root, h)
        elif x3 > x4 and y3 > y4:
            x12 = int(hs.landmark[12].x * width)
            circle4.showCircle(img, root, h, x12)
            return img, True

    return img, False


# 显示每个点的id
def showID(img, multi_hand_landmarks):
    for handlms in result.multi_hand_landmarks:
        for i, lm in enumerate(handlms.landmark):
            # print(i, lm.x, lm.y)  # 点坐标比例
            xpos = int(lm.x * width)
            ypos = int(lm.y * height)
            # 显示第几个点
            cv2.putText(img, str(i), (xpos - 25, ypos + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 2)
    return img


def showKeyBoard(img, multi_hand_landmarks):
    if multi_hand_landmarks is None:
        return img, False
    iShow = False

    for hs in multi_hand_landmarks:
        x17, x5 = int(hs.landmark[17].x * width), int(hs.landmark[5].x * width)
        x8, y8 = int(hs.landmark[8].x * width), int(hs.landmark[8].y * height)
        y6 = int(hs.landmark[6].y * height)
        # 判断左右手  x17 > x5 就是右手
        if x17 > x5:
            y16, y14 = int(hs.landmark[16].y * height), int(hs.landmark[14].y * height)
            y20, y18 = int(hs.landmark[20].y * height), int(hs.landmark[18].y * height)
            y10, y12 = int(hs.landmark[10].y * height), int(hs.landmark[12].y * height)
            if y16 - y14 - 30 > 0 and y20 - y18 - 30 > 0 and y10 > y12:
                # 中指和食指 靠拢
                x12 = int(hs.landmark[12].x * width)

                l = (x8 - x12) * (x8 - x12) + (y8 - y12) * (y8 - y12)
                if l < 2500:
                    iShow = True
                    img = kb.drawAll(img)
                elif l > 3500:
                    kb.cleanText()
                    iShow = False
            else:
                kb.cleanText()
                iShow = False

        elif x17 < x5:  # 左手
            if kb.active:
                if y8 < y6:
                    img = kb.event(img, x8, y8)
                else:
                    kb.update_time()
                iShow = True

            if len(multi_hand_landmarks) == 1:
                kb.cleanText()
                iShow = False
    return img, iShow


def showLine(img, multi_hand_landmarks):
    if len(multi_hand_landmarks) <= 0:
        return img, False
    for hs in multi_hand_landmarks:
        # 判断左右手  x17 > x5 就是右手
        if int(hs.landmark[17].x * width) > int(hs.landmark[5].x * width):
            continue
        y16, y14 = int(hs.landmark[16].y * height), int(hs.landmark[14].y * height)
        y20, y18 = int(hs.landmark[20].y * height), int(hs.landmark[18].y * height)
        y10, y12 = int(hs.landmark[10].y * height), int(hs.landmark[12].y * height)
        y6, y8 = int(hs.landmark[6].y * height), int(hs.landmark[8].y * height)
        if y14 < y16 and y10 < y12 and y20 > y18 and y8 < y6:
            x8 = int(hs.landmark[8].x * width)
            lm.draw(img, x8, y8)

    return img, False


# 控制鼠标
def control_mouse(img, multi_hand_landmarks):
    if len(multi_hand_landmarks) <= 0:
        return img, False
    for hs in multi_hand_landmarks:
        if int(hs.landmark[17].x * width) < int(hs.landmark[5].x * width):
            continue
        y16, y14 = int(hs.landmark[16].y * height), int(hs.landmark[14].y * height)
        y20, y18 = int(hs.landmark[20].y * height), int(hs.landmark[18].y * height)
        y10, y12 = int(hs.landmark[10].y * height), int(hs.landmark[12].y * height)
        y6, y8 = int(hs.landmark[6].y * height), int(hs.landmark[8].y * height)

        x2, x4 = hs.landmark[2].x * width, hs.landmark[4].x * width

        if y14 < y16 and y10 < y12 and y20 > y18 and y8 < y6:
            if x4 > x2:
                x8 = int(hs.landmark[8].x * width)
                controlM.move(x8, y8)

            else:
                controlM.click()

            return img, True

    return img, False


def show(img, multi_hand_landmarks):
    img, ok = showCircle4Img(img, multi_hand_landmarks)
    if ok:
        kb.cleanText()
        lm.clean()
        return img

    # circle4.cleanData()
    img, ok = showCircle(img, multi_hand_landmarks)
    if ok:
        kb.cleanText()
        lm.clean()
        return img
    cm.cleanData()
    img, ok = showCutImg(img, multi_hand_landmarks)
    if ok:
        kb.cleanText()
        lm.clean()
        return img

    img, ok = showKeyBoard(img, multi_hand_landmarks)
    if ok:
        lm.clean()
        return img

    img, ok = control_mouse(img, multi_hand_landmarks)
    if ok:
        kb.cleanText()
        lm.clean()
        return img

    img, ok = showLine(img, multi_hand_landmarks)
    if ok:
        kb.cleanText()
        return img
    return img


mp_hand = hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2)
while cap.isOpened():
    ret, img = cap.read()
    if not ret:
        continue
    img.flags.writeable = False  # 提高性能
    img = cv2.flip(img, 1)
    height = img.shape[0]
    width = img.shape[1]
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = showPose(img, imgRGB)
    result = mp_hand.process(imgRGB)
    if result.multi_hand_landmarks:
        for hs in result.multi_hand_landmarks:
            draw.draw_landmarks(img, hs, hands.HAND_CONNECTIONS, styleDot, styleLine)
        img = show(img, result.multi_hand_landmarks)
        # img = showID(img, result.multi_hand_landmarks)
    else:
        kb.cleanText()

    cv2.imshow('img', showFPS(img))
    if cv2.waitKey(1) == ord('q'):
        break

mp_hand.close()
cap.release()
cv2.destroyAllWindows()
