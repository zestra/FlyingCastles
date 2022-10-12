from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *

from gameobjects.matrix44 import Matrix44
from gameobjects.vector3 import Vector3

from math import radians
import random


SCREEN_SIZE = (1100, 600)


def add_tuples(tuples):
    x, y, z = 0, 0, 0

    for tuple in tuples:
        x += tuple[0]
        y += tuple[1]
        z += tuple[2]

    return tuple(x, y, z)


def resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(width)/height, .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    glEnable(GL_DEPTH_TEST)

    glShadeModel(GL_FLAT)
    glClearColor(0.537, 0.784, 0.953, 0.0)

    glEnable(GL_COLOR_MATERIAL)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLight(GL_LIGHT0, GL_POSITION, (0, 1, 1, 0))



class Pure3dObject:

    # The object is pure because it is constructed from vertices,
    # and not a compound objects composed of other 3d pure or compound objects.

    def __init__(self, vertices, position, normals, colour):

        self.vertices = vertices
        self.position = position
        self.normals = normals
        self.colour = colour

    def render(self):
        glColor(self.colour)

        vertices = []
        for face in self.vertices:
            vertices.append([])
            for vertex in face:
                vertices[len(vertices) - 1].append(tuple(Vector3(vertex) + self.position))

        face_index = 0
        for face in vertices:

            glBegin(GL_POLYGON)

            glNormal3dv(self.normals[face_index][0])


            for vertex in face:
                glVertex(vertex)

            face_index += 1

            glEnd()


class Hexaprism(Pure3dObject):

    def __init__(self, position, width, height, colour):

        self.position = position
        self.colour = colour

        self.vertices = [  # grouped by faces
            [(-2*width, 0, -width), (-width, 0, 0), (0, 0, 0), (width, 0, -width), (0, 0, -2*width), (-width, 0, -2*width), (-2*width, 0, -width)],  # bottom
            [(-2*width, height, -width), (-width, height, 0), (0, height, 0), (width, height, -width), (0, height, -2*width), (-width, height, -2*width), (-2*width, height, -width)],  # top
            [(-2*width, 0, -width), (-width, 0, 0), (-width, height, 0), (-2*width, height, -width)],  # * rest below are rectangles
            [(-width, 0, 0), (-width, height, 0), (0, height, 0), (0, 0, 0)],
            [(0, 0, 0), (0, height, 0), (width, height, -width), (width, 0, -width)],
            [(width, 0, -width), (width, height, -width), (0, height, -2*width), (0, 0, -2*width)],
            [(0, 0, -2*width), (0, height, -2*width), (-width, height, -2*width), (-width, 0, -2*width)],
            [(-width, 0, -2*width), (-width, height, -2*width), (-2*width, height, -width), (-2*width, 0, -width)]
        ]

        self.normals = [  # reflection of light per face
            [(0, 0, -1)],
            [(0, 0, +1)],
            [(-1, -1, 0)],
            [(0, -1, 0)],
            [(+1, -1, 0)],
            [(+1, +1, 0)],
            [(0, +1, 0)],
            [(+1, +1, 0)],
        ]


class Pyramid(Pure3dObject):

    def __init__(self, position, colour):

        self.position = position
        self.colour = colour

        self.vertices = [  # grouped by faces
            [(1, 0, 0), (0, 0, 0), (0, 1, 0)],  # bottom
            [(1, 0, 0), (0, 0, 1), (0, 0, 0)],  # left
            [(0, 0, 0), (0, 0, 1), (0, 1, 0)],  # right
            [(1, 0, 0), (0, 0, 1), (0, 1, 0)]   # top
        ]

        self.normals = [  # reflection of light per face
            [(+1, +1, +1)],   # bottom
            [(+1, 0, 0)],     # left
            [(0, -1, 0)],     # right
            [(0, 0, -1)]      # top
        ]


class Cube(Pure3dObject):

    def __init__(self, position, colour):

        self.position = position
        self.colour = colour

        self.vertices = [  # grouped by faces
            [(1, 0, 0), (1, 0, 1), (0, 0, 1), (0, 0, 0)],
            [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)],
            [(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)],
            [(1, 1, 0), (1, 0, 0), (1, 0, 1), (1, 1, 1)],
            [(0, 1, 1), (0, 0, 1), (1, 0, 1), (1, 1, 1)],
            [(1, 1, 0), (1, 1, 1), (0, 1, 1), (0, 1, 0)]
        ]

        self.normals = [  # reflection of light per face
            [(0, +1, 0)],
            [(-1, -1, 0)],
            [(0, -1, -1)],
            [(+1, 0, 0)],
            [(0, 0, +1)],
            [(0, -1, 0)]
        ]


class Map(object):

    def __init__(self):

        map_surface = pygame.image.load(picture)
        map_surface.lock()

        w, h = map_surface.get_size()

        self.shapes = []

        for y in range(h):
            for x in range(w):

                r, g, b, a = map_surface.get_at((x, y))

                if (r, g, b) != (0, 0, 0):

                    gl_col = (r/255.0, g/255.0, b/255.0)  # Draw Hexagonal Buildings
                    position = (float(x), 0.0, float(y))
                    hexaprism = Hexaprism(position, 1, int(int(b)/2), gl_col)
                    self.shapes.append(hexaprism)

                else:
                    position = (float(x), 1.0, float(y))  # Draw Pyramid-like Grass
                    pyramid = Pyramid( position, (0, 1, 0))
                    self.shapes.append(pyramid)

                position = (float(x), 0.0, float(y))  # Draw Cubic Ground
                cube = Cube(position, (0, 1, 0))
                self.shapes.append(cube)
                position = (float(x), -1.0, float(y))
                cube = Cube(position, (0, 1, 0))
                self.shapes.append(cube)


        map_surface.unlock()

        self.display_list = None

    def render(self):

        if self.display_list is None:

            self.display_list = glGenLists(1)
            glNewList(self.display_list, GL_COMPILE)

            for cube in self.shapes:
                cube.render()

            glEndList()

        else:

            glCallList(self.display_list)


def run():
    pygame.init()
    window = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE|OPENGL|DOUBLEBUF)

    resize(*SCREEN_SIZE)
    init()

    clock = pygame.time.Clock()

    map = Map()

    camera_matrix = Matrix44()
    camera_matrix.translate = (20, 10, -5)

    rotation_direction = Vector3()
    rotation_speed = radians(90.0)
    movement_direction = Vector3()
    movement_speed = 5.0

    while True:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == KEYUP and event.key == K_ESCAPE:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        time_passed = clock.tick()
        seconds_passed = time_passed / 1000.

        keys_pressed = pygame.key.get_pressed()

        rotation_direction.set(0.0, 0.0, 0.0)
        movement_direction.set(0.0, 0.0, 0.0)

        if keys_pressed[K_LEFT]:
            rotation_direction.y = +1.0
        elif keys_pressed[K_RIGHT]:
            rotation_direction.y = -1.0
        if keys_pressed[K_UP]:
            rotation_direction.x = -1.0
        elif keys_pressed[K_DOWN]:
            rotation_direction.x = +1.0
        if keys_pressed[K_z]:
            rotation_direction.z = -1.0
        elif keys_pressed[K_x]:
            rotation_direction.z = +1.0
        if keys_pressed[K_q]:
            movement_direction.z = -1.0
            movement_speed += 0.025
        elif keys_pressed[K_a]:
            movement_direction.z = +1.0
            movement_speed += 0.025
        else:
            movement_speed = 5.0

        rotation = rotation_direction * rotation_speed * seconds_passed
        rotation_matrix = Matrix44.xyz_rotation(*rotation)
        camera_matrix *= rotation_matrix

        heading = Vector3(camera_matrix.forward)
        movement = heading * movement_direction.z * movement_speed
        camera_matrix.translate += movement * seconds_passed

        glLoadMatrixd(camera_matrix.get_inverse().to_opengl())

        glLight(GL_LIGHT3, GL_POSITION, (0, 0, 0, 0))

        map.render()

        pygame.display.flip()


if __name__ == "__main__":
    picture = "pic3.png"
    run()