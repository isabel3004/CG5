from Base3DObjects import Point


class BezierMotion:
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, start_time: float, end_time: float):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.start_time = start_time
        self.end_time = end_time

    def get_current_position(self, current_time: float):
        if current_time < self.start_time:
            return self.p1
        elif current_time > self.end_time:
            return self.p4
        else:
            r = (current_time - self.start_time) / (self.start_time - self.end_time)
            c1 = (1-r)**3
            c2 = (1-r)**2 * r
            c3 = (1-r) * r**2
            c4 = r**3
            return self.p1 * c1 + self.p2 * c2 + self.p3 * c3 + self.p4 * c4