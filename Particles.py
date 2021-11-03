from random import *

from Base3DObjects import *
from Shaders import *


class Particle:
    def __init__(self, position, motion):
        self.pos = position # relative
        self.dir = motion
        self.time_lived = 0.0


class ParticleEffect:
    def __init__(self, position, texture, opacity, rate = 10, time_to_live = 2.0, fade_time = 0.3):
        self.texture = texture
        self.position = position
        self.sprite = Sprite()
        self.particles = []
        self.time_since_particle = 0.0 # time since creation
        self.rate = rate
        self.time_to_live = time_to_live
        self.opacity = opacity
        self.fade_time = fade_time

    def update(self, delta_time):
        particles_to_kill = []
        for particle in self.particles:
            particle.time_lived += delta_time
            if particle.time_lived > self.time_to_live:
                particles_to_kill.append(particle)
            particle.pos += particle.dir * delta_time
        for particle in particles_to_kill:
            self.particles.remove(particle)
        self.time_since_particle += delta_time
        time_per_particle = 1.0 / self.rate
        while self.time_since_particle > time_per_particle:
            self.time_since_particle -= time_per_particle
            self.particles.append(Particle(Point(self.position.x, self.position.y, self.position.z), 
                                Vector(random() - 0.5, random(), 0.0) * 0.5))

    def draw(self, sprite_shader, model_matrix, op = 0.0, use_op = False):
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE) # to make black basically transparent
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        sprite_shader.set_diffuse_tex(0)
        sprite_shader.set_alpha_tex(None)

        model_matrix.push_matrix()
        model_matrix.add_translation(self.position.x, self.position.y, self.position.z)

        for particle in self.particles:
            if particle.time_lived < self.fade_time:
                opacity = (particle.time_lived / self.fade_time) * self.opacity
            elif particle.time_lived > (self.time_to_live - self.fade_time):
                opacity = (1.0 - (particle.time_lived - (self.time_to_live - self.fade_time)) 
                                / (self.fade_time) * self.opacity)
            else:
                opacity = self.opacity   
            if use_op:
                opacity = op 
            sprite_shader.set_opacity(opacity)
            model_matrix.push_matrix()
            model_matrix.add_translation(particle.pos.x, particle.pos.y, particle.pos.z)
            model_matrix.add_scale(1.0, 1.0, 1.0)
            model_matrix.add_rotation_y((random() - 0.5) * pi / 25.0)
            sprite_shader.set_model_matrix(model_matrix.matrix)
            self.sprite.draw(sprite_shader)
            model_matrix.pop_matrix()

        model_matrix.pop_matrix()
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)


class Fire:
    """Encapsulates a fire particle effect with a strong light source centered in it"""
    def __init__(self, sprite_shader: SpriteShader, shader: Shader3D, particle_effect: ParticleEffect, fire_id):
        self.sprite_shader = sprite_shader
        self.shader = shader
        self.particle_effect = particle_effect
        if fire_id in {1, 2, 3}:
            if fire_id == 1:
                self.shader.set_fire_01_position(Point(self.particle_effect.position.x, self.particle_effect.position.y, self.particle_effect.position.z))
            elif fire_id == 2:
                self.shader.set_fire_02_position(Point(self.particle_effect.position.x, self.particle_effect.position.y, self.particle_effect.position.z))
            elif fire_id == 3:
                self.shader.set_fire_03_position(Point(self.particle_effect.position.x, self.particle_effect.position.y, self.particle_effect.position.z))
            self.shader.set_light_diffuse(0.7, 0.4, 0.7)
            self.shader.set_light_specular(0.5, 0.2, 0.5)

    def update(self, delta_time):
        self.particle_effect.update(delta_time)
    
    def draw(self, model_matrix, op = 0.0, use_op = False):
        self.sprite_shader.use()
        self.particle_effect.draw(self.sprite_shader, model_matrix, op, use_op)
        
    