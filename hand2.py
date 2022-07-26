# -*- encoding: utf-8 -*-
import cv2
import mediapipe as mp

# 使用手势模型
hands = mp.solutions.hands
draw = mp.solutions.drawing_utils
# 设置样式
styleDot = draw.DrawingSpec(color=(0, 0, 255), thickness=5)
# 线的样式
styleLine = draw.DrawingSpec(color=(0, 255, 255), thickness=10)

# static_image_mode=False,  静态图像就是true
# max_num_hands=2,   检测的手的状态
# model_complexity=1,        默认1
# min_detection_confidence=0.5,   最低置信度  越大检测的置信度越高
# min_tracking_confidence=0.5   追踪 的最低置信度
h = hands.Hands()

cap = cv2.VideoCapture(0)

while 1:
    ret, img = cap.read()
    if ret:
        height = img.shape[0]
        width = img.shape[1]
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = h.process(imgRGB)
        # print(result.multi_hand_landmarks)
        if result.multi_hand_landmarks:
            # 检测每一个手
            for handlms in result.multi_hand_landmarks:
                # hands.HAND_CONNECTIONS 点和点之间用线连接
                draw.draw_landmarks(img, handlms, hands.HAND_CONNECTIONS, styleDot, styleLine)
                for i, lm in enumerate(handlms.landmark):
                    # print(i, lm.x, lm.y)  # 点坐标比例
                    xpos = int(lm.x * width)
                    ypos = int(lm.y * height)
                    # 显示第几个点
                    cv2.putText(img, str(i), (xpos - 25, ypos + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 2)
                    print(i, xpos, ypos)  # 位置

        cv2.imshow('img', img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyWindows()
