import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

class Plane:
    def __init__(plane, vertices, color, reflection, shininess):
        plane.vertices = vertices
        plane.isselected = False
        plane.position = np.array([0,0,0])
        plane.rotation_x = 0
        plane.rotation_y = 0
        plane.color = color
        plane.reflection = reflection
        plane.normal = np.array([0.0,0.0,1.0])
        plane.ambient = np.array([plane.color[0]/5,plane.color[1]/5,plane.color[2]/5])
        plane.specular = np.array([1.,1.,1.])
        plane.shininess = shininess
        plane.rtposition = [plane.position[0], plane.position[1], plane.position[2]-2.0]

    def draw(plane):
        glTranslatef(plane.position[0], plane.position[1], plane.position[2])
        glRotated(plane.rotation_x,1,0,0)
        glRotated(plane.rotation_y,0,1,0)
        glBegin(GL_QUADS)
        for vertex in plane.vertices:
            if plane.isselected:
                glColor4f(1, 1, 1, 1)
            else:
                glColor4f(plane.color[0], plane.color[1], plane.color[0], 1)
            glVertex3fv(vertex)
        glEnd()
        glTranslatef(-plane.position[0], -plane.position[1], -plane.position[2])


    def move(plane, x, y, z):
        plane.position = np.array([plane.position[0] + x, plane.position[1] + y, plane.position[2] + z])
        plane.rtposition =  [plane.position[0], plane.position[1], plane.position[2]-2.0]

    def scale(plane, value):
        plane.vertices = (
            (plane.vertices[0][0]-value, plane.vertices[0][1]-value, plane.vertices[0][2]),
            (plane.vertices[1][0]+value, plane.vertices[1][1]-value, plane.vertices[1][2]),
            (plane.vertices[2][0]+value, plane.vertices[2][1]+value, plane.vertices[2][2]),
            (plane.vertices[3][0]-value, plane.vertices[3][1]+value, plane.vertices[3][2]),
            )

    def rotate_x(plane, a):
        plane.rotation_x += a

    def rotate_y(plane, a):
        plane.rotation_y += a

    def intersect(plane, P, O, D):
        N = plane.normal
        denom = np.dot(N,D)
        if np.abs(denom) < 0.0001:
            return None
        d_new = np.dot(P-O,N) / denom
        if d_new < 0.0001:
            return None
        return d_new

class Cube:
    def __init__(cube, vertices, surfaces, color, reflection, shininess):
        cube.vertices = vertices
        cube.surfaces = surfaces
        cube.isselected = False
        cube.position = np.array([0,0,0])
        cube.rotation_x = 0
        cube.rotation_y = 0
        cube.color = color
        cube.reflection = reflection
        cube.normal = np.array([0.0,0.0,1.0])
        cube.ambient = np.array([cube.color[0]/5,cube.color[1]/5,cube.color[2]/5])
        cube.specular = np.array([1.,1.,1.])
        cube.shininess = shininess
        cube.rtposition = [cube.position[0], cube.position[1], cube.position[2]]
        cube.scaleof = 1.

    def draw(cube):
        glTranslatef(cube.position[0], cube.position[1], cube.position[2])
        glPushMatrix()
        glRotated(cube.rotation_x,1,0,0)
        glRotated(cube.rotation_y,0,1,0)
        glBegin(GL_QUADS)
        for surface in cube.surfaces:
            for vertex in surface:
                color = cube.color
                if cube.isselected:
                    color = (1.,1.,1.)
                glColor3fv(color)
                glVertex3f(
                cube.vertices[vertex][0],
                cube.vertices[vertex][1],
                cube.vertices[vertex][2]
                )
        glEnd()
        glPopMatrix()
        glTranslatef(-cube.position[0], -cube.position[1], -cube.position[2])

    def move(cube, x, y, z):
        cube.position = [cube.position[0] + x, cube.position[1] + y, cube.position[2] + z]
        cube.rtposition = cube.position
        # print(cube.rtposition)

    def scale(cube, value):
        cube.vertices = (
            (cube.vertices[0][0]+value, cube.vertices[0][1]-value, cube.vertices[0][2]-value),
            (cube.vertices[1][0]+value, cube.vertices[1][1]+value, cube.vertices[1][2]-value),
            (cube.vertices[2][0]-value, cube.vertices[2][1]+value, cube.vertices[2][2]-value),
            (cube.vertices[3][0]-value, cube.vertices[3][1]-value, cube.vertices[3][2]-value),
            (cube.vertices[4][0]+value, cube.vertices[4][1]-value, cube.vertices[4][2]+value),
            (cube.vertices[5][0]+value, cube.vertices[5][1]+value, cube.vertices[5][2]+value),
            (cube.vertices[6][0]-value, cube.vertices[6][1]-value, cube.vertices[6][2]+value),
            (cube.vertices[7][0]-value, cube.vertices[7][1]+value, cube.vertices[7][2]+value)
            )

        cube.scaleof += value

    def rotate_x(cube, a):
        cube.rotation_x += a

    def rotate_y(cube, a):
        cube.rotation_y += a

    def intersect(cube, P, O, D):
        min = [cube.rtposition[0]+cube.scaleof, cube.rtposition[1]-cube.scaleof, cube.rtposition[2]-cube.scaleof]
        max = [cube.rtposition[0]-cube.scaleof, cube.rtposition[1]+cube.scaleof, cube.rtposition[2]+cube.scaleof]

        tmin = (min[0] - O[0]) / D[0]
        tmax = (max[0] - O[0]) / D[0]

        if (tmin > tmax):
            tmp = tmin
            tmin = tmax
            tmax = tmp

        tymin = (min[1] - O[1]) / D[1]
        tymax = (max[1] - O[1]) / D[1]

        if (tymin > tymax):
            tmp = tymin
            tymin = tymax
            tymax = tmp

        if ((tmin > tymax) or (tymin > tmax)):
            return None

        if (tymin > tmin):
            tmin = tymin
        if (tymax < tmax):
            tmax = tymax

        tzmin = (min[2] - O[2]) / D[2]
        tzmax = (max[2] - O[2]) / D[2]

        if (tzmin > tzmax):
            tmp = tzmin
            tzmin = tzmax
            tzmax = tmp

        if ((tmin > tzmax) or (tzmin > tmax)):
            return None

        if (tzmin > tmin):
            tmin = tzmin
        if (tzmax < tmax):
            tmax = tzmax

        if (.01 <= tmin < tmax):
            return tmin
        elif (0.01 <= tymin < tmin and 0.01 <= tymin < tzmin):
            return tymin
        elif (0.01 <= tzmin < tmin and 0.01 <= tzmin < tymin):
            return tzmin
        else:
            return None

class Sphere:
    def __init__(sphere, radius, slices, stacks, color, reflection, shininess):
        sphere.radius = np.array(radius)
        sphere.slices = slices
        sphere.stacks = stacks
        sphere.isselected = False
        sphere.position = np.array([0,0,0])
        sphere.rotation_x = 0
        sphere.rotation_y = 0
        sphere.color = color
        sphere.reflection = reflection
        sphere.ambient = np.array([sphere.color[0]/5,sphere.color[1]/5,sphere.color[2]/5])
        sphere.specular = np.array([1.,1.,1.])
        sphere.shininess = shininess
        sphere.rtposition = sphere.position

    def draw(sphere):
        glTranslatef(sphere.position[0], sphere.position[1], sphere.position[2])
        if sphere.isselected:
            glColor4f(1, 1, 1, 1)
        else:
            glColor4f(sphere.color[0], sphere.color[1], sphere.color[2], 1)
        newSphere = gluNewQuadric()
        gluSphere(newSphere, sphere.radius, sphere.slices, sphere.stacks)
        glTranslatef(-sphere.position[0], -sphere.position[1], -sphere.position[2])

    def move(sphere, x, y, z):
        sphere.position = np.array([sphere.position[0] + x, sphere.position[1] + y, sphere.position[2] + z])
        sphere.rtposition = sphere.position
        #print(sphere.position)

    def scale(sphere, value):
        sphere.radius += value

    def rotate_x(sphere, a):
        sphere.rotation_x += a

    def rotate_y(sphere, a):
        sphere.rotation_y += a

    def intersect(sphere, center, ray_origin, ray_direction):
        radius = sphere.radius
        b = 2 * np.dot(ray_direction, ray_origin - center)
        c = np.linalg.norm(ray_origin - center) ** 2 - radius ** 2
        delta = b ** 2 - 4 * c
        if delta > 0:
            t1 = (-b + np.sqrt(delta)) / 2
            t2 = (-b - np.sqrt(delta)) / 2
            if t1 > 0 and t2 > 0:
                return min(t1, t2)
        return None
