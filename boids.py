import math
import random
import pygame
import numpy as np


def add_vectors(vector1, vector2):
    """ Returns the sum of two vectors vectors are of the form (angle, magnitude)
    """
    angle1, length1 = vector1
    angle2, length2 = vector2

    x = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y = math.cos(angle1) * length1 + math.cos(angle2) * length2

    angle = 0.5 * math.pi - math.atan2(y, x)
    length = math.hypot(x, y)
    return (angle, length)


def collide(p1, p2):
    """ Tests whether two particles overlap. If they do, make them bounce
    """

    dx = p1.x - p2.x
    dy = p1.y - p2.y

    dist = math.hypot(dx, dy)
    if dist < p1.size + p2.size:
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        total_mass = p1.mass + p2.mass

        (p1.angle, p1.speed) = add_vectors((p1.angle, p1.speed*(p1.mass-p2.mass)/total_mass), (angle, 2*p2.speed*p2.mass/total_mass))
        (p2.angle, p2.speed) = add_vectors((p2.angle, p2.speed*(p2.mass-p1.mass)/total_mass), (angle+math.pi, 2*p1.speed*p1.mass/total_mass))

        overlap = 0.5*(p1.size + p2.size - dist+1)
        p1.x += math.sin(angle)*overlap
        p1.y -= math.cos(angle)*overlap
        p2.x -= math.sin(angle)*overlap
        p2.y += math.cos(angle)*overlap

def get_distance(particle1, particle2):
    del_x = particle1.x - particle2.x
    del_y = particle1.y - particle2.y
    hyp = math.hypot(del_x, del_y)
    return hyp

def get_angle_vector(particle1, particle2):
    del_x = particle1.x - particle2.x
    del_y = particle1.y - particle2.y
    hyp = math.hypot(del_x, del_y)
    angle = math.atan2(del_x, del_y)*180/math.pi
    return (angle, 1)


def get_opposite_angle_vector(particle1, particle2):
    del_x = particle1.x - particle2.x
    del_y = particle1.y - particle2.y
    hyp = math.hypot(del_x, del_y)
    angle = math.atan2(del_x, del_y)*180/math.pi
    return (-angle, 1)


class Boid(object):
    """Class to represent a Boid in the Environment
    """
    def __init__(self, environment, x, y, speed, angle, awareness, separation):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.awareness = awareness
        self.environment = environment
        self.separation = separation

        self.colour = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        self.mass = 1
        self.size = 1
        self.thickness = 0

    def move(self):
        """Update position based on speed and angle
        """
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def seek_flock_center(self):
        x, y = self.find_centroid()
        self.seek(x, y)

    def seek(self, x, y):
        """Change angle and speed to move towards a given point
        """
        dx = x - self.x
        dy = y - self.y
        self.angle = 0.5 * math.pi + math.atan2(dy, dx)
        self.speed = math.hypot(dx, dy) * 0.01

    def avoid(self, boids):
        """Move away from boids
        """
        vector = self.angle, self.speed
        for boid in boids:
            distance = get_distance(self, boid)
            if distance < self.separation:
                self.angle, self.speed = add_vectors(vector, get_angle_vector(boid, self))

    def match_speed(self, boids):
        speeds = [boid.speed for boid in boids]
        speed = np.mean(speeds)
        self.speed += speed/float(8)

    def find_centroid_angle(self, boids):
        angles = [boid.angle for boid in boids]
        angle = np.mean(angles)
        return angle

    def find_centroid(self):
        particle_coordinates_x = []
        particle_coordinates_y = []
        for particle in self.environment.boids:
            particle_coordinates_x.append(particle.x)
            particle_coordinates_y.append(particle.y)
        new_x = np.mean(particle_coordinates_x)
        new_y = np.mean(particle_coordinates_y)
        return (new_x, new_y)

    def get_neighbors(self):
        neighbors = []
        for boid in self.environment.boids:
            if math.hypot(self.x - boid.x, self.y - boid.y) < self.awareness:
                neighbors.append(boid)
        return neighbors

    def realign(self):
        neighbors = self.get_neighbors()
        if not neighbors:
            self.angle, self.speed = self.angle, self.speed
            return
        neighbor_centroid_angle = self.find_centroid_angle(neighbors)
        ave = (neighbor_centroid_angle + self.angle)/float(2)
        self.angle += ave

    def regroup(self, centroid):
        x, y = centroid
        self.seek(x, y)



class Environment:
    """ Defines the boundary of a simulation and its properties """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.boids = []

        self.colour = (0, 0, 0)
        self.mass_of_air = 0.0
        self.elasticity = 1
        self.acceleration = None
        self.centroid = None

    def add_boid(self, environment, x, y, speed, angle, awareness, separation):
        """ Add boids to the Environment"""
        boid = Boid(environment, x, y, speed, angle, awareness, separation)
        self.boids.append(boid)

    def update(self):
        """  Moves particles and tests for collisions with walls others """
        for i, boid in enumerate(self.boids):
            boid.move()
            boid.seek_flock_center()
            boid.avoid(self.boids)
            boid.realign()
            self.bounce(boid)
            for boid2 in self.boids[i+1:]:
                collide(boid, boid2)

    def bounce(self, particle):
        """ Tests whether a particle has hit the environment boundary"""

        if particle.x > self.width - particle.size:
            particle.x = 2*(self.width - particle.size) - particle.x
            particle.angle = - particle.angle

        elif particle.x < particle.size:
            particle.x = 2*particle.size - particle.x
            particle.angle = - particle.angle

        if particle.y > self.height - particle.size:
            particle.y = 2*(self.height - particle.size) - particle.y
            particle.angle = math.pi - particle.angle

        elif particle.y < particle.size:
            particle.y = 2*particle.size - particle.y
            particle.angle = math.pi - particle.angle

    def findParticle(self, x, y):
        """ Returns any particle that occupies position x, y """

        for particle in self.particles:
            if math.hypot(particle.x - x, particle.y - y) <= particle.size:
                return particle
        return None