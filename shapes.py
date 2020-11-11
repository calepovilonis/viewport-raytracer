import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math

class Plane:
    def __init__(plane, vertices):
        plane.vertices = vertices

    def draw_plane(plane):
        glBegin(GL_QUADS)
        for vertex in plane.vertices:
            glColor4f(0.5, 0.5, 0.5, 1)
            glVertex3fv(vertex)
        glEnd()

class Cube:
    def __init__(cube, vertices, surfaces):
        cube.vertices = vertices
        cube.surfaces = surfaces

    def draw_cube(cube):
        glBegin(GL_QUADS)
        for surface in cube.surfaces:
            for vertex in surface:
                color = (0, .5, 0)
                glColor3fv(color)
                glVertex3f(
                cube.vertices[vertex][0],
                cube.vertices[vertex][1],
                cube.vertices[vertex][2]
                )
        glEnd()

class Sphere:
    def __init__(sphere, radius, slices, stacks):
        sphere.radius = radius
        sphere.slices = slices
        sphere.stacks = stacks

    def draw_sphere(sphere):
        glColor4f(0.5, 0.2, 0.2, .5)
        newSphere = gluNewQuadric()
        gluSphere(newSphere, sphere.radius, sphere.slices, sphere.stacks)
