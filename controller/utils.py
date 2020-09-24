class Rotator:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.angle = 0

    def rotation(self):
        self.angle = (self.angle + 90) % 360

    def cal_rotate_location(self, x, y):
        if self.angle == 0:
            return x, y
        elif self.angle == 90:
            return y, self.width - x
        elif self.angle == 180:
            return self.width - x, self.height - y
        else:
            return self.height - y, x

    def recover_location(self, x, y):
        if self.angle == 0:
            return x, y
        elif self.angle == 90:
            return self.width - y, x
        elif self.angle == 180:
            return self.width - x, self.height - y
        else:
            return y, self.height - x
