import pygame
from OpenGL.GL import *
import numpy as np
import settings

class World:
    def __init__(self, size_x, size_y, size_z):
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        
        # Используем NumPy для более эффективного хранения блоков
        self.blocks = np.zeros((size_x, size_y, size_z), dtype=np.uint8)
        
        # Инициализация земли и камня
        self.blocks[:, 0, :] = 2  # Камень на уровне 0
        self.blocks[:, 1, :] = 1  # Земля на уровне 1
        
        self.textures = self.load_textures()
        # Создаем display list для кэширования отрисовки
        self.display_list = None
        self.needs_update = True

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
    
    def update_chunk(self, x=None, y=None, z=None):
        """Отметить мир или его часть как требующую обновления"""
        self.needs_update = True
        
    def draw(self):
        # Используем display list для кэширования геометрии
        if self.needs_update or self.display_list is None:
            if self.display_list is None:
                self.display_list = glGenLists(1)
            
            glNewList(self.display_list, GL_COMPILE)
            self._render_world()
            glEndList()
            self.needs_update = False
        
        # Отрисовываем кэшированную геометрию
        glCallList(self.display_list)
    
    def _render_world(self):
        """Внутренний метод для рендеринга мира"""
        glEnable(GL_TEXTURE_2D)
        
        # Используем NumPy для быстрого поиска непустых блоков
        x_coords, y_coords, z_coords = np.where(self.blocks > 0)
        
        for i in range(len(x_coords)):
            x, y, z = x_coords[i], y_coords[i], z_coords[i]
            block_type = self.blocks[x, y, z]
            texture_id = self.textures['dirt'] if block_type == 1 else self.textures['stone']
            
            # Проверяем и рисуем только видимые грани
            # Верхняя грань
            if y + 1 >= self.size_y or self.blocks[x, y + 1, z] == 0:
                self.draw_face(x, y, z, texture_id, "top")
            # Нижняя грань
            if y - 1 < 0 or self.blocks[x, y - 1, z] == 0:
                self.draw_face(x, y, z, texture_id, "bottom")
            # Передняя грань
            if z + 1 >= self.size_z or self.blocks[x, y, z + 1] == 0:
                self.draw_face(x, y, z, texture_id, "front")
            # Задняя грань
            if z - 1 < 0 or self.blocks[x, y, z - 1] == 0:
                self.draw_face(x, y, z, texture_id, "back")
            # Левая грань
            if x - 1 < 0 or self.blocks[x - 1, y, z] == 0:
                self.draw_face(x, y, z, texture_id, "left")
            # Правая грань
            if x + 1 >= self.size_x or self.blocks[x + 1, y, z] == 0:
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
        
    def set_block(self, x, y, z, block_type):
        """Установить блок определенного типа в указанной позиции"""
        if 0 <= x < self.size_x and 0 <= y < self.size_y and 0 <= z < self.size_z:
            # Если блок не меняется, ничего не делаем
            if self.blocks[x, y, z] == block_type:
                return True
            
            # Устанавливаем новый тип блока
            self.blocks[x, y, z] = block_type
        
            # Отмечаем, что мир нуждается в обновлении
            self.needs_update = True
        
            # Выводим отладочную информацию
            if hasattr(settings, 'DEBUG_MODE') and settings.DEBUG_MODE:
                print(f"Блок установлен: ({x}, {y}, {z}) -> {block_type}")
            
            return True
        return False
    def get_block(self, x, y, z):
        """Получить тип блока в указанной позиции"""
        if 0 <= x < self.size_x and 0 <= y < self.size_y and 0 <= z < self.size_z:
            return self.blocks[x, y, z]
        return None