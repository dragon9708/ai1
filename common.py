# -*- encoding: utf-8 -*-
import cv2, math
import random
import numpy as np


class Circle(object):
    def __init__(self, x, y, r, id):
        self.r = r  # 半径
        self.centerX = x
        self.centerY = y
        self.id = id

    def draw(self, img, color):
        cv2.circle(img, (self.centerX, self.centerY), self.r, color, -1)


class Circle2(Circle):
    def __init__(self, x, y, r, id, color):
        super(Circle2, self).__init__(x, y, r, id)
        self.color = color

    def draw(self, img):
        cv2.circle(img, (self.centerX, self.centerY), self.r, self.color, -1)


# 圆管理类
class RandomCircleManager(object):
    # count 圆的个数  随机产生
    def __init__(self, width, height, count):
        self.count = count
        self.active_index = -1  # 激活id
        self.circles = {}
        self.weight = width
        self.height = height

    # 随机多个圆
    def randCircle(self):
        for i in range(1, self.count + 1):
            r = random.randint(60, 100)
            x = random.randint(100, self.weight - 100)
            y = random.randint(100, self.height - 100)
            self.circles[i] = Circle(x, y, r, i)

    def show(self, image, alpha):
        overlay = image.copy()
        for i in range(1, self.count + 1):
            color = (random.randint(50, 200), random.randint(10, 100), random.randint(10, 100))
            if i == self.active_index:
                color = (color[0] - 50, color[1] - 50, color[2] - 50)
            self.circles[i].draw(overlay, color)
        # 融合
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        return image


# 定死的圆
class CircleManager(object):
    def __init__(self, width, height):
        self.active_id = 0  # 激活id
        self.circles = {
            1: Circle(300, 500, 70, 1),
            2: Circle(710, 310, 80, 2),
            3: Circle(300, 180, 90, 3),
        }
        self.weight = width
        self.height = height
        self.colors = {
            1: (255, 100, 0),
            2: (0, 255, 0),
            3: (150, 50, 0),
        }

    def cleanData(self):
        self.active_id = 0

    def show(self, img, alpha):
        overlay = img.copy()
        for i in range(1, len(self.circles) + 1):
            color = self.colors[i]
            if i == self.active_id:
                color = (0, 0, 255)
            self.circles[i].draw(overlay, color)
        # 融合
        return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    # 激活的圆
    def getId(self, check_x, check_y):
        self.active_id = 0
        for i in range(1, len(self.circles) + 1):
            circle = self.circles[i]
            r2 = (check_x - circle.centerX) * (check_x - circle.centerX) + (check_y - circle.centerY) * (check_y - circle.centerY)
            if r2 < (circle.r - 10) * (circle.r - 10):
                self.active_id = circle.id
                return circle.id
        return 0

    # 更新x,y
    def updateActiveCircle(self, x, y):
        aId = self.active_id
        if aId > 0:
            self.circles[aId].centerX = x
            self.circles[aId].centerY = y


# 方块管理类
class SquareManager(object):
    def __init__(self, rect_width):

        # 方框长度
        self.rect_width = rect_width

        # 方块list
        self.square_count = 0
        self.rect_left_x_list = []
        self.rect_left_y_list = []
        self.alpha_list = []

        # 中指与矩形左上角点的距离
        self.L1 = 0
        self.L2 = 0

        # 激活移动模式
        self.drag_active = False

        # 激活的方块ID
        self.active_index = -1

    # 创建一个方块，但是没有显示
    def create(self, rect_left_x, rect_left_y, alpha=0.4):
        self.rect_left_x_list.append(rect_left_x)
        self.rect_left_y_list.append(rect_left_y)
        self.alpha_list.append(alpha)
        self.square_count += 1

    # 更新位置
    def display(self, class_obj):
        for i in range(0, self.square_count):
            x = self.rect_left_x_list[i]
            y = self.rect_left_y_list[i]
            alpha = self.alpha_list[i]

            overlay = class_obj.image.copy()

            if (i == self.active_index):
                cv2.rectangle(overlay, (x, y), (x + self.rect_width, y + self.rect_width), (255, 0, 255), -1)
            else:
                cv2.rectangle(overlay, (x, y), (x + self.rect_width, y + self.rect_width), (255, 0, 0), -1)

            # Following line overlays transparent rectangle over the self.image
            class_obj.image = cv2.addWeighted(overlay, alpha, class_obj.image, 1 - alpha, 0)

    # 判断落在哪个方块上，返回方块的ID
    def checkOverlay(self, check_x, check_y):
        for i in range(0, self.square_count):
            x = self.rect_left_x_list[i]
            y = self.rect_left_y_list[i]

            if (x < check_x < (x + self.rect_width)) and (y < check_y < (y + self.rect_width)):
                # 保存被激活的方块ID
                self.active_index = i

                return i

        return -1

    # 计算与指尖的距离
    def setLen(self, check_x, check_y):
        # 计算距离
        self.L1 = check_x - self.rect_left_x_list[self.active_index]
        self.L2 = check_y - self.rect_left_y_list[self.active_index]

    # 更新方块
    def updateSquare(self, new_x, new_y):
        # print(self.rect_left_x_list[self.active_index])
        self.rect_left_x_list[self.active_index] = new_x - self.L1
        self.rect_left_y_list[self.active_index] = new_y - self.L2


# 四个圆 转圈
class Circle4Manager(object):

    def __init__(self):
        self.circles = {}
        self.cleanData()

    def cleanData(self):
        self.active_id = 0
        self.step_degree = 0
        self.run_circles = [
            Circle(0, 0, 0, 11),
            Circle(0, 0, 0, 12),
            Circle(0, 0, 0, 13),
            Circle(0, 0, 0, 14)
        ]
        self.run_circles_dir = [0, 1, 2, 3]  # 旋转的方向

    def cleanRunCircleData(self, root, rate, br):
        self.step_degree = 0
        cy = int(root[1] - 200 * rate)
        cx = root[0]
        r = int(25 * rate)
        offset = br - 250 * rate
        self.run_circles_dir = [0, 1, 2, 3]
        self.run_circles[0].r = r
        self.run_circles[1].r = r
        self.run_circles[2].r = r
        self.run_circles[3].r = r
        self.run_circles[0].centerX = int(cx - offset)
        self.run_circles[0].centerY = cy
        self.run_circles[1].centerX = cx
        self.run_circles[1].centerY = int(cy + offset)
        self.run_circles[2].centerX = int(cx + offset)
        self.run_circles[2].centerY = cy
        self.run_circles[3].centerX = cx
        self.run_circles[3].centerY = int(cy - offset)

    def calc_run_circle(self, root, rate, h):
        cx, cy = root[0], int(root[1] - 200 * rate)  # 圆心
        br = int(h + 100 * rate)
        r = br - 250 * rate  # 半径
        # 重新计算方向
        if self.step_degree >= 90:
            self.cleanRunCircleData(root, rate, br)
            # 更新一次方向
            tmp = self.run_circles_dir[0]
            for i in range(1, len(self.run_circles_dir)):
                self.run_circles_dir[i - 1] = self.run_circles_dir[i]
            self.run_circles_dir[len(self.run_circles_dir) - 1] = tmp
            return

        degree = math.radians(self.step_degree)
        t1 = r * math.cos(degree)
        t2 = r * math.sin(degree)
        r = int(25 * rate)

        for i, dir in enumerate(self.run_circles_dir):
            x0 = self.run_circles[i].centerX
            y0 = self.run_circles[i].centerY
            if dir == 0:
                x0, y0 = cx - t1, cy + t2
            elif dir == 1:
                x0, y0 = cx + t2, cy + t1
            elif dir == 2:
                x0, y0 = cx + t1, cy - t2
            elif dir == 3:
                x0, y0 = cx - t2, cy - t1
            self.run_circles[i].centerX = int(x0)
            self.run_circles[i].centerY = int(y0)
            self.run_circles[i].r = r

        self.step_degree = self.step_degree + 5

    def calc_active(self, x, y, root, rate, br):
        self.active_id = 0
        for id, circle in self.circles.items():
            xt = circle.centerX - x
            yt = circle.centerY - y
            t = xt * xt + yt * yt
            if t < 200:
                self.active_id = id
                self.cleanRunCircleData(root, rate, br)
                return id
        return 0

    # 画旋转的圆 画4个吧
    def drawRunCircle(self, img, root, h):
        if self.active_id <= 0:
            return img
        c2 = self.circles.get(self.active_id, None)
        if c2 is None:
            return img
        rate = self.get_rate(h)
        # 重新计算圆的位置
        self.calc_run_circle(root, rate, h)

        color = c2.color
        for c in self.run_circles:
            c.draw(img, color)

        return img

    def get_rate(self, h):
        rate = h / 400
        if h > 400:
            rate = 1
        return rate

    # 手掌的根节点， 手掌大小，绘制大小
    def showCircle(self, img, root, h, x):
        # 有个比例
        rootY = root[1]
        rootX = root[0]
        rate = self.get_rate(h)
        r = int(25 * rate)
        x1 = int(56 * rate)
        x2 = int(160 * rate)

        # 在一个大圆上  大圆半径r1
        r1 = int(h + 100 * rate)
        r2 = r1 * r1
        xt1 = x1 * x1
        xt2 = x2 * x2
        y1 = math.sqrt(r2 - xt1)
        y2 = math.sqrt(r2 - xt2)

        self.circles = {
            1: Circle2(rootX - x1, int(rootY - y1), r, 1, (26, 115, 232)),
            2: Circle2(rootX - x2, int(rootY - y2), r, 2, (242, 139, 130)),
            3: Circle2(rootX + x1, int(rootY - y1), r, 3, (253, 214, 99)),
            4: Circle2(rootX + x2, int(rootY - y2), r, 4, (129, 201, 149)),
        }
        for _, circle in self.circles.items():
            circle.draw(img)

        # 画小红圈
        rx = x - 10
        y = math.sqrt(r2 - (rootX - rx) * (rootX - rx))
        ry = int(rootY - y)
        cv2.circle(img, (rx, ry), r + 3, (0, 0, 255), 2)
        # 计算激活的id
        self.calc_active(rx, ry, root, rate, r1)
        return img


class LineManager(object):

    def __init__(self):
        self.points = []

    def clean(self):
        self.points = []

    def draw(self, img, x, y):
        if len(self.points) > 0:
            x0, y0 = self.points[len(self.points) - 1]
            if math.fabs(x0 - x) < 3 and math.fabs(y0 - y) < 3:
                return img
        # if len(self.points) > 100:
        #     self.points = []

        self.points.append([x, y])
        pts = np.array(self.points, np.int32)
        cv2.polylines(img, pts=[pts], isClosed=False, color=(0, 0, 180), thickness=5)
        return img


if __name__ == '__main__':
    img = cv2.imread("./1.jpg")
    img = cv2.resize(img, (1080, 720))

    cm = CircleManager(1080, 720)

    image = cm.show(img, 0.4)

    cv2.imshow('res', image)
    cv2.waitKey(0)
