from random import randint


class Shake:
    def __init__(self):
        self.shake_time = 0
        self.shake_x = 0
        self.shake_y = 0
        self.shake_intensity = 5

    def trigger_shake(self, shake_intensity=5, duration=10):
        self.shake_time = duration
        self.shake_intensity = shake_intensity

    def update_shake(self):
        if self.shake_time > 0:
            self.shake_time -= 1
            self.shake_x = randint(-self.shake_intensity, self.shake_intensity)
            self.shake_y = randint(-self.shake_intensity, self.shake_intensity)
        else:
            self.shake_x = 0
            self.shake_y = 0

    def apply_shake(self, x_offset, y_offset):
        return x_offset + self.shake_x, y_offset + self.shake_y
