from os import close
from scipy.spatial.transform import Rotation
import numpy as np
from math import *  # trigonometry

from Base3DObjects import *


class ModelMatrix:
    def __init__(self):
        self.matrix = [1, 0, 0, 0,
                       0, 1, 0, 0,
                       0, 0, 1, 0,
                       0, 0, 0, 1]
        self.stack = []
        self.stack_count = 0
        self.stack_capacity = 0

    def load_identity(self):
        self.matrix = [1, 0, 0, 0,
                       0, 1, 0, 0,
                       0, 0, 1, 0,
                       0, 0, 0, 1]

    def copy_matrix(self):
        new_matrix = [0] * 16
        for i in range(16):
            new_matrix[i] = self.matrix[i]
        return new_matrix

    def add_transformation(self, matrix2):
        counter = 0
        new_matrix = [0] * 16
        for row in range(4):
            for col in range(4):
                for i in range(4):
                    new_matrix[counter] += self.matrix[row*4 + i] * \
                        matrix2[col + 4*i]
                counter += 1
        self.matrix = new_matrix

    def add_nothing(self):
        other_matrix = [1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1]
        self.add_transformation(other_matrix)

    def add_translation(self, x, y, z):
        other_matrix = [
            1, 0, 0, x,
            0, 1, 0, y,
            0, 0, 1, z,
            0, 0, 0, 1
        ]
        self.add_transformation(other_matrix)

    def add_scale(self, x, y, z):
        other_matrix = [
            x, 0, 0, 0,
            0, y, 0, 0,
            0, 0, z, 0,
            0, 0, 0, 1
        ]
        self.add_transformation(other_matrix)

    def add_rotation_x(self, angle):
        other_matrix = [
            1, 0, 0, 0,
            0, cos(angle), -sin(angle), 0,
            0, sin(angle), cos(angle), 0,
            0, 0, 0, 1
        ]
        self.add_transformation(other_matrix)

    def add_rotation_y(self, angle):
        other_matrix = [
            cos(angle), 0, sin(angle), 0,
            0, 1, 0, 0,
            -sin(angle), 0, cos(angle), 0,
            0, 0, 0, 1
        ]
        self.add_transformation(other_matrix)

    def add_rotation_z(self, angle):
        other_matrix = [
            cos(angle), -sin(angle), 0, 0,
            sin(angle), cos(angle), 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]
        self.add_transformation(other_matrix)

    def push_matrix(self):
        self.stack.append(self.copy_matrix())

    def pop_matrix(self):
        self.matrix = self.stack.pop()

    # mainly for debugging
    def __str__(self):
        ret_str = ""
        counter = 0
        for _ in range(4):
            ret_str += "["
            for _ in range(4):
                ret_str += " " + str(self.matrix[counter]) + " "
                counter += 1
            ret_str += "]\n"
        return ret_str


class ViewMatrix:
    """The ViewMatrix class holds the camera's coordinate frame and
    set's up a transformation concerning the camera's position
    and orientation"""

    def __init__(self):
        self.eye = Point(0, 0, 0)
        self.u = Vector(1, 0, 0)
        self.v = Vector(0, 1, 0)
        self.n = Vector(0, 0, 1)

    def look(self, eye, center, up):
        self.eye = eye
        self._up = up
        self.n = (eye - center).normalize()
        self.u = up.cross(self.n).normalize()
        self.v = self.n.cross(self.u)

    def roll(self, angle):
        c = cos(angle)
        s = sin(angle)
        tmp_u = self.u * c + self.v * s
        self.v = self.u * (-s) + self.v * c
        self.u = tmp_u

    def pitch(self, angle):
        c = cos(angle)
        s = sin(angle)
        tmp_v = self.v * c + self.n * s
        self.n = self.v * (-s) + self.n * c
        self.v = tmp_v

    def yaw(self, angle):
        c = cos(angle)
        s = sin(angle)
        tmp_u = self.u * c + self.n * s
        self.n = self.u * (-s) + self.n * c
        self.u = tmp_u

    def turn(self, angle):
        c = cos(angle)
        s = sin(angle)
        u_x = self.u.x * c + self.u.z * s
        u_y = self.u.y
        u_z = self.u.x * (-s) + self.u.z * c
        self.u = Vector(u_x, u_y, u_z)
        v_x = self.v.x * c + self.v.z * s
        v_y = self.v.y
        v_z = self.v.x * (-s) + self.v.z * c
        self.v = Vector(v_x, v_y, v_z)
        n_x = self.n.x * c + self.n.z * s
        n_y = self.n.y
        n_z = self.n.x * (-s) + self.n.z * c
        self.n = Vector(n_x, n_y, n_z)

        

        

    def slide(self, del_u, del_v, del_n):
        self.eye += self.u * del_u + self.v * del_v + self.n * del_n

    def walk(self, del_u, del_z):
        """An alternative version of slide that does not allow movement on the y-axis"""
        self.slide(del_u, 0, del_z)

    def get_matrix(self):
        minusEye = Vector(-self.eye.x, -self.eye.y, -self.eye.z)
        return [self.u.x, self.u.y, self.u.z, minusEye.dot(self.u),
                self.v.x, self.v.y, self.v.z, minusEye.dot(self.v),
                self.n.x, self.n.y, self.n.z, minusEye.dot(self.n),
                0,        0,        0,        1]


class ProjectionMatrix:
    """Builds transformations concerning the camera's "lens" """

    def __init__(self):
        self.left = -1
        self.right = 1
        self.bottom = -1
        self.top = 1
        self.near = -1
        self.far = 1
        self.is_orthographic = True

    def set_orthographic(self, left, right, bottom, top, near, far):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far
        self.is_orthographic = True

    def set_perspective(self, fovy, aspect, near, far):
        self.near = near
        self.far = far
        self.top = near + tan(fovy / 2)
        self.bottom = -self.top
        self.right = self.top * aspect
        self.left = -self.right
        self.is_orthographic = False

    def get_matrix(self):
        if self.is_orthographic:
            A = 2 / (self.right - self.left)
            B = -(self.right + self.left) / (self.right - self.left)
            C = 2 / (self.top - self.bottom)
            D = -(self.top + self.bottom) / (self.top - self.bottom)
            E = 2 / (self.near - self.far)
            F = (self.near + self.far) / (self.near - self.far)

            return [A, 0, 0, B,
                    0, C, 0, D,
                    0, 0, E, F,
                    0, 0, 0, 1]
        else:
            A = (2 * self.near) / (self.right - self.left)
            B = (self.right + self.left) / (self.right - self.left)
            C = (2 * self.near) / (self.top - self.bottom)
            D = (self.top + self.bottom) / (self.top - self.bottom)
            E = -(self.far + self.near) / (self.far - self.near)
            F = -(2 * self.far * self.near) / (self.far - self.near)

            return [A, 0, B, 0,
                    0, C, D, 0,
                    0, 0, E, F,
                    0, 0, -1, 0]


### testing ###
if __name__ == "__main__":
    matrix = ModelMatrix()
    matrix.push_matrix()
    print(matrix)
    matrix.add_translation(3, 1, 2)
    matrix.push_matrix()
    print(matrix)
    matrix.add_scale(2, 3, 4)
    print(matrix)
    matrix.pop_matrix()
    print(matrix)

    matrix.add_translation(5, 5, 5)
    matrix.push_matrix()
    print(matrix)
    matrix.add_scale(3, 2, 3)
    print(matrix)
    matrix.pop_matrix()
    print(matrix)

    matrix.pop_matrix()
    print(matrix)

    matrix.push_matrix()
    matrix.add_scale(2, 2, 2)
    print(matrix)
    matrix.push_matrix()
    matrix.add_translation(3, 3, 3)
    print(matrix)
    matrix.push_matrix()
    matrix.add_rotation_y(pi / 3)
    print(matrix)
    matrix.push_matrix()
    matrix.add_translation(1, 1, 1)
    print(matrix)
    matrix.pop_matrix()
    print(matrix)
    matrix.pop_matrix()
    print(matrix)
    matrix.pop_matrix()
    print(matrix)
    matrix.pop_matrix()
    print(matrix)
