import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math

from shapes import *

pygame.init()
display = (1280, 720)
screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
glEnable(GL_BLEND)

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glShadeModel(GL_SMOOTH)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])

glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
gluLookAt(0, -8, 0, 0, 0, 0, 0, 0, 1)
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
glLoadIdentity()

# SHAPE INFO

vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

plane_vertices = (
    (-10,-10,-2),
    (10,-10,-2),
    (10,10,-2),
    (-10,10,-2),
    )

surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
    )

# END SHAPE INFO

# init mouse movement and center mouse on screen
displayCenter = [screen.get_size()[i] // 2 for i in range(2)]
pygame.mouse.set_pos(displayCenter)
mouseMove = [0, 0]

up_down_angle = 0.0
paused = False
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                run = False
            if event.key == pygame.K_PAUSE or event.key == pygame.K_p:
                paused = not paused
                pygame.mouse.set_pos(displayCenter)
        # if not paused:
        #     if event.type == pygame.MOUSEMOTION:
        #         mouseMove = [event.pos[i] - mouseMove[i] for i in range(2)]

    if not paused:
        # get keys
        keypress = pygame.key.get_pressed()
        mouseMove = pygame.mouse.get_rel()
        mousepress = pygame.mouse.get_pressed()


        # init model view matrix
        glLoadIdentity()

        if mousepress[0]:
        # apply the look up and down
            up_down_angle += mouseMove[1]*0.15
            glRotatef(up_down_angle, 1.0, 0.0, 0.0)
        else:
            glRotatef(up_down_angle, 1.0, 0.0, 0.0)

        # init the view matrix
        glPushMatrix()
        glLoadIdentity()

        if mousepress[0]:
            # apply the left and right rotation
            glRotatef(mouseMove[0]*0.15, 0.0, 1.0, 0.0)

        mods = pygame.key.get_mods()
        # apply the movment
        if keypress[pygame.K_w]:
            glTranslatef(0,0,0.1)
        if keypress[pygame.K_s]:
            glTranslatef(0,0,-0.1)
        if keypress[pygame.K_d]:
            glTranslatef(-0.1,0,0)
        if keypress[pygame.K_a]:
            glTranslatef(0.1,0,0)
        if keypress[pygame.K_SPACE]:
            if mods & pygame.KMOD_SHIFT:
                glTranslatef(0, 0.1, 0)
            else:
                glTranslatef(0, -0.1, 0)

        # multiply the current matrix by the get the new view matrix and store the final vie matrix
        glMultMatrixf(viewMatrix)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

        # apply view matrix
        glPopMatrix()
        glMultMatrixf(viewMatrix)

        glLightfv(GL_LIGHT0, GL_POSITION, [1, -1, 1, 0])

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glPushMatrix()

        plane1 = Plane(plane_vertices)
        plane1.draw_plane()

        cube1 = Cube(vertices, surfaces)
        cube1.draw_cube()

        sphere1 = Sphere(1.0, 128, 128)
        glTranslatef(-3, 0, 0)
        sphere1.draw_sphere()

        sphere2 = Sphere(1.0, 128, 128)
        glTranslatef(6, 0, 0)
        sphere2.draw_sphere()

        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

pygame.quit()
