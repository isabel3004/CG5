from Base3DObjects import Point


class BezierMotion:
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, start_time: float, end_time: float):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.start_time = start_time
        self.end_time = end_time

    def get_current_position(self, current_time: float, out_pos: Point):
        if current_time < self.start_time:
            out_pos.x = self.p1.x
            out_pos.y = self.p1.y
            out_pos.z = self.p1.z
        elif current_time > self.end_time:
            out_pos.x = self.p4.x
            out_pos.y = self.p4.y
            out_pos.z = self.p4.z
        else:
            r = (current_time - self.start_time) / (self.end_time - self.start_time)
            out_pos.x = self.p1.x * (1.0 - r)*(1.0 - r)*(1.0 - r) + self.p2.x * (1.0 - r)*(1.0 - r)*r + self.p3.x * (1.0 - r)*r*r + self.p4.x * r*r*r
            out_pos.y = self.p1.y * (1.0 - r)*(1.0 - r)*(1.0 - r) + self.p2.y * (1.0 - r)*(1.0 - r)*r + self.p3.y * (1.0 - r)*r*r + self.p4.y * r*r*r
            out_pos.z = self.p1.z * (1.0 - r)*(1.0 - r)*(1.0 - r) + self.p2.z * (1.0 - r)*(1.0 - r)*r + self.p3.z * (1.0 - r)*r*r + self.p4.z * r*r*r


if __name__ == '__main__':
    p = Point(2.5,2.2,2.14)
    c = 1.4
    print(p * c)