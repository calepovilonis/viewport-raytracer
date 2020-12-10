import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import matplotlib.pyplot as plt
import math

from shapes import *
from matrixmath import *

# ray tracing algorithm reference from https://medium.com/swlh/ray-tracing-from-scratch-in-python-41670e6a96f9

pygame.init()
w = 852
h = 480
display = (w, h)

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
light = np.array([7.,-5.,4.5])
light_color = np.array([1.,1.,1.])
light_ambient = np.array([1.,1.,1.])
light_specular = np.array([1.,1.,1.])

max_depth = 3
col = np.zeros(3)
image = np.zeros((h, w, 3))

ratio = float(w) / h
screen_project = (-1, 1 / ratio, 1, -1 / ratio)

glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
gluLookAt(0, -8, 0, 0, 0, 0, 0, 0, 1)
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
glLoadIdentity()

camera = np.array([0, 0, 0])
camera_test = np.array([0., -6., 0.0])
pixel_screen = [0.0, -5., 0.0]
camera_rotation = [0, 0, 0]
#camera_lookat = np.array([0.0,0.0,0.0])

ambient_color = np.array([.05,.05,.05])

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
    (-1000,-1000,-2),
    (1000,-1000,-2),
    (1000,1000,-2),
    (-1000,1000,-2),
    )

surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
    )

gameobjects = []
# END SHAPE INFO

# begin ray tracing functions
def normalize(v):
    return v / np.linalg.norm(v)

def reflected(v, axis):
    return v - 2 * np.dot(v, axis) * axis

def nearest_intersected_object(objects, ray_origin, ray_direction):
    distances = [obj.intersect(obj.rtposition,ray_origin, ray_direction) for obj in objects]
    nearest_object = None
    min_distance = np.inf
    for index, distance in enumerate(distances):
        if distance and distance < min_distance:
            min_distance = distance
            nearest_object = objects[index]
    return nearest_object, min_distance

# end ray tracing functions

# init mouse movement and center mouse on screen
displayCenter = [screen.get_size()[i] // 2 for i in range(2)]
pygame.mouse.set_pos(displayCenter)
mouseMove = [0, 0]

up_down_angle = 0.0
left_right_angle = 0.0
paused = False
run = True

picked = 0
placed = False
rotate = False
move = False

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                run = False
            # if event.key == pygame.K_PAUSE or event.key == pygame.K_p:
            #     paused = not paused
            #     pygame.mouse.set_pos(displayCenter)
            if event.key == pygame.K_PLUS:
                print("plus")
        if event.type == pygame.MOUSEBUTTONDOWN:
            # middle mouse button
            if event.button == 2:
                gameobjects[picked].isselected = False
            # up scroll
            if event.button == 4:
                if (len(gameobjects) == 0):
                    continue
                if (len(gameobjects) == 1):
                    picked = 0
                    gameobjects[picked].isselected = True
                else:
                    prev = picked
                    if picked == len(gameobjects)-1:
                        picked = 0
                    else:
                        picked+=1
                    gameobjects[picked].isselected = True
                    gameobjects[prev].isselected = False
            # down scroll
            elif event.button == 5:
                if (len(gameobjects) == 0):
                    continue
                if (len(gameobjects) == 1):
                    picked = 0
                    gameobjects[picked].isselected = True
                else:
                    prev = picked
                    if picked == 0:
                        picked = len(gameobjects)-1
                    else:
                        picked-=1
                    gameobjects[picked].isselected = True
                    gameobjects[prev].isselected = False

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
            camera_rotation = [camera_rotation[0]+up_down_angle, camera_rotation[1], camera_rotation[2]]
        else:
            glRotatef(up_down_angle, 1.0, 0.0, 0.0)

        # init the view matrix
        glPushMatrix()
        glLoadIdentity()

        if mousepress[0]:
            left_right_angle = mouseMove[0]*0.15
            # apply the left and right rotation
            glRotatef(left_right_angle, 0.0, 1.0, 0.0)
            camera_rotation = [camera_rotation[0], camera_rotation[1]+left_right_angle, camera_rotation[2]]

        #print(camera)

        mods = pygame.key.get_mods()

        selected = None
        for obj in gameobjects:
            if obj.isselected == True:
                selected = obj
                break


        # apply the movment
        if keypress[pygame.K_r]:
            print("Rendering to image...")
            for i, y in enumerate(np.linspace(screen_project[1], screen_project[3], h)):
                for j, x in enumerate(np.linspace(screen_project[0], screen_project[2], w)):
                    pixel = np.array([x+pixel_screen[0], pixel_screen[1], y+pixel_screen[2]])
                    origin = camera_test

                    direction = normalize(pixel - origin)

                    color = np.zeros((3))
                    reflection = 1.

                    for k in range(max_depth):
                        # check for intersections
                        nearest_object, min_distance = nearest_intersected_object(gameobjects, origin, direction)
                        if nearest_object is None:
                            continue

                        # compute intersection point between ray and nearest object
                        intersection = origin + min_distance * direction

                        normal_to_surface = normalize(intersection - nearest_object.rtposition)
                        shifted_point = intersection + 1e-5 * normal_to_surface
                        intersection_to_light = normalize(light - shifted_point)

                        _, min_distance = nearest_intersected_object(gameobjects, shifted_point, intersection_to_light)
                        intersection_to_light_distance = np.linalg.norm(light - intersection)
                        is_shadowed = min_distance < intersection_to_light_distance

                        #print(min_distance, type(nearest_object), intersection, shifted_point, intersection_to_light_distance)

                        if is_shadowed:
                            continue

                        # RGB
                        illumination = np.zeros((3))

                        # ambient
                        illumination += nearest_object.ambient * light_ambient

                        # diffuse
                        illumination += nearest_object.color * light_color * np.dot(intersection_to_light, normal_to_surface)

                        # specular
                        intersection_to_camera = normalize(camera_test - intersection)
                        H = normalize(intersection_to_light + intersection_to_camera)
                        illumination += nearest_object.specular * light_specular * np.dot(normal_to_surface, H) ** (nearest_object.shininess / 4)

                        # reflection
                        color += reflection * illumination
                        reflection *= nearest_object.reflection

                        origin = shifted_point
                        direction = reflected(direction, normal_to_surface)

                    image[i, j] = np.clip(color, 0, 1)

                print("progress: %d/%d" % (i + 1, h))
            plt.imsave("render.png", image)
            print("Image saved to directory.")

        if keypress[pygame.K_w]:
            glTranslatef(0,0,0.1)
            camera[1] = camera[1]+.03
            pixel_screen[1] = pixel_screen[1]+.03
        if keypress[pygame.K_s]:
            glTranslatef(0,0,-0.1)
            camera[1] = camera[1]-.03
            pixel_screen[1] = pixel_screen[1]-.03
        if keypress[pygame.K_d]:
            glTranslatef(-0.1,0,0)
            camera[0] = camera[0]+.03
            pixel_screen[0] = pixel_screen[0]+.03
        if keypress[pygame.K_a]:
            glTranslatef(0.1,0,0)
            camera[0] = camera[0]-.03
            pixel_screen[0] = pixel_screen[0]-.03
        if keypress[pygame.K_SPACE]:
            if mods & pygame.KMOD_SHIFT:
                glTranslatef(0, 0.1, 0)
                camera[2] = camera[2]+.03
                pixel_screen[2] = pixel_screen[2]+.03
            else:
                glTranslatef(0, -0.1, 0)
                camera[2] = camera[2]-.03
                pixel_screen[2] = pixel_screen[2]-.03

        vm = glGetFloatv(GL_MODELVIEW_MATRIX)
        invert = InverseMat44(vm)
        camera = [camera[0]+invert[12], camera[1]+invert[13], camera[2]+invert[14]]

        if keypress[pygame.K_l]:
            try:
                lx = float(input("Light x position: "))
                ly = float(input("Light y position: "))
                lz = float(input("Light z position: "))

                light[0] = lx
                light[1] = ly
                light[2] = lz
            except:
                continue
        if keypress[pygame.K_p]:
            if placed == False:
                plane = Plane(plane_vertices, [.5,.5,.5], 0.00, 0)
                plane.position = np.array([0.0, 0.0, 0.0])
                for obj in gameobjects:
                    if obj.isselected == True:
                        obj.isselected = False
                plane.isselected = True
                gameobjects.append(plane)
                picked = len(gameobjects)-1
                placed = True
        elif keypress[pygame.K_c]:
            if placed == False:
                cube = Cube(vertices, surfaces, [.5,.5,.5], 0.25, 75)
                cube.position = np.array([0.,0.,0.])
                for obj in gameobjects:
                    if obj.isselected == True:
                        obj.isselected = False
                cube.isselected = True
                picked = len(gameobjects)-1
                gameobjects.append(cube)
                placed = True
        elif keypress[pygame.K_o]:
            if placed == False:
                sphere = Sphere(1.0, 128, 128, [.5,.5,.5], 0.5, 100)
                sphere.position = np.array([0.0, 0, 0.0])
                for obj in gameobjects:
                    if obj.isselected == True:
                        obj.isselected = False
                sphere.isselected = True
                picked = len(gameobjects)-1
                gameobjects.append(sphere)
                placed = True
        else:
            placed = False
        if selected is not None:
            if keypress[pygame.K_n]:
                r = input("Material Red value (0-1): ")
                g = input("Material Green value (0-1): ")
                b = input("Material Blue value (0-1): ")
                reflect = input("Material Reflection value (0-1): ")
                s = input("Material Shininess value (0-100): ")

                selected.color[0] = float(r)
                selected.color[1] = float(g)
                selected.color[2] = float(b)
                selected.reflection = float(reflect)
                selected.shininess = float(s)

            if keypress[pygame.K_m]:
                move = True
                rotate = False
            if keypress[pygame.K_COMMA]:
                move = False
                rotate = True
            if keypress[pygame.K_BACKSPACE]:
                selected.isselected = False
                if picked == len(gameobjects)-1:
                    picked-=1
                gameobjects.remove(selected)
            if keypress[pygame.K_UP]:
                if move:
                    if mods & pygame.KMOD_SHIFT:
                        selected.move(0, 0, .1)
                    else:
                        selected.move(0, .1, 0)
                if rotate:
                    selected.rotate_x(-.5)
            if keypress[pygame.K_DOWN]:
                if move:
                    if mods & pygame.KMOD_SHIFT:
                        selected.move(0, 0, -.1)
                    else:
                        selected.move(0, -.1, 0)
                if rotate:
                        selected.rotate_x(.5)
            if keypress[pygame.K_LEFT]:
                if move:
                    selected.move(-.1, 0, 0)
                if rotate:
                    selected.rotate_y(-.5)
            if keypress[pygame.K_RIGHT]:
                if move:
                    selected.move(.1, 0, 0)
                if rotate:
                    selected.rotate_y(.5)
            if keypress[pygame.K_KP_PLUS] or keypress[pygame.K_RIGHTBRACKET]:
                selected.scale(.05)
            if keypress[pygame.K_KP_MINUS] or keypress[pygame.K_LEFTBRACKET]:
                selected.scale(-.05)

        # multiply the current matrix by the get the new view matrix and store the final vie matrix
        glMultMatrixf(viewMatrix)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

        # apply view matrix
        glPopMatrix()
        glMultMatrixf(viewMatrix)

        glLightfv(GL_LIGHT0, GL_POSITION, [1, -1, 1, 0])

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glPushMatrix()

        for obj in gameobjects:
            obj.draw()

        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

pygame.quit()
