import pygame
from OpenGL.GL import *


class World:
    def __init__(self, size_x, size_y, size_z):
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        self.blocks = [
            [
                [
                    1 if y == 1 else 2 if y == 0 else 0  # Земля на уровне 0, камень на уровне 1
                    for z in range(size_z)
                ]
                for y in range(size_y)
            ]
            for x in range(size_x)
        ]

        self.textures = self.load_textures()

    @staticmethod
    def load_textures():
        # Загружаем текстуры
        textures = {}
        textures['dirt'] = World.load_texture("textures/dirt.png")
        textures['stone'] = World.load_texture("textures/stone.png")
        return textures

    @staticmethod
    def load_texture(path):
        # Загружаем изображение с помощью Pygame
        texture_surface = pygame.image.load(path)
        texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
        width, height = texture_surface.get_size()

        # Генерируем текстуру в OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        return texture_id

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        for x in range(self.size_x):
            for y in range(self.size_y):
                for z in range(self.size_z):
                    if self.blocks[x][y][z] != 0:  # Если блок не "воздух"
                        block_type = self.blocks[x][y][z]
                        texture_id = self.textures['dirt'] if block_type == 1 else self.textures['stone']
                    
                        # Проверяем и рисуем только видимые грани
                        if y + 1 >= self.size_y or self.blocks[x][y + 1][z] == 0:  # Верхняя грань
                            self.draw_face(x, y, z, texture_id, "top")
                        if y - 1 < 0 or self.blocks[x][y - 1][z] == 0:  # Нижняя грань
                            self.draw_face(x, y, z, texture_id, "bottom")
                        if z + 1 >= self.size_z or self.blocks[x][y][z + 1] == 0:  # Передняя грань
                            self.draw_face(x, y, z, texture_id, "front")
                        if z - 1 < 0 or self.blocks[x][y][z - 1] == 0:  # Задняя грань
                            self.draw_face(x, y, z, texture_id, "back")
                        if x - 1 < 0 or self.blocks[x - 1][y][z] == 0:  # Левая грань
                            self.draw_face(x, y, z, texture_id, "left")
                        if x + 1 >= self.size_x or self.blocks[x + 1][y][z] == 0:  # Правая грань
                            self.draw_face(x, y, z, texture_id, "right")
        glDisable(GL_TEXTURE_2D)


    @staticmethod
    def draw_face(x, y, z, texture_id, face):
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glBegin(GL_QUADS)

        if face == "top":  # Верхняя грань
            glTexCoord2f(0, 0)
            glVertex3f(x, y + 1, z)
            glTexCoord2f(1, 0)
            glVertex3f(x + 1, y + 1, z)
            glTexCoord2f(1, 1)
            glVertex3f(x + 1, y + 1, z + 1)
            glTexCoord2f(0, 1)
            glVertex3f(x, y + 1, z + 1)
        elif face == "bottom":  # Нижняя грань
            glTexCoord2f(0, 0)
            glVertex3f(x, y, z)
            glTexCoord2f(1, 0)
            glVertex3f(x + 1, y, z)
            glTexCoord2f(1, 1)
            glVertex3f(x + 1, y, z + 1)
            glTexCoord2f(0, 1)
            glVertex3f(x, y, z + 1)
        elif face == "front":  # Передняя грань
            glTexCoord2f(0, 0)
            glVertex3f(x, y, z + 1)
            glTexCoord2f(1, 0)
            glVertex3f(x + 1, y, z + 1)
            glTexCoord2f(1, 1)
            glVertex3f(x + 1, y + 1, z + 1)
            glTexCoord2f(0, 1)
            glVertex3f(x, y + 1, z + 1)
        elif face == "back":  # Задняя грань
            glTexCoord2f(0, 0)
            glVertex3f(x, y, z)
            glTexCoord2f(1, 0)
            glVertex3f(x + 1, y, z)
            glTexCoord2f(1, 1)
            glVertex3f(x + 1, y + 1, z)
            glTexCoord2f(0, 1)
            glVertex3f(x, y + 1, z)
        elif face == "left":  # Левая грань
            glTexCoord2f(0, 0)
            glVertex3f(x, y, z)
            glTexCoord2f(1, 0)
            glVertex3f(x, y, z + 1)
            glTexCoord2f(1, 1)
            glVertex3f(x, y + 1, z + 1)
            glTexCoord2f(0, 1)
            glVertex3f(x, y + 1, z)
        elif face == "right":  # Правая грань
            glTexCoord2f(0, 0)
            glVertex3f(x + 1, y, z)
            glTexCoord2f(1, 0)
            glVertex3f(x + 1, y, z + 1)
            glTexCoord2f(1, 1)
            glVertex3f(x + 1, y + 1, z + 1)
            glTexCoord2f(0, 1)
            glVertex3f(x + 1, y + 1, z)

        glEnd()
