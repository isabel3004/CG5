from math import *

import pygame
from pygame.locals import *

from Shaders import *
from Matrices import *
from Base3DObjects import *
from Particles import *
import obj_3D_loading
from BezierMotion import *


class GraphicsProgram3D:

    def __init__(self):
        pygame.init() 
        pygame.display.set_mode((800,600), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("don't forget to set a caption :)")

        self.sprite_shader = SpriteShader()
        self.sprite_shader.use()

        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()
        self.view_matrix = ViewMatrix()
        self.projection_matrix = ProjectionMatrix()

        self.view_matrix.look(Point(5,5,5), Point(0, 0, 0), Vector(0,1,0))
        self.shader.set_view_matrix(self.view_matrix.get_matrix())

        self.fov = pi / 6
        self.projection_matrix.set_perspective(self.fov, 800 / 600, 0.1, 30)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        ### fog ###
        self.shader.set_start_fog(3, 0, 3)
        self.shader.set_end_fog(7, 0, 7)
        self.shader.set_fog_color(0.0, 0.0, 0.0)

        self.cube = Cube()
        self.sphere = OptimizedSphere(24, 48)
        self.car = obj_3D_loading.load_obj_file(sys.path[0] + '/models', 'carro.obj')
        self.asteroid_01 = obj_3D_loading.load_obj_file(sys.path[0] + '/models', 'asteroid_01.obj')
        self.asteroid_02 = obj_3D_loading.load_obj_file(sys.path[0] + '/models', 'asteroid_02.obj')

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.angle = 0

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

        self.translation = Vector(0, 0, 0) 
        self.angle = 0

        self.texture_id_particle = self.load_texture(sys.path[0] + '/textures/particle_purple.jpeg') 
        self.texture_id_space_02 = self.load_texture(sys.path[0] + '/textures/space.jpeg')
        self.texture_id_asteroid_01 = self.load_texture(sys.path[0] + '/textures/asteroid_01.jpg')
        self.texture_id_asteroid_02 = self.load_texture(sys.path[0] + '/textures/asteroid_02.png')

        self.sprite = Sprite()
        self.sky_sphere = SkySphere(36, 72)
        particle_effect = ParticleEffect(Point(2.0, 2.0, 2.0), self.texture_id_particle, 1.0)
        self.fire = Fire(self.sprite_shader, self.shader, particle_effect, Color(1.0, 1.0, 1.0), Color(0.6, 0.6, 0.6))

        self.fr_ticker = 0
        self.fr_sum = 0

        self.time_running = -1
        self.start_animation_time = 1.0
        self.end_animation_time = 10.0

        p = Point(self.view_matrix.eye.x, self.view_matrix.eye.y, self.view_matrix.eye.z)
        self.motion = BezierMotion(p, Point(14,-23,-18), Point(-11,7,-3), Point(3.0,3.0,3.0), self.start_animation_time, self.end_animation_time)
        self.can_move = True

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
        if self.fr_sum > 1.0:
            # print(self.fr_ticker / self.fr_sum)
            self.fr_sum = 0
            self.fr_ticker = 0
        if self.time_running == -1: # first frame
            self.time_running = 0.0
        else:
            self.time_running += delta_time
        # print(self.time_running)
        if self.time_running > self.start_animation_time and self.time_running < self.end_animation_time:
            self.can_move = False
            self.motion.get_current_position(self.time_running - self.start_animation_time, self.view_matrix.eye)
            # print(self.view_matrix.eye)
        else:
            self.can_move = True


        # self.translation += Vector(delta_time, delta_time, delta_time) * 0.2
        # self.angle += delta_time * 0.2
        
        # self.view_matrix.look_at(Point(1, 0, 3) + Point(self.angle, self.angle, self.angle), Point(0, 0, 0), Vector(0,1,0))
        # self.shader.use()
        # self.shader.set_view_matrix(self.view_matrix.get_matrix())

        self.angle += 1 * delta_time
        # if angle > 2 * pi:
        #     angle -= (2 * pi)

        self.fire.update(delta_time)

        if self.can_move:
            if self.UP_key_down: # upwards
                self.view_matrix.pitch(pi * delta_time)
            if self.DOWN_key_down: # downwards
                self.view_matrix.pitch(-pi * delta_time)
            if self.LEFT_key_down: # counterclockwise
                self.view_matrix.yaw(-pi * delta_time)
            if self.RIGHT_key_down: # clockwise
                self.view_matrix.yaw(pi * delta_time)
            if self.W_key_down: # move forward
                self.view_matrix.slide(0, 0, -4 * delta_time)
            if self.S_key_down: # move backwards
                self.view_matrix.slide(0, 0, 4 * delta_time)
            if self.A_key_down: # move left
                self.view_matrix.slide(-4 * delta_time, 0, 0)
            if self.D_key_down: # move right
                self.view_matrix.slide(4 * delta_time, 0, 0)
            if self.Q_key_down: # counterclockwise
                self.view_matrix.roll(-pi * delta_time)
            if self.E_key_down: # clockwise
                self.view_matrix.roll(pi * delta_time)
            if self.R_key_down: # move up
                self.view_matrix.slide(0, 4 * delta_time, 0)
            if self.F_key_down: # move down
                self.view_matrix.slide(0, -4 * delta_time, 0)
        
    

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
        self.sprite_shader.set_opacity(1.0)

        self.sky_sphere.draw(self.sprite_shader)
        self.model_matrix.pop_matrix()  
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glClear(GL_DEPTH_BUFFER_BIT)

        ### objects ###
        self.shader.use()

        self.shader.set_view_matrix(self.view_matrix.get_matrix()) # set view matrix every single frame

        self.shader.set_eye_position(self.view_matrix.eye)
        # self.shader.set_light_position(Point(10 * cos(self.angle), 0.0, 10 * sin(self.angle)))
        # self.shader.set_light_position(Point(5,15,5))
        # self.shader.set_light_diffuse(1.0, 1.0, 1.0)
        # self.shader.set_light_specular(0.9, 0.9, 0.9)
        self.shader.set_mat_diffuse(Color(0.9, 0.9, 0.9))
        self.shader.set_mat_specular(Color(0.3, 0.3, 0.3))
        self.shader.set_mat_shininess(4.0)

        # self.model_matrix.load_identity()

        # self.cube.set_vertices(self.shader)

        # glActiveTexture(GL_TEXTURE0)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id_space_01)
        # self.shader.set_diffuse_tex(0)
        # # glActiveTexture(GL_TEXTURE1)
        # # glBindTexture(GL_TEXTURE_2D, self.texture_id_earth_spec)
        # self.shader.set_spec_tex(0) # reset so it is not applied to cube
        
        # self.shader.set_mat_diffuse(Color(1.0, 1.0, 1.0))
        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(3.0, 0.0, -6.0)
        # self.model_matrix.add_scale(2.0, 2, 2)
        # self.model_matrix.add_rotation_y(self.angle)
        # self.model_matrix.add_rotation_z(self.angle)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # # glActiveTexture(GL_TEXTURE0)
        # # glBindTexture(GL_TEXTURE_2D, self.texture_id_earth_spec)
        # # self.shader.set_spec_tex(1)

        # # self.shader.set_mat_diffuse(1.0, 1.0, 1.0)
        # # self.model_matrix.push_matrix()
        # # self.model_matrix.add_translation(2.0, 3.0, -10.0)
        # # self.model_matrix.add_scale(2.0, 2, 2)
        # # self.model_matrix.add_rotation_y(self.angle)
        # # self.model_matrix.add_rotation_z(self.angle)
        # # self.shader.set_model_matrix(self.model_matrix.matrix)
        # # self.cube.draw(self.shader)
        # # self.model_matrix.pop_matrix()

        # glEnable(GL_CULL_FACE) # just discard some stuff that we do not see nor care abt before the fragment shader for optimization
        # glCullFace(GL_BACK) 
        # glFrontFace(GL_CW) # need this bcs of how this sphere is drawn. Use gl_front for skybox effect (only inside face rendered)

        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # glActiveTexture(GL_TEXTURE1)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id_earth_spec)
        # self.shader.set_spec_tex(1)

        self.sphere.set_vertices(self.shader)

        self.shader.set_mat_diffuse(Color(1, 1, 1), 0.5)
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(3.0, 10.0, -5.0)
        self.model_matrix.add_scale(2.0, 2.0, 2.0)
        self.model_matrix.add_rotation_x(self.angle/5)
        self.model_matrix.add_rotation_y(self.angle/5)
        self.model_matrix.add_rotation_z(self.angle /5)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.car.draw(self.shader)
        # self.sphere.draw(self.shader)
        self.model_matrix.pop_matrix()
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id_asteroid_01)
        self.shader.set_diffuse_tex(0)

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(3.0, 3.0, -3.0)
        self.model_matrix.add_scale(2.0, 2.0, 2.0)
        self.model_matrix.add_rotation_x(self.angle/5)
        self.model_matrix.add_rotation_y(self.angle/5)
        self.model_matrix.add_rotation_z(self.angle /5)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.asteroid_01.draw(self.shader)
        # self.sphere.draw(self.shader)
        self.model_matrix.pop_matrix()

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id_asteroid_02)
        self.shader.set_diffuse_tex(0)

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-3.0, 3.0, 3.0)
        self.model_matrix.add_scale(2.0, 2.0, 2.0)
        self.model_matrix.add_rotation_x(self.angle/5)
        self.model_matrix.add_rotation_y(self.angle/5)
        self.model_matrix.add_rotation_z(self.angle /5)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.asteroid_02.draw(self.shader)
        # self.sphere.draw(self.shader)
        self.model_matrix.pop_matrix()

        # glDisable(GL_CULL_FACE)
        # glDisable(GL_BLEND)

        # self.sphere.set_vertices(self.shader)

        # for i in range(8):
        #     self.model_matrix.push_matrix()
        #     self.model_matrix.add_rotation_x(self.angle * 0.74324 + i * pi / 4.0)
        #     self.model_matrix.add_translation(0, 5, 0)
        #     self.model_matrix.add_rotation_x(-(self.angle * 0.74324 + i * pi / 4.0))
        #     self.model_matrix.add_scale(3.0, 3.0, 3.0)
        #     self.shader.set_model_matrix(self.model_matrix.matrix)

        #     self.shader.set_mat_diffuse(Color(1.0, 1.0, 1.0))
        #     self.sphere.draw(self.shader)
        #     self.model_matrix.pop_matrix()

        ### sprite ###
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        # glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.sprite_shader.use()

        self.sprite_shader.set_view_matrix(self.view_matrix.get_matrix()) # set view matrix every single frame
        self.sprite_shader.set_projection_matrix(self.projection_matrix.get_matrix())

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(1.0, 1.0, 1.0)
        # self.model_matrix.add_scale(3.0, 3.0, 3.0)
        # self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
        # self.model_matrix.pop_matrix()

        # self.sprite_shader.set_alpha_tex(1)
        # glActiveTexture(GL_TEXTURE0)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id_leaf_color)
        # self.sprite_shader.set_diffuse_tex(0)
        # glActiveTexture(GL_TEXTURE1)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id_leaf_alpha)
        # self.sprite_shader.set_spec_tex(1)
        # self.sprite_shader.set_opacity(1.0)

        # self.sprite.draw(self.sprite_shader)

        # glDisable(GL_BLEND)

        self.fire.draw(self.model_matrix)

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
                    if event.key == K_UP:
                        self.UP_key_down = True
                    if event.key == K_DOWN:
                        self.DOWN_key_down = True
                    if event.key == K_LEFT:
                        self.LEFT_key_down = True
                    if event.key == K_RIGHT:
                        self.RIGHT_key_down = True
                    if event.key == K_w:
                        self.W_key_down = True
                    if event.key == K_s:
                        self.S_key_down = True
                    if event.key == K_a:
                        self.A_key_down = True
                    if event.key == K_d:
                        self.D_key_down = True
                    if event.key == K_q:
                        self.Q_key_down = True
                    if event.key == K_e:
                        self.E_key_down = True
                    if event.key == K_r:
                        self.R_key_down = True
                    if event.key == K_f:
                        self.F_key_down = True
                elif event.type == pygame.KEYUP:
                    if event.key == K_UP:
                        self.UP_key_down = False
                    if event.key == K_DOWN:
                        self.DOWN_key_down = False
                    if event.key == K_LEFT:
                        self.LEFT_key_down = False
                    if event.key == K_RIGHT:
                        self.RIGHT_key_down = False
                    if event.key == K_w:
                        self.W_key_down = False
                    if event.key == K_s:
                        self.S_key_down = False
                    if event.key == K_a:
                        self.A_key_down = False
                    if event.key == K_d:
                        self.D_key_down = False
                    if event.key == K_q:
                        self.Q_key_down = False
                    if event.key == K_e:
                        self.E_key_down = False
                    if event.key == K_r:
                        self.R_key_down = False
                    if event.key == K_f:
                        self.F_key_down = False
            self.update()
            self.display()
        pygame.quit()

    def start(self):
        self.program_loop()


if __name__ == "__main__":
    GraphicsProgram3D().start()
