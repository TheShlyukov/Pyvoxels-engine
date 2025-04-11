from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from player import Player
from world import World
import settings
import time

class Game:
    def __init__(self):
        # Инициализация Pygame и OpenGL
        pygame.init()
        pygame.display.set_caption("Pyvoxels Engine Alpha 0.0.2")
        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), 
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        
        # Настройка OpenGL
        self.setup_opengl()
        
        # Создаём игрока и мир
        self.player = Player()
        self.world = World(10 * settings.WORLD_SIZE, 15, 10 * settings.WORLD_SIZE)
        
        # Настройка игры
        self.running = True
        self.clock = pygame.time.Clock()
        self.fps_font = pygame.font.SysFont("Arial", 18)
        self.fps_surface = None
        self.last_time = time.time()
        self.frame_count = 0
        self.fps_display = 0
        
        # Захват мыши
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
    
    def setup_opengl(self):
        """Настройка OpenGL"""
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.4, 0.8, 1, 1)  # Голубой цвет фона (небо)
        
        # Настройка проекции
        glMatrixMode(GL_PROJECTION)
        gluPerspective(70, (settings.WINDOW_WIDTH / settings.WINDOW_HEIGHT), 0.1, 100)
        glMatrixMode(GL_MODELVIEW)
        
        # Настройка освещения
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 10.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Левая кнопка мыши - разрушение блока
                if event.button == 1:
                    target_block, _ = self.player.raycast(self.world)
                    if target_block:
                        # Выводим отладочную информацию
                        if settings.DEBUG_MODE:
                            print(f"Разрушаем блок: {target_block}")
                        self.world.set_block(target_block[0], target_block[1], target_block[2], 0)  # 0 - воздух
            
                # Правая кнопка мыши - размещение блока
                elif event.button == 3:
                    target_block, place_pos = self.player.raycast(self.world)
                    if target_block and place_pos:
                        # Выводим отладочную информацию
                        if settings.DEBUG_MODE:
                            print(f"Размещаем блок: {place_pos}, рядом с: {target_block}")
                        
                        # Проверяем, что игрок не находится в этом блоке
                        player_min_x = int(self.player.x - self.player.width/2)
                        player_max_x = int(self.player.x + self.player.width/2)
                        player_min_y = int(self.player.y)
                        player_max_y = int(self.player.y + self.player.height)
                        player_min_z = int(self.player.z - self.player.width/2)
                        player_max_z = int(self.player.z + self.player.width/2)
                        
                        # Проверяем, не пересекается ли новый блок с игроком
                        if not (player_min_x <= place_pos[0] <= player_max_x and
                                player_min_y <= place_pos[1] <= player_max_y and
                                player_min_z <= place_pos[2] <= player_max_z):
                            # Размещаем выбранный блок
                            self.world.set_block(place_pos[0], place_pos[1], place_pos[2], self.player.selected_block)
    
    def update(self):
        """Обновление игровой логики"""
        # Работа с мышью
        dx, dy = pygame.mouse.get_rel()
        self.player.handle_mouse(dx, dy)
        
        # Работа с клавишами
        keys = pygame.key.get_pressed()
        self.player.handle_keys(keys, self.world)
        
        # Обновление FPS счетчика
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            self.fps_display = self.frame_count
            self.frame_count = 0
            self.last_time = current_time
    
    def render(self):
        """Отрисовка сцены"""
        # Очистка буферов
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Обновление камеры
        self.player.update_camera()
        
        # Обновление позиции света
        light_position = [10.0, 10.0, 20.0 * settings.WORLD_SIZE, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        
        # Отрисовка мира
        self.world.draw()
        
        # Отрисовка выделения блока, на который смотрит игрок
        if settings.DEBUG_MODE:
            self.draw_block_highlight()
        
        # Отрисовка прицела
        self.draw_crosshair()
        
        # Отображение FPS если включено
        if settings.SHOW_FPS:
            self.draw_fps()
        
        # Отображение информации о выбранном блоке
        self.draw_selected_block_info()
        
        # Обновление экрана
        pygame.display.flip()

    def draw_block_highlight(self):
        """Отрисовка выделения блока, на который смотрит игрок"""
        target_block, place_pos = self.player.raycast(self.world)
        
        if target_block:
            # Отключаем освещение для отрисовки контура
            glDisable(GL_LIGHTING)
            glDisable(GL_TEXTURE_2D)
            
            # Рисуем контур выбранного блока
            glColor3f(1.0, 1.0, 1.0)  # Белый цвет
            glLineWidth(2.0)
            
            x, y, z = target_block
            
            glBegin(GL_LINE_LOOP)
            glVertex3f(x, y, z)
            glVertex3f(x+1, y, z)
            glVertex3f(x+1, y, z+1)
            glVertex3f(x, y, z+1)
            glEnd()
            
            glBegin(GL_LINE_LOOP)
            glVertex3f(x, y+1, z)
            glVertex3f(x+1, y+1, z)
            glVertex3f(x+1, y+1, z+1)
            glVertex3f(x, y+1, z+1)
            glEnd()
            
            glBegin(GL_LINES)
            glVertex3f(x, y, z)
            glVertex3f(x, y+1, z)
            
            glVertex3f(x+1, y, z)
            glVertex3f(x+1, y+1, z)
            
            glVertex3f(x+1, y, z+1)
            glVertex3f(x+1, y+1, z+1)
            
            glVertex3f(x, y, z+1)
            glVertex3f(x, y+1, z+1)
            glEnd()
            
            # Если есть позиция для размещения блока, рисуем её другим цветом
            if place_pos:
                glColor3f(0.0, 1.0, 0.0)  # Зеленый цвет
                
                x, y, z = place_pos
                
                glBegin(GL_LINE_LOOP)
                glVertex3f(x, y, z)
                glVertex3f(x+1, y, z)
                glVertex3f(x+1, y, z+1)
                glVertex3f(x, y, z+1)
                glEnd()
                
                glBegin(GL_LINE_LOOP)
                glVertex3f(x, y+1, z)
                glVertex3f(x+1, y+1, z)
                glVertex3f(x+1, y+1, z+1)
                glVertex3f(x, y+1, z+1)
                glEnd()
                
                glBegin(GL_LINES)
                glVertex3f(x, y, z)
                glVertex3f(x, y+1, z)
                
                glVertex3f(x+1, y, z)
                glVertex3f(x+1, y+1, z)
                
                glVertex3f(x+1, y, z+1)
                glVertex3f(x+1, y+1, z+1)
                
                glVertex3f(x, y, z+1)
                glVertex3f(x, y+1, z+1)
                glEnd()
            
            # Восстанавливаем состояние OpenGL
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_LIGHTING)
    
    def draw_crosshair(self):
        """Отрисовка прицела в центре экрана"""
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, settings.WINDOW_WIDTH, 0, settings.WINDOW_HEIGHT, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Рисуем прицел
        center_x = settings.WINDOW_WIDTH // 2
        center_y = settings.WINDOW_HEIGHT // 2
        size = 10
        
        glColor3f(1.0, 1.0, 1.0)  # Белый цвет
        glBegin(GL_LINES)
        # Горизонтальная линия
        glVertex2f(center_x - size, center_y)
        glVertex2f(center_x + size, center_y)
        # Вертикальная линия
        glVertex2f(center_x, center_y - size)
        glVertex2f(center_x, center_y + size)
        glEnd()
        
        # Восстанавливаем матрицы
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def draw_fps(self):
        """Отображение счетчика FPS"""
        # Отключаем 3D-рендеринг для отрисовки текста
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Переключаемся на ортографическую проекцию
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, settings.WINDOW_WIDTH, 0, settings.WINDOW_HEIGHT, -1, 1)  # Изменено: второй параметр 0, третий settings.WINDOW_HEIGHT
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Создаем текстовую поверхность с FPS
        if not hasattr(self, 'fps_font') or self.fps_font is None:
            self.fps_font = pygame.font.SysFont("Arial", 18)
        
        fps_text = f"FPS: {self.fps_display}"
        fps_surface = self.fps_font.render(fps_text, True, (255, 255, 255))
        
        # Преобразуем поверхность в текстуру OpenGL
        fps_data = pygame.image.tostring(fps_surface, "RGBA", True)
        fps_width, fps_height = fps_surface.get_size()
        
        # Создаем текстуру
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, fps_width, fps_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, fps_data)
        
        # Настраиваем параметры текстуры
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Отрисовываем текстуру
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(10, 10)
        glTexCoord2f(1, 0); glVertex2f(10 + fps_width, 10)
        glTexCoord2f(1, 1); glVertex2f(10 + fps_width, 10 + fps_height)
        glTexCoord2f(0, 1); glVertex2f(10, 10 + fps_height)
        glEnd()
        
        # Удаляем текстуру
        glDeleteTextures(1, [texture_id])
        
        # Восстанавливаем состояние OpenGL
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        
        # Восстанавливаем матрицы
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def draw_selected_block_info(self):
        """Отображение информации о выбранном блоке"""
        # Отключаем 3D-рендеринг для отрисовки текста
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Переключаемся на ортографическую проекцию
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, settings.WINDOW_WIDTH, 0, settings.WINDOW_HEIGHT, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Создаем текстовую поверхность с информацией о блоке
        if not hasattr(self, 'block_font') or self.block_font is None:
            self.block_font = pygame.font.SysFont("Arial", 18)
        
        # Определяем название блока
        block_names = {
            0: "Воздух",
            1: "Земля",
            2: "Камень"
        }
        block_name = block_names.get(self.player.selected_block, f"Блок {self.player.selected_block}")
        
        block_text = f"Выбран: {block_name} [{self.player.selected_block}]"
        block_surface = self.block_font.render(block_text, True, (255, 255, 255))
        
        # Преобразуем поверхность в текстуру OpenGL
        block_data = pygame.image.tostring(block_surface, "RGBA", True)
        block_width, block_height = block_surface.get_size()
        
        # Создаем текстуру
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, block_width, block_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, block_data)
        
        # Настраиваем параметры текстуры
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Отрисовываем текстуру
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Размещаем текст в правом верхнем углу
        x_pos = settings.WINDOW_WIDTH - block_width - 10
        y_pos = settings.WINDOW_HEIGHT - block_height - 10
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x_pos, y_pos)
        glTexCoord2f(1, 0); glVertex2f(x_pos + block_width, y_pos)
        glTexCoord2f(1, 1); glVertex2f(x_pos + block_width, y_pos + block_height)
        glTexCoord2f(0, 1); glVertex2f(x_pos, y_pos + block_height)
        glEnd()
        
        # Удаляем текстуру
        glDeleteTextures(1, [texture_id])
        
        # Восстанавливаем состояние OpenGL
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        
        # Восстанавливаем матрицы
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def run(self):
        """Основной игровой цикл"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(settings.FPS)
        
        pygame.quit()

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
