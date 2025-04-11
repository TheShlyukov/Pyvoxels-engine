# settings.py

# Параметры графики
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Параметры управления
MOUSE_SENSITIVITY = 0.15
PLAYER_SPEED = 0.05
SPRINT_SPEED = PLAYER_SPEED * 2
FLY_SPEED = 0.1

# Физика
GRAVITY = 0.01
JUMP_STRENGTH = 0.2

# Параметры мира
WORLD_SIZE = 4
RENDER_DISTANCE = 8  # Дистанция отрисовки в блоках
CHUNK_SIZE = 16      # Размер чанка в блоках

# Параметры игрока
PLAYER_HEIGHT = 1.8  # Высота игрока в блоках
PLAYER_WIDTH = 0.6   # Ширина игрока в блоках
PLAYER_EYE_HEIGHT = 1.6  # Высота глаз от земли

# Взаимодействие с блоками
INTERACTION_DISTANCE = 5.0  # Максимальное расстояние для взаимодействия с блоками

# Отладка
DEBUG_MODE = False   # Режим отладки
SHOW_FPS = True      # Показывать FPS
