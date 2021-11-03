from math import *

import pygame
from pygame.locals import *

from Shaders import *
from Matrices import *
from Base3DObjects import *
from Particles import *
import obj_3D_loading
from BezierMotion import *

import tkinter as tk
import time


class GraphicsProgram3D:

    def __init__(self):
        pygame.init() 
        pygame.display.set_mode((800,600), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("don't forget to set a caption :)")
        # initialize shaders
        self.sprite_shader = SpriteShader()
        self.sprite_shader.use()
        self.shader = Shader3D()
        self.shader.use()
        # initialize matrices
        self.model_matrix = ModelMatrix()
        self.view_matrix = ViewMatrix()
        self.projection_matrix = ProjectionMatrix()
        self.view_matrix.look(Point(5,5,5), Point(0, 5, 0), Vector(0,1,0))
        self.shader.set_view_matrix(self.view_matrix.get_matrix())
        self.fov = pi / 6
        self.projection_matrix.set_perspective(self.fov, 800 / 600, 0.1, 30)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())
        # set fog
        self.shader.set_start_fog(5, 0, 5)
        self.shader.set_end_fog(15, 0, 15)
        self.shader.set_fog_color(0.0, 0.0, 0.0)
        # initialize game objects
        self.cube = Cube()
        self.track = Track()
        self.sphere = OptimizedSphere(24, 48)
        self.car = obj_3D_loading.load_obj_file(sys.path[0] + '/models', 'carro.obj')
        self.asteroid_01 = obj_3D_loading.load_obj_file(sys.path[0] + '/models', 'asteroid_01.obj')
        self.asteroid_02 = obj_3D_loading.load_obj_file(sys.path[0] + '/models', 'asteroid_02.obj')
        # initialize controls
        self.UP_key_down = False
        self.DOWN_key_down = False
        self.LEFT_key_down = False
        self.RIGHT_key_down = False
        self.W_key_down = False
        self.A_key_down = False
        self.S_key_down = False
        self.D_key_down = False
        self.Q_key_down = False
        self.E_key_down = False
        self.R_key_down = False
        self.F_key_down = False
        self.angle = 0
        # initialize textures
        self.texture_id_particle = self.load_texture(sys.path[0] + '/textures/particle_purple.jpeg') 
        self.texture_id_space_02 = self.load_texture(sys.path[0] + '/textures/space.jpeg')
        self.texture_id_asteroid_01 = self.load_texture(sys.path[0] + '/textures/asteroid_01.jpg')
        self.texture_id_asteroid_02 = self.load_texture(sys.path[0] + '/textures/asteroid_02.png')
        self.texture_id_road = self.load_texture(sys.path[0] + "/textures/road.jpg")
        self.texture_id_port_passed = self.load_texture(sys.path[0] + "/textures/black.png")
        self.texture_id_boost = self.load_texture(sys.path[0] + "/textures/boost.png")
        self.texture_id_boost_rotated = self.load_texture(sys.path[0] + "/textures/boost_rotated.png")
        self.opacity = 1.0 # this is used for the fading effect
        # initialize sprites and particle effects
        self.sprite = Sprite()
        self.sky_sphere = SkySphere()
        particle_effect_01 = ParticleEffect(Point(5.0, 5.0, 5.0), self.texture_id_particle, 1.0)
        self.fire_01 = Fire(self.sprite_shader, self.shader, particle_effect_01, 1)
        particle_effect_02 = ParticleEffect(Point(0.0, 5.0, 0.0), self.texture_id_particle, 1.0)
        self.fire_02 = Fire(self.sprite_shader, self.shader, particle_effect_02, 2)
        particle_effect_03 = ParticleEffect(Point(5.0, 5.0, -5.0), self.texture_id_particle, 1.0)
        self.fire_03 = Fire(self.sprite_shader, self.shader, particle_effect_03, 3)
        # framerate
        self.fr_ticker = 0
        self.fr_sum = 0
        # initial animation phase
        self.time_running = -1 # means first frame - will be set to actual running time once the program is fully loaded and starts
        self.start_animation_time = 1.0
        self.end_animation_time = 11.0
        p = Point(4, 2.1, 0) # Point(self.view_matrix.eye.x, self.view_matrix.eye.y, self.view_matrix.eye.z)
        self.motion = BezierMotion(p, Point(24,-16,-11), Point(-11, 14, 10), p, self.start_animation_time, self.end_animation_time)
            # added a small delta-time to make sure we end at the right position, otherwise the motion might end slightly earlier
            # has to be larger the faster the motion is, i.e. the smaller the difference between end_time and start_time is
            # 10.0 was just picked arbitrarily after some testing
        self.end_animation_time += 10.0 / (self.end_animation_time - self.start_animation_time)
        self.can_move = False
        # variables used in the actual game
        self.speed = 0.0
        self.falling = False
        self.port11, self.port12, self.port13, self.port14 = False, False, False, False # has the port been passed yet
        self.port21, self.port22 = False, False
        self.boost = False
        self.tb = 0
        # program phases
        self.init = False # initial animation
        self.transition = False # transition phase
        self.transition_length = 3.0
        self.game = False # actual game
        self.won = False # victory screen
        # finally, ready to go
        self.init = True
        self.t0 = time.time() # game start time
        self.clock = pygame.time.Clock()
        self.clock.tick()

    def load_texture(self, path_string):
        surface = pygame.image.load(path_string)
        tex_string = pygame.image.tostring(surface, "RGBA", 1)
        width = surface.get_width()
        height = surface.get_height()
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_string)
        return tex_id

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        self.fr_sum += delta_time
        self.fr_ticker += 1
        if self.time_running == -1: # first frame
            self.time_running = 0.0
        else:
            self.time_running += delta_time
        if self.fr_sum > 1.0:
            # print(self.fr_ticker / self.fr_sum)
            self.fr_sum = 0
            self.fr_ticker = 0
        self.fire_01.update(delta_time)
        self.fire_02.update(delta_time)
        self.fire_03.update(delta_time)
        self.angle += 1 * delta_time
        # initial animation
        if self.init:
            if self.start_animation_time < self.time_running < self.end_animation_time:
                self.motion.get_current_position(self.time_running - self.start_animation_time, self.view_matrix.eye)
            elif self.time_running > self.end_animation_time:
                self.init = False
                # self.transition = True
                self.game = True
        # actual game
        elif self.game:
            self.can_move = True
            if not self.falling:
                self.previous_position = Point(self.view_matrix.eye.x, self.view_matrix.eye.y, self.view_matrix.eye.z)
            if self.can_move:
                if self.LEFT_key_down: # counterclockwise
                    self.view_matrix.yaw(-pi * delta_time)
                if self.RIGHT_key_down: # clockwise
                    self.view_matrix.yaw(pi * delta_time)
                if self.W_key_down: # move forward
                    if self.speed < 4.1:
                        self.speed += 0.05
                    self.view_matrix.slide(0, 0, -self.speed * delta_time)
                else:
                    if self.speed > 0.0:
                        self.speed -= 0.05
                        self.view_matrix.slide(0, 0, -self.speed * delta_time)
                if self.S_key_down: # move backwards
                    self.view_matrix.slide(0, 0, 4 * delta_time)

                # falling off track
                floor_x, floor_z = 20, 20
                start_x, start_z = -5, 0
                if (self.view_matrix.eye.x <= (-(start_x + floor_x)) or self.view_matrix.eye.x >= (-start_x)  or self.view_matrix.eye.z <= (-floor_z/2) or self.view_matrix.eye.z >= (floor_z/2)
                    or (-13 < self.view_matrix.eye.x < 3 and 8 > self.view_matrix.eye.z > -8) or self.view_matrix.eye.y < 2):
                    self.view_matrix.eye.y -= 0.15
                    self.falling = True
                    self.boost = False
                if self.falling and self.view_matrix.eye.y < -2:
                    self.view_matrix.eye.x = self.previous_position.x
                    self.view_matrix.eye.y = 2.1
                    self.view_matrix.eye.z = self.previous_position.z
                    self.falling = False
                
                # boost
                if (3.2 <= self.view_matrix.eye.x <= 3.8 and -5.5 <= self.view_matrix.eye.z <= -4.5) or (-1.5 <= self.view_matrix.eye.x <= 1.5 and -10 <= self.view_matrix.eye.z <= -9):
                    self.boost = True
                    self.tb = time.time()
                if self.boost:
                    if (time.time() - self.tb) < 0.8:
                        self.view_matrix.slide(0, 0, -3 * delta_time)
                    else:
                        self.boost = False

                # check if port is passed
                if -1.9>=self.view_matrix.eye.x>=-2.1 and -9.9 <=self.view_matrix.eye.z<=-9.1: # port1(2, -9.9, 1)
                    print("port11 passed")
                    self.port11 = True
                elif -5.9>=self.view_matrix.eye.x>=-6.1 and -9.2<=self.view_matrix.eye.z<=-8.4: # port1(-6, -9.2, 2)
                    print("port12 passed")
                    self.port12 = True
                elif -6.3>=self.view_matrix.eye.x>=-6.5 and -9.2<=self.view_matrix.eye.z<=-8.4: # port1(-6.4, -9.2, 3)
                    print("port13 passed")
                    self.port13 = True
                elif -6.7>=self.view_matrix.eye.x>=-6.9 and -9.2<=self.view_matrix.eye.z<=-8.4: # port1(-6.8, -9.2, 4)
                    print("port14 passed")
                    self.port14 = True
                elif 4.9>=self.view_matrix.eye.x>=4.1 and -7.1<=self.view_matrix.eye.z<=-6.9: # port2(4.9, -7, 1)
                    print("port21 passed")
                    self.port21 = True
                elif 4.2>=self.view_matrix.eye.x>=3.4 and -3.1<=self.view_matrix.eye.z<=-2.9: # port2(4.2, -3, 2)
                    print("port22 passed")
                    self.port22 = True
                
                if self.port11 and self.port12 and self.port13 and self.port14 and self.port21 and self.port22:
                    print("finished in", time.time()-self.t0)
                    print(time.time()-self.t0)
                    self.won = True
                    self.game = False
        # in this case, nothing needs to be updated
        elif self.won:
            pass
        elif self.transition:
            pass

    def display(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glViewport(0, 0, 800, 600)
        self.model_matrix.load_identity()

        ### skybox ###
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glDisable(GL_DEPTH_TEST)

        self.sprite_shader.use()
        self.sky_sphere.set_vertices(self.sprite_shader)
        self.sprite_shader.set_projection_matrix(self.projection_matrix.get_matrix())
        self.sprite_shader.set_view_matrix(self.view_matrix.get_matrix())
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(self.view_matrix.eye.x, self.view_matrix.eye.y, self.view_matrix.eye.z)
        self.sprite_shader.set_model_matrix(self.model_matrix.matrix)      
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id_space_02)
        self.sprite_shader.set_diffuse_tex(0)
        self.sprite_shader.set_alpha_tex(None)
        self.sprite_shader.set_opacity(self.opacity)

        self.sky_sphere.draw(self.sprite_shader)
        self.model_matrix.pop_matrix()  
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glClear(GL_DEPTH_BUFFER_BIT)

        ### objects ###
        self.shader.use()
        self.shader.set_view_matrix(self.view_matrix.get_matrix())
        self.shader.set_eye_position(self.view_matrix.eye)
        self.shader.set_mat_diffuse(Color(0.9, 0.9, 0.9), self.opacity)
        self.shader.set_mat_specular(Color(0.3, 0.3, 0.3), self.opacity)
        self.shader.set_mat_shininess(4.0)

        self.model_matrix.load_identity()

        def set_tex(tex):
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, tex)
            self.shader.set_diffuse_tex(0)
            # glActiveTexture(GL_TEXTURE1)
            # glBindTexture(GL_TEXTURE_2D, tex)
            self.shader.set_spec_tex(0)

        set_tex(self.texture_id_road)
        ### track ###
        self.track.set_vertices(self.shader)
        self.shader.set_mat_diffuse(Color(1.0, 1.0, 1.0), self.opacity)
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-5, 2, 0.0) 
        self.model_matrix.add_scale(20, 1, 20)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.track.draw(self.shader)
        self.model_matrix.pop_matrix()
        
        def port_passed():
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, self.texture_id_port_passed)
                self.shader.set_diffuse_tex(0)
                # glActiveTexture(GL_TEXTURE1)
                # glBindTexture(GL_TEXTURE_2D, self.texture_id_port_passed)
                # self.shader.set_spec_tex(0)

        self.cube.set_vertices(self.shader)
        h, t = 1.51, 0.05 # height course and thickness of port
        p_w, p_h = 0.8, 1.4 # port width and height

        def port1(px, py, nr):  
            if nr == 1 and self.port11: 
                set_tex(self.texture_id_port_passed)
            elif nr == 2 and self.port12: 
                set_tex(self.texture_id_port_passed)
            elif nr == 3 and self.port13:
                set_tex(self.texture_id_port_passed)
            elif nr == 4 and self.port14:
                set_tex(self.texture_id_port_passed)
            else:
                set_tex(self.texture_id_road)
            self.model_matrix.push_matrix()     
            self.model_matrix.add_translation(px, h + (p_h/2), py)   
            self.model_matrix.add_scale(t, p_h, t)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()
            self.model_matrix.push_matrix()     
            self.model_matrix.add_translation(px, h + (p_h/2), py + p_w)   
            self.model_matrix.add_scale(t, p_h, t)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()
            self.model_matrix.push_matrix()     
            self.model_matrix.add_translation(px, h + p_h, py + (p_w/2))   
            self.model_matrix.add_scale(t, t, p_w + t)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()
        
        def port2(px, py, nr):
            if nr == 1 and self.port21: 
                set_tex(self.texture_id_port_passed)
            elif nr == 2 and self.port22:
                set_tex(self.texture_id_port_passed)
            else:
                set_tex(self.texture_id_road)
            self.model_matrix.push_matrix()     
            self.model_matrix.add_translation(px, h + (p_h/2), py)   
            self.model_matrix.add_scale(t, p_h, t)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()
            self.model_matrix.push_matrix()     
            self.model_matrix.add_translation(px - p_w, h + (p_h/2), py)   
            self.model_matrix.add_scale(t, p_h, t)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()
            self.model_matrix.push_matrix()     
            self.model_matrix.add_translation(px - (p_w/2), h + p_h, py)   
            self.model_matrix.add_scale(p_w + t, t, t)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()

        port2(4.9, -7, 1)
        port2(4.2, -3, 2)
        port1(2, -9.9, 1)
        port1(-6, -9.2, 2)
        port1(-6.4, -9.2, 3)
        port1(-6.8, -9.2, 4)
        
        set_tex(self.texture_id_boost)

        self.model_matrix.push_matrix()     
        self.model_matrix.add_translation(3.5, 1.52, -5)   
        self.model_matrix.add_scale(1, 0.01, 0.6)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        set_tex(self.texture_id_boost_rotated)

        self.model_matrix.push_matrix()     
        self.model_matrix.add_translation(0, 1.52, -9.5)   
        self.model_matrix.add_scale(3, 0.01, 1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        # don't draw the car when playing the game
        if self.init or self.won:
            self.sphere.set_vertices(self.shader)

            self.shader.set_mat_diffuse(Color(1, 1, 1), self.opacity)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(4.0, 2.3, 0.0)
            self.model_matrix.add_scale(0.35, 0.35, 0.35)
            # self.model_matrix.add_rotation_x(self.angle / 3.0)
            # self.model_matrix.add_rotation_y(self.angle / 3.0)
            # self.model_matrix.add_rotation_z(self.angle / 3.0)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.car.draw(self.shader)
            self.model_matrix.pop_matrix()
        
        ### asteroids ###
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id_asteroid_01)
        self.shader.set_diffuse_tex(0)

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-5.0, 8, -12.0)
        self.model_matrix.add_scale(3.0, 3.0, 3.0)
        self.model_matrix.add_rotation_x(self.angle/3.0)
        self.model_matrix.add_rotation_y(self.angle/3.0)
        self.model_matrix.add_rotation_z(self.angle /3.0)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.asteroid_01.draw(self.shader)
        self.model_matrix.pop_matrix()

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id_asteroid_02)
        self.shader.set_diffuse_tex(0)

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-5, 2.5, 1.0)
        self.model_matrix.add_scale(3.5, 3.5, 3.5)
        self.model_matrix.add_rotation_x(self.angle/3.0)
        self.model_matrix.add_rotation_y(self.angle/3.0)
        self.model_matrix.add_rotation_z(self.angle/3.0)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.asteroid_02.draw(self.shader)
        self.model_matrix.pop_matrix()

        ### fires ###
        self.sprite_shader.use()
        self.sprite_shader.set_view_matrix(self.view_matrix.get_matrix())
        self.sprite_shader.set_projection_matrix(self.projection_matrix.get_matrix())
        self.fire_01.draw(self.model_matrix)
        self.fire_02.draw(self.model_matrix)
        self.fire_03.draw(self.model_matrix)

        pygame.display.flip()

    def program_loop(self):
        exiting = False
        while not exiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True
                    if event.key == K_LEFT:
                        self.LEFT_key_down = True
                    if event.key == K_RIGHT:
                        self.RIGHT_key_down = True
                    if event.key == K_w:
                        self.W_key_down = True
                    if event.key == K_s:
                        self.S_key_down = True
                elif event.type == pygame.KEYUP:
                    if event.key == K_LEFT:
                        self.LEFT_key_down = False
                    if event.key == K_RIGHT:
                        self.RIGHT_key_down = False
                    if event.key == K_w:
                        self.W_key_down = False
                    if event.key == K_s:
                        self.S_key_down = False
            self.update()
            self.display()
        pygame.quit()

    def start(self):
        self.program_loop()


if __name__ == "__main__":
    GraphicsProgram3D().start()
