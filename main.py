from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from player import Player
from world import World  # Импортируем мир
import settings


# Инициализация Pygame и OpenGL
pygame.init()
screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)

# Настройка OpenGL
glEnable(GL_DEPTH_TEST)
glClearColor(0.4, 0.8, 1, 1)  # небо
glMatrixMode(GL_PROJECTION)
gluPerspective(70, (settings.WINDOW_WIDTH / settings.WINDOW_HEIGHT), 0.1, 100)
glMatrixMode(GL_MODELVIEW)

# Настройка освещения
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_COLOR_MATERIAL)
glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 10.0, 10.0, 1.0])  # Источник света
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # Диффузное освещение
glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])  # Отражённый свет
glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # Материал блоков



running = True

FPS = settings.FPS
game_ticks = pygame.time.Clock()

# Создаём игрока и мир
player = Player()
world = World(10 * settings.WORLD_SIZE, 5, 10 * settings.WORLD_SIZE)
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)  # Захват мыши

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)

    # Работа с мышью и клавишами
    dx, dy = pygame.mouse.get_rel()
    player.handle_mouse(dx, dy)

    keys = pygame.key.get_pressed()
    player.handle_keys(keys)

    # Отрисовка сцены
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    player.update_camera()

    light_position = [10.0, 10.0, 20.0 * settings.WORLD_SIZE, 1.0]  # Позиция источника света в мировых координатах
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    
    world.draw()  # Рисуем мир

    pygame.display.flip()
    game_ticks.tick(FPS)

pygame.quit()
