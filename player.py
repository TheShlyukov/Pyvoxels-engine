from OpenGL.GL import *
import math
import settings  # Импорт настроек
import pygame

class Player:
    def __init__(self):
        self.x, self.y, self.z = 5 * settings.WORLD_SIZE, 3, 5 * settings.WORLD_SIZE  # Позиция игрока
        self.pitch, self.yaw = 0, 0  # Углы камеры
        self.speed = settings.PLAYER_SPEED  # Скорость движения
        self.sprint_speed = settings.SPRINT_SPEED # скорость спринта
        self.fly_speed = settings.FLY_SPEED  # Скорость полёта
        self.mouse_sensitivity = settings.MOUSE_SENSITIVITY  # Чувствительность мыши

    def update_camera(self):
        # Применяем повороты камеры
        glRotatef(self.pitch, 1, 0, 0)  # Поворот по оси X
        glRotatef(self.yaw, 0, 1, 0)    # Поворот по оси Y
        # Сдвигаем сцену, чтобы камера была в позиции игрока
        glTranslatef(-self.x, -self.y, -self.z)

    def handle_mouse(self, dx, dy):
        self.yaw += dx * self.mouse_sensitivity
        self.pitch += dy * self.mouse_sensitivity
        self.pitch = max(-90, min(90, self.pitch))  # Ограничение по вертикали

    def handle_keys(self, keys):
        # Движение вперёд/назад/влево/вправо с учётом угла камеры
        sin_yaw = math.sin(math.radians(self.yaw))
        cos_yaw = math.cos(math.radians(self.yaw))

        if keys[pygame.K_w]:  # Вперёд
            if keys[pygame.K_LCTRL]:
                self.x += self.sprint_speed * sin_yaw
                self.z -= self.sprint_speed * cos_yaw
            else:
                self.x += self.speed * sin_yaw
                self.z -= self.speed * cos_yaw 
        if keys[pygame.K_s]:  # Назад
            self.x -= self.speed * sin_yaw
            self.z += self.speed * cos_yaw
        if keys[pygame.K_a]:  # Влево
            self.x -= self.speed * cos_yaw
            self.z -= self.speed * sin_yaw
        if keys[pygame.K_d]:  # Вправо
            self.x += self.speed * cos_yaw
            self.z += self.speed * sin_yaw

        # Полёт вверх/вниз
        if keys[pygame.K_SPACE]:  # Вверх
            self.y += self.fly_speed
        if keys[pygame.K_LSHIFT]:  # Вниз
            self.y -= self.fly_speed
