from OpenGL.GL import *
import math
import settings
import pygame
import numpy as np

class Player:
    def __init__(self):
        # Позиция игрока
        self.position = np.array([5 * settings.WORLD_SIZE, 3, 5 * settings.WORLD_SIZE], dtype=np.float32)
        self.pitch, self.yaw = 0, 0  # Углы камеры
        self.speed = settings.PLAYER_SPEED
        self.sprint_speed = settings.SPRINT_SPEED
        self.fly_speed = settings.FLY_SPEED
        self.mouse_sensitivity = settings.MOUSE_SENSITIVITY
        self.gravity = settings.GRAVITY if hasattr(settings, 'GRAVITY') else 0.01
        self.jump_strength = settings.JUMP_STRENGTH if hasattr(settings, 'JUMP_STRENGTH') else 0.2
        self.velocity_y = 0
        self.is_flying = True  # Режим полета
        self.is_on_ground = False
        
        # Увеличиваем размеры игрока
        self.height = 1.8  # Высота игрока (почти 2 блока)
        self.width = 0.6   # Ширина игрока
        self.eye_height = 1.6  # Высота глаз от земли
        
        # Уменьшаем отступ для коллизий, чтобы игрок мог проходить в узкие места
        self.collision_padding = 0.2
        
        self.prev_f_pressed = False  # Для переключения режима полета
        self.selected_block = 2  # По умолчанию выбран камень (2)
        self.interaction_distance = 5.0  # Максимальное расстояние для взаимодействия с блоками

    @property
    def x(self):
        return self.position[0]
        
    @x.setter
    def x(self, value):
        self.position[0] = value
        
    @property
    def y(self):
        return self.position[1]
        
    @y.setter
    def y(self, value):
        self.position[1] = value
        
    @property
    def z(self):
        return self.position[2]
        
    @z.setter
    def z(self, value):
        self.position[2] = value

    def update_camera(self):
        # Применяем повороты камеры
        glRotatef(self.pitch, 1, 0, 0)  # Поворот по оси X
        glRotatef(self.yaw, 0, 1, 0)    # Поворот по оси Y
        
        # Сдвигаем сцену, чтобы камера была на уровне глаз игрока
        # Вычитаем высоту глаз из позиции Y
        glTranslatef(-self.x, -(self.y + self.eye_height), -self.z)

    def handle_mouse(self, dx, dy):
        # Исправляем инверсию по горизонтали - убираем минус перед dx
        self.yaw += dx * self.mouse_sensitivity  # Теперь движение мыши вправо поворачивает камеру вправо
        self.pitch += dy * self.mouse_sensitivity  # Оставляем инверсию по вертикали
        self.pitch = max(-89, min(89, self.pitch))  # Ограничение по вертикали

    def handle_keys(self, keys, world=None):
        # Вычисляем направление движения
        sin_yaw = math.sin(math.radians(self.yaw))
        cos_yaw = math.cos(math.radians(self.yaw))
        
        # Определяем скорость в зависимости от спринта
        current_speed = self.sprint_speed if keys[pygame.K_LCTRL] else self.speed
        
        # Вектор движения
        move_vector = np.zeros(3, dtype=np.float32)
        
        if keys[pygame.K_w]:  # Вперёд
            move_vector[0] += sin_yaw
            move_vector[2] -= cos_yaw
        if keys[pygame.K_s]:  # Назад
            move_vector[0] -= sin_yaw
            move_vector[2] += cos_yaw
        if keys[pygame.K_a]:  # Влево
            move_vector[0] -= cos_yaw
            move_vector[2] -= sin_yaw
        if keys[pygame.K_d]:  # Вправо
            move_vector[0] += cos_yaw
            move_vector[2] += sin_yaw
            
        # Нормализуем вектор движения, если он не нулевой
        length = np.linalg.norm(move_vector)
        if length > 0:
            move_vector /= length
            move_vector *= current_speed
        
        # Применяем движение по горизонтали
        new_position = self.position.copy()
        new_position[0] += move_vector[0]
        new_position[2] += move_vector[2]
        
        # Проверка коллизий с миром (если мир передан)
        if world is not None:
            # Проверяем коллизии только если не в режиме полета
            if not self.is_flying:
                # Проверка коллизий по X
                if self.check_collision(new_position[0], self.y, self.z, world):
                    new_position[0] = self.x
                
                # Проверка коллизий по Z
                if self.check_collision(new_position[0], self.y, new_position[2], world):
                    new_position[2] = self.z
        
        # Применяем новую позицию
        self.position[0] = new_position[0]
        self.position[2] = new_position[2]
        
        # Обработка вертикального движения
        if self.is_flying:
            # В режиме полета
            if keys[pygame.K_SPACE]:  # Вверх
                self.position[1] += self.fly_speed
            if keys[pygame.K_LSHIFT]:  # Вниз
                self.position[1] -= self.fly_speed
        else:
            # В режиме ходьбы с гравитацией
            # Проверяем, стоим ли мы на земле
            self.is_on_ground = self.check_ground(world)
            
            if self.is_on_ground:
                self.velocity_y = 0
                if keys[pygame.K_SPACE]:  # Прыжок
                    self.velocity_y = self.jump_strength
            else:
                # Применяем гравитацию
                self.velocity_y -= self.gravity
            
            # Применяем вертикальную скорость
            new_y = self.y + self.velocity_y
            
            # Проверка коллизий по Y
            if world is not None and self.check_collision(self.x, new_y, self.z, world):
                if self.velocity_y < 0:  # Если падаем вниз
                    self.is_on_ground = True
                self.velocity_y = 0
            else:
                self.position[1] = new_y
        
        # Переключение режима полета
        if keys[pygame.K_f] and not self.prev_f_pressed:
            self.is_flying = not self.is_flying
        self.prev_f_pressed = keys[pygame.K_f]

        # Обработка клавиши R для сброса позиции
        if keys[pygame.K_r]:
            self.reset_position()
            
        # Выбор блока (1-9)
        for i in range(1, 10):
            if keys[getattr(pygame, f'K_{i}')]:
                self.selected_block = i

    def check_collision(self, x, y, z, world):
        """Проверка коллизий с блоками мира с учетом размеров игрока"""
        # Получаем координаты блоков, которые занимает игрок
        min_x, max_x = int(x - self.width/2), int(x + self.width/2)
        min_y, max_y = int(y), int(y + self.height)
        min_z, max_z = int(z - self.width/2), int(z + self.width/2)
        
        # Проверяем все блоки, которые могут пересекаться с игроком
        for check_x in range(min_x, max_x + 1):
            for check_y in range(min_y, max_y + 1):
                for check_z in range(min_z, max_z + 1):
                    # Проверяем, что координаты в пределах мира
                    if (0 <= check_x < world.size_x and 
                        0 <= check_y < world.size_y and 
                        0 <= check_z < world.size_z):
                        
                        # Если блок не воздух
                        if world.blocks[check_x, check_y, check_z] != 0:
                            # Проверяем коллизию с этим блоком
                            # Центр блока
                            block_center_x = check_x + 0.5
                            block_center_y = check_y + 0.5
                            block_center_z = check_z + 0.5
                            
                            # Расстояние от центра игрока до центра блока
                            dx = abs(x - block_center_x)
                            dy = abs((y + self.height/2) - block_center_y)
                            dz = abs(z - block_center_z)
                            
                            # Сумма половин размеров
                            sum_half_width_x = (self.width/2 + 0.5)
                            sum_half_height = (self.height/2 + 0.5)
                            sum_half_width_z = (self.width/2 + 0.5)
                            
                            # Если расстояние меньше суммы половин размеров, то есть коллизия
                            if (dx < sum_half_width_x and
                                dy < sum_half_height and
                                dz < sum_half_width_z):
                                return True
        return False

    def check_ground(self, world):
        """Проверка, стоит ли игрок на земле"""
        # Проверяем блоки прямо под ногами игрока
        feet_y = int(self.y - 0.1)  # Немного ниже позиции ног
        
        # Проверяем несколько точек под игроком для более надежного определения
        check_points = [
            (self.x, self.z),  # Центр
            (self.x - self.width/2, self.z),  # Левый край
            (self.x + self.width/2, self.z),  # Правый край
            (self.x, self.z - self.width/2),  # Передний край
            (self.x, self.z + self.width/2)   # Задний край
        ]
        
        for point_x, point_z in check_points:
            block_x, block_z = int(point_x), int(point_z)
            
            if (0 <= block_x < world.size_x and 
                0 <= feet_y < world.size_y and 
                0 <= block_z < world.size_z):
                
                if world.blocks[block_x, feet_y, block_z] != 0:
                    return True
        
        return False

    def reset_position(self):
        """Сбросить позицию игрока в центр карты"""
        self.position = np.array([5 * settings.WORLD_SIZE, 3, 5 * settings.WORLD_SIZE], dtype=np.float32)
        self.pitch, self.yaw = 0, 0  # Сбрасываем углы камеры
        self.velocity_y = 0  # Сбрасываем вертикальную скорость
        if settings.DEBUG_MODE:
            print("Позиция игрока сброшена в центр карты.")
        
    def raycast(self, world):
        """Определение блока, на который смотрит игрок"""
        # Начальная позиция луча - позиция глаз игрока
        ray_pos = self.position.copy()
        ray_pos[1] += self.eye_height  # Добавляем высоту глаз
        
        # Направление луча - направление взгляда игрока
        ray_dir = np.array([
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            -math.sin(math.radians(self.pitch)),
            -math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ], dtype=np.float32)
        
        # Нормализуем направление
        ray_dir /= np.linalg.norm(ray_dir)
        
        # Шаг для луча (уменьшаем для большей точности)
        step = 0.01
        
        # Максимальное расстояние для проверки
        max_distance = self.interaction_distance
        
        # Проходим по лучу с шагом step
        for i in range(int(max_distance / step)):
            # Текущая позиция на луче
            current_pos = ray_pos + ray_dir * step * i
            
            # Координаты блока
            block_x, block_y, block_z = int(current_pos[0]), int(current_pos[1]), int(current_pos[2])
            
            # Проверяем, что координаты в пределах мира
            if (0 <= block_x < world.size_x and 
                0 <= block_y < world.size_y and 
                0 <= block_z < world.size_z):
                
                # Если блок не воздух, возвращаем его координаты и предыдущую позицию
                if world.blocks[block_x, block_y, block_z] != 0:
                    # Вычисляем предыдущую позицию для размещения блока
                    prev_pos = ray_pos + ray_dir * step * (i - 1)
                    prev_block_x, prev_block_y, prev_block_z = int(prev_pos[0]), int(prev_pos[1]), int(prev_pos[2])
                    
                    # Проверяем, что предыдущая позиция в пределах мира
                    if (0 <= prev_block_x < world.size_x and 
                        0 <= prev_block_y < world.size_y and 
                        0 <= prev_block_z < world.size_z):
                        
                        return (block_x, block_y, block_z), (prev_block_x, prev_block_y, prev_block_z)
        
        return None, None
