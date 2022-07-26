# -*- encoding: utf-8 -*-
import cv2
import numpy as np
import math


# 多边形剪裁 points=[[],[],[]] 必须大于3，不做check了
def CutImgByPolylines(image, points):
    pts = np.array(points, np.int32)
    mask = np.zeros(image.shape[0:2], dtype="uint8")
    # cv2.polylines(pls, pts=[pts], isClosed=True, color=(255, 255, 255), thickness=3)
    cv2.fillPoly(mask, [pts], color=[255, 255, 255])  # 填充
    return cv2.bitwise_and(image, image, mask=mask)


if __name__ == '__main__':
    # img = np.zeros((500, 500, 3), np.uint8)
    # img[:] = (128, 128, 128)
    # points = [[200, 200], [300, 100], [400, 200], [400, 400], [200, 400]]
    # img = CutImgByPolylines(img, points)
    # cv2.imshow('Polylines', img)
    # cv2.waitKey(0)
    # x = math.cos(math.radians(60))
    # print(x * x)  # 0.03015368960704583
    print(math.sqrt(13))
