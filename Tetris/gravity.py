from config import GRAV, GRAV_ACCEL, GRAV_THRESH

class Gravity:
    def __init__(self):
        self.speed = GRAV
        self.progress = 0

    def reset_progress(self):
        self.progress = 0

    def update_progress(self, ticks=1):
        self.speed += GRAV_ACCEL * ticks
        self.progress += self.speed * ticks

        if self.progress >= GRAV_THRESH:
            return True
        return False 