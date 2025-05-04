import time
import pygame
import random
import json
import os
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 1200
CELL_SIZE = 60
GRID_WIDTH = 20
GRID_HEIGHT = 20
PANEL_HEIGHT = 200

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

PANEL_WIDTH = 350  # Ширина панели ресурсов
RESOURCE_PANEL_COLOR = (50, 50, 70)  # Цвет фона панели ресурсов
RESOURCE_IMAGES = {
    'ugol': 'middleage/buildings/Coal.png',
    'diamond': 'middleage/buildings/Diamond.png',
    'gold': 'middleage/buildings/Gold.png',
    'iron': 'middleage/buildings/Iron.png'
}
# Создаем экран
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Развивай свою цивилизацию")

# Шрифты
font = pygame.font.SysFont('Arial', 16)
title_font = pygame.font.SysFont('Arial', 24, bold=True)

Model = ["field", "resources", "townhall", "buildings", "user_balance", "costs"]
type_builds = {
    -2: "Территория",
    2: "Жилой дом",
    3: "Ферма",
    4: "Фабрика",
    5: 'Рудник',
    6: 'Амбар',
    7: 'Колония',
    8: 'Монетный двор',
    9: 'Лесопилка',
    10: 'Мастерская',
    11: 'Улуч. завода',
    12: 'Расширить территорию'

}

class ResourceVisibilityButton:
    def __init__(self, x, y, width=200, height=60):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (80, 80, 80)
        self.hover_color = (120, 120, 120)
        self.is_hovered = False
        self.active = False
        self.text = "Ресурсы"
        self.resource_images = {}
        
        # Загружаем изображения ресурсов
        for res_name, path in RESOURCE_IMAGES.items():
            try:
                img = pygame.image.load(path)
                self.resource_images[res_name] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            except:
                print(f"Не удалось загрузить изображение ресурса: {path}")
                self.resource_images[res_name] = None
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Подсветка если активно
        if self.active:
            pygame.draw.rect(surface, GREEN, self.rect, 3, border_radius=8)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.active = not self.active
                return True
        return False
    
    def draw_resources_overlay(self, game):
        """Отрисовывает поверхность с ресурсами"""
        if not self.active:
            return
        
        # Создаем полупрозрачную серую поверхность
        overlay = pygame.Surface((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((100, 100, 100, 150))  # Серый с прозрачностью
        
        # Рисуем ресурсы на этой поверхности
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                resource = game.data["resources"][row][col]
                if resource in self.resource_images and self.resource_images[resource]:
                    x = col * CELL_SIZE
                    y = row * CELL_SIZE
                    overlay.blit(self.resource_images[resource], (x, y))
        
        # Наносим поверхность на экран
        screen.blit(overlay, (400, 0))


class Button_bld:
    def __init__(self, type, txt, x, y, width=180, height=80):
        self.type = type
        self.txt = txt
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (70, 70, 120)
        self.hover_color = (100, 100, 180)
        self.is_hovered = False
        self.image = None
        self.image_rect = None
        # Загрузка изображения здания
        building_images = {
            1: "middleage/buildings/Main.png",
            2: "middleage/buildings/Home1.png",
            3: "middleage/buildings/Farm.png",
            4: "middleage/buildings/Factorio1.png",
            5: "middleage/buildings/Mine.png",
            6: "middleage/buildings/Barn.png",
            7: "middleage/buildings/Kolonisation.png",
            8: "middleage/buildings/Mint.png",
            9: "middleage/buildings/Sawmill.png",
            10: "middleage/buildings/Workshop.png",
            11: "middleage/buildings/Factorio2.png"
        }
        
        building_num = {
            'territory': -2,
            'house': 2,
            'farm': 3,
            'Factorio': 4,
            'Kolonisation': 7,
            'Mine': 5,
            'Barn': 6,
            'Mint': 8,
            'Sawmill': 9,
            'Workshop': 10,
            'Factorio2': 11,
            'remove': -1,
            'Ничего': 0
        }.get(type, 0)
        
        if building_num > 0:
            try:
                self.image = pygame.image.load(building_images[building_num])
                self.image = pygame.transform.scale(self.image, (40, 40))
                self.image_rect = self.image.get_rect(
                    center=(self.rect.centerx, self.rect.centery - 15))
            except:
                print(f"Не удалось загрузить изображение для {txt}")
                self.image = None
    

    
    def draw(self, surface):
        # Рисуем фон кнопки
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        
        # Рисуем изображение (если есть)
        if self.image:
            surface.blit(self.image, self.image_rect)
        
        # Рисуем текст
        text_surface = font.render(self.txt, True, WHITE)
        text_rect = text_surface.get_rect(
            center=(self.rect.centerx, self.rect.centery + 20))
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class EndTurnButton:
    def __init__(self, x, y, width=200, height=60):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (100, 150, 100)
        self.hover_color = (150, 200, 150)
        self.is_hovered = False
        self.text = "Конец хода"
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surface = title_font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class MainMenu:
    def __init__(self):
        self.buttons = []
        self.create_buttons()
        self.input_active = False
        self.input_text = ""
        self.input_rect = None
        self.font = pygame.font.SysFont('Arial', 24)
        self.game_files = []
        self.selected_game = None
        self.load_games_list()
        self.back_button = pygame.Rect(30, 30, 120, 40)
        self.scroll_offset = 0  # Смещение для прокрутки
        self.max_visible_games = 6  # Максимальное количество видимых игр
        self.scroll_bar = None
        self.scroll_dragging = False
        
    def create_buttons(self):
        button_width = 300
        button_height = 60
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 2 - 100
        
        self.new_game_btn = pygame.Rect(start_x, start_y, button_width, button_height)
        self.load_game_btn = pygame.Rect(start_x, start_y + 80, button_width, button_height)
        self.exit_btn = pygame.Rect(start_x, start_y + 160, button_width, button_height)
        
    def load_games_list(self):
        if not os.path.exists('middleage/games'):
            os.makedirs('middleage/games')
        self.game_files = [f for f in os.listdir('middleage/games') if f.endswith('.JSON')]
        self.scroll_offset = 0  # Сброс прокрутки при обновлении списка
        
    def draw(self, screen):
        screen.fill((50, 50, 70))
        
        title = title_font.render("Развивай свою цивилизацию", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        if self.selected_game is None:
            pygame.draw.rect(screen, (70, 70, 120), self.new_game_btn, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.new_game_btn, 2, border_radius=8)
            
            pygame.draw.rect(screen, (70, 70, 120), self.load_game_btn, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.load_game_btn, 2, border_radius=8)
            
            pygame.draw.rect(screen, (120, 70, 70), self.exit_btn, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.exit_btn, 2, border_radius=8)
            
            new_game_text = font.render("Новая игра", True, WHITE)
            load_game_text = font.render("Загрузить игру", True, WHITE)
            exit_text = font.render("Выйти из игры", True, WHITE)
            
            screen.blit(new_game_text, (self.new_game_btn.centerx - new_game_text.get_width()//2, 
                                       self.new_game_btn.centery - new_game_text.get_height()//2))
            screen.blit(load_game_text, (self.load_game_btn.centerx - load_game_text.get_width()//2, 
                                        self.load_game_btn.centery - load_game_text.get_height()//2))
            screen.blit(exit_text, (self.exit_btn.centerx - exit_text.get_width()//2, 
                                   self.exit_btn.centery - exit_text.get_height()//2))
        
        if self.input_active:
            pygame.draw.rect(screen, WHITE, self.input_rect, 2)
            pygame.draw.rect(screen, (80, 80, 100), self.input_rect)
            text_surface = self.font.render(self.input_text, True, WHITE)
            screen.blit(text_surface, (self.input_rect.x + 10, self.input_rect.y + 10))
            prompt = font.render("Введите название игры:", True, WHITE)
            screen.blit(prompt, (self.input_rect.x, self.input_rect.y - 30))
            
            pygame.draw.rect(screen, (120, 70, 70), self.back_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.back_button, 2, border_radius=8)
            back_text = font.render("Назад", True, WHITE)
            screen.blit(back_text, (self.back_button.centerx - back_text.get_width()//2, 
                                   self.back_button.centery - back_text.get_height()//2))
            
        elif self.selected_game == "load":
            panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
            pygame.draw.rect(screen, (50, 50, 80), panel_rect, border_radius=10)
            pygame.draw.rect(screen, BLUE, panel_rect, 2, border_radius=10)
            
            pygame.draw.rect(screen, (120, 70, 70), self.back_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.back_button, 2, border_radius=8)
            back_text = font.render("Назад", True, WHITE)
            screen.blit(back_text, (self.back_button.centerx - back_text.get_width()//2, 
                                   self.back_button.centery - back_text.get_height()//2))
            
            title = font.render("Выберите игру для загрузки:", True, WHITE)
            screen.blit(title, (panel_rect.centerx - title.get_width()//2, panel_rect.y + 20))
            
            if not self.game_files:
                no_games = font.render("Нет сохраненных игр", True, WHITE)
                screen.blit(no_games, (panel_rect.centerx - no_games.get_width()//2, panel_rect.centery))
            else:
                # Ограничиваем отображение игр в зависимости от прокрутки
                visible_games = self.game_files[self.scroll_offset:self.scroll_offset + self.max_visible_games]
                
                for i, game_file in enumerate(visible_games):
                    btn_rect = pygame.Rect(panel_rect.x + 50, panel_rect.y + 60 + i*40, 300, 30)
                    color = (100, 100, 150) if btn_rect.collidepoint(pygame.mouse.get_pos()) else (70, 70, 100)
                    
                    pygame.draw.rect(screen, color, btn_rect, border_radius=5)
                    pygame.draw.rect(screen, BLACK, btn_rect, 1, border_radius=5)
                    
                    name = font.render(game_file[:-5], True, WHITE)
                    screen.blit(name, (btn_rect.x + 10, btn_rect.y + 5))
                
                # Рисуем ползунок, если игр больше, чем можно отобразить
                if len(self.game_files) > self.max_visible_games:
                    # Фон ползунка
                    scroll_bg = pygame.Rect(panel_rect.right - 15, panel_rect.y + 60, 10, 240)
                    pygame.draw.rect(screen, (70, 70, 100), scroll_bg, border_radius=5)
                    
                    # Вычисляем размер и положение ползунка
                    scroll_height = max(30, 240 * self.max_visible_games / len(self.game_files))
                    scroll_pos = (240 - scroll_height) * self.scroll_offset / (len(self.game_files) - self.max_visible_games)
                    
                    self.scroll_bar = pygame.Rect(panel_rect.right - 15, panel_rect.y + 60 + scroll_pos, 10, scroll_height)
                    pygame.draw.rect(screen, (100, 100, 150), self.scroll_bar, border_radius=5)
    
    def handle_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == MOUSEBUTTONDOWN:
            # Проверяем back_button только когда он активен
            if (self.input_active or self.selected_game == "load") and self.back_button.collidepoint(mouse_pos):
                self.selected_game = None
                self.input_active = False
                return "back"
                
            if self.selected_game is None:
                if self.new_game_btn.collidepoint(mouse_pos):
                    self.selected_game = "new"
                    self.input_active = True
                    self.input_text = ""
                    self.input_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 150, 300, 40)
                    return "new"
                    
                elif self.load_game_btn.collidepoint(mouse_pos):
                    self.selected_game = "load"
                    self.load_games_list()
                    return "load"
                    
                elif self.exit_btn.collidepoint(mouse_pos):
                    return "exit"
                    
            elif self.selected_game == "load" and self.game_files:
                panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
                
                # Проверяем клик по ползунку
                if self.scroll_bar and self.scroll_bar.collidepoint(mouse_pos):
                    self.scroll_dragging = True
                    return None
                
                if panel_rect.collidepoint(mouse_pos):
                    visible_games = self.game_files[self.scroll_offset:self.scroll_offset + self.max_visible_games]
                    for i, game_file in enumerate(visible_games):
                        btn_rect = pygame.Rect(panel_rect.x + 50, panel_rect.y + 60 + i*40, 300, 30)
                        if btn_rect.collidepoint(mouse_pos):
                            return game_file
                            
        elif event.type == MOUSEBUTTONUP:
            self.scroll_dragging = False
            
        elif event.type == MOUSEMOTION and self.scroll_dragging:
            panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
            if panel_rect.collidepoint(mouse_pos):
                # Вычисляем новое положение прокрутки
                scroll_area = pygame.Rect(panel_rect.right - 15, panel_rect.y + 60, 10, 240)
                rel_y = mouse_pos[1] - scroll_area.y
                new_offset = int((rel_y / scroll_area.height) * (len(self.game_files) - self.max_visible_games))
                self.scroll_offset = max(0, min(new_offset, len(self.game_files) - self.max_visible_games))
                
        elif event.type == MOUSEWHEEL and self.selected_game == "load":
            # Прокрутка колесиком мыши
            self.scroll_offset = max(0, min(self.scroll_offset - event.y, len(self.game_files) - self.max_visible_games))
            
        elif event.type == KEYDOWN and self.input_active:
            if event.key == K_RETURN:
                if self.input_text:
                    filename = f"{self.input_text}.JSON"
                    self.input_active = False
                    self.selected_game = None
                    
                    game_data = {el: self.create_game_data(el) for el in Model}
                    try:
                        with open(f'middleage/games/{filename}', 'w', encoding='utf-8') as f:
                            json.dump(game_data, f, ensure_ascii=False, indent=4)
                        return None
                    except Exception as e:
                        print(f"Ошибка создания игры: {e}")
                        return None
            elif event.key == K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode
                
        return None    
    def create_game_data(self, el):
        # Реализация аналогична методу create() в классе Game
        if el == "field":
            z = 20
            matrix = [[0 for _ in range(z)] for _ in range(z)]
            for i in range(z):
                for j in range(z):
                    delta = 15
                    persent_forest = 30
                    persent_lug = 70
                
                    if i + 1 < z and matrix[i + 1][j] == 2:
                        persent_forest += delta
                        persent_lug -= delta
                    if j + 1 < z and matrix[i][j + 1] == 2:
                        persent_forest += delta
                        persent_lug -= delta
                    if j - 1 >= 0 and matrix[i][j - 1] == 2:
                        persent_forest += delta
                        persent_lug -= delta
                    if i - 1 >= 0 and matrix[i - 1][j] == 2:
                        persent_forest += delta
                        persent_lug -= delta
                        
                    rand = random.randint(0, 100)
                    
                    if rand <= persent_lug:
                        matrix[i][j] = 1
                    else:
                        matrix[i][j] = 2
            return matrix
        elif el == "resources":
            z = 20
            matrix = [['nothng' for _ in range(z)] for _ in range(z)]
            resources = ['gold'] * 5 + ['ugol'] * 20 + ['iron'] * 10 + ['diamond'] * 4 + ['nothng'] * 61
            for i in range(z):
                for j in range(z):
                    matrix[i][j] = random.choice(resources)
            return matrix
        elif el == "townhall":
            return []
        elif el == "buildings":
            return [[0 for _ in range(20)] for _ in range(20)]
        elif el == "user_balance": 
            return {
                "coin_profits": 100,
                "wood": 20,
                "hammers": 10,
                "food_profits": 0,
                "people": 0,
                "ugol": 0,
                "iron": 0,
                "diamond": 0,
                "gold": 0
            }
        elif el == "costs":
            return {
                "coin_profits": 0
            }
        
class Game:
    def __init__(self, f):
        try:
            with open(f'middleage/games/{f}', 'r', encoding='utf-8') as file:
                self.data = json.load(file)
                self.f = f
                if not self.check_data():
                    raise Exception("Ошибка при проверке данных")
                self.fase = 0  # 0 - выбор места для ратуши, 1 - основной режим
                self.selected_building = None
                self.buttons = self.create_buttons()
                self.hovered_cell = None
                self.show_confirmation = False
                self.confirmation_pos = None
                self.townhall_img = None
                self.yes_button = None
                self.hovered_cells = []
                self.show_confirmation_building = False
                self.costs = {
                    -2 : {'coin_profits': 50},
                    2 : {'coin_profits': 10},
                    3 : {'coin_profits': 10},
                    4 : {'coin_profits': 25},
                    5 : {'coin_profits': 10}, # + 5 * колво рудников
                    6 : {'coin_profits': 80, 'wood': 30}, 
                    7 : {'coin_profits': 10, 'hammers': 9, 'wood': 50},
                    8 : {'coin_profits': 100, 'hammers': 6, 'wood': 30},
                    9 : {'coin_profits': 50},
                    10 : {'coin_profits': 100, 'hammers': 5, 'wood': 40},
                    11 : {'coin_profits': 50, 'hammers': 3, 'ugol': 2},
                    12 : {'coin_profits': 30}
                }
                self.selected_info = None  # Будет хранить информацию о выбранной постройке
                self.selected_info_timer = 0  # Таймер для отображения информации
                self.cur_cell = None
                for row in self.data["buildings"]:
                    for build in row:
                        if build == 1:
                            self.fase = 1
                        elif build == 5:
                            self.costs[5]['coin_profits'] += 5
                

                self.building_images = {}
                building_files = {
                    1: "Main.png",
                    2: "Home1.png",
                    3: "Farm.png",
                    4: "Factorio1.png",
                    5: "Mine.png",
                    6: "Barn.png",
                    7: "Kolonisation.png",
                    8: "Mint.png",
                    9: "Sawmill.png",
                    10: "Workshop.png",
                    11: "Factorio2.png"
                }
                self.resource_visibility_button = ResourceVisibilityButton(SCREEN_WIDTH - 360, SCREEN_HEIGHT - PANEL_HEIGHT - 180)
                
                for building_num, filename in building_files.items():
                    try:
                        img = pygame.image.load(f'middleage/buildings/{filename}')
                        self.building_images[building_num] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
                    except:
                        print(f"Не удалось загрузить изображение для здания {building_num}")
                        self.building_images[building_num] = None
                        print(self.fase)
                 # Для хранения информации о наведении на ресурс
                self.hovered_resource = None
                self.hovered_resource_pos = None
                self.show_confirmation = False
                self.show_confirmation_building = False  # Добавьте эту строку
                self.confirmation_pos = None
                self.confirmation_type = None
                # Загружаем маленькие иконки ресурсов (20x20 пикселей)
                self.resource_icons = {}
                for res_name, path in RESOURCE_IMAGES.items():
                    try:
                        img = pygame.image.load(path)
                        self.resource_icons[res_name] = pygame.transform.scale(img, (40, 40))
                    except:
                        print(f"Не удалось загрузить иконку ресурса: {path}")
                        self.resource_icons[res_name] = None

                
        except Exception as e:
            print(f"Ошибка при загрузке игры: {e}")
            self.data = {el: self.create(el) for el in Model}
            self.f = f
            self.save_data()
            self.buttons = self.create_buttons()
            self.fase = 0
            self.hovered_cell = None
            self.show_confirmation = False
            self.confirmation_pos = None
            self.townhall_img = None

    def get_building_num(self, b_type):
        for key in type_builds.keys():
            if type_builds[key] == b_type:
                return key
        return None

    def translate(self, name):
        en_ru = {
            "coin_profits": 'Монеты',
            "wood": "Дерево",
            "hammers": "Молоты",
            "food_profits": "Продовольствие",
            "people": "Рабочая сила",
            "ugol": "Уголь",
            "iron": "Железо",
            "diamond": "Алмазы",
            "gold": "Золото"
        }
        return en_ru[name]

    def get_distance_from_townhall_or_colony(self, row, col):
        """Возвращает минимальное расстояние до ратуши или колонии и тип здания (1 - ратуша, 7 - колония)"""
        min_distance = float('inf')
        building_type = None
        
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if self.data["buildings"][r][c] in [1, 7]:  # 1 - ратуша, 7 - колония
                    distance = max(abs(row - r), abs(col - c))  # Расстояние в "кругах"
                    if distance < min_distance:
                        min_distance = distance
                        building_type = self.data["buildings"][r][c]
        
        return min_distance, building_type

    def calculate_territory_taxes(self):
        """Рассчитывает налоги за территорию"""
        taxes = 0
        
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if [col, row] in self.data["townhall"]:
                    distance, building_type = self.get_distance_from_townhall_or_colony(row, col)
                    
                    if building_type == 1:  # Ратуша
                        if distance == 1:
                            taxes += 1
                        elif distance == 2:
                            taxes += 2
                        elif distance >= 3:
                            taxes += 3
                    elif building_type == 7:  # Колония
                        if distance == 1:  # Первый круг от колонии
                            taxes += 2
                        elif distance == 2:
                            taxes += 3
                        elif distance >= 3:
                            taxes += 4
        
        return taxes


    def draw_resources_panel(self):
        """Отрисовка панели с ресурсами игрока"""
        # Рисуем фон панели
        panel_rect = pygame.Rect(30, 40, 340, SCREEN_HEIGHT - PANEL_HEIGHT - 400)
        pygame.draw.rect(screen, RESOURCE_PANEL_COLOR, panel_rect, border_radius=10)
        pygame.draw.rect(screen, BLUE, panel_rect, 2, border_radius=10)
        
        # Заголовок панели
        title = title_font.render("Ресурсы", True, WHITE)
        screen.blit(title, (150, 10))
        
        # Отображаем все ресурсы
        y_offset = 10
        for resource, amount in self.data["user_balance"].items():
            # Пропускаем нулевые ресурсы для чистоты интерфейса
            
                
            # Создаем строку для отображения
            resource_text = f"{self.translate(resource)}: {amount}"
            text_surface = font.render(resource_text, True, WHITE)
            screen.blit(text_surface, (panel_rect.x + 30, panel_rect.y + y_offset))
            
            y_offset += 30
        
        # Добавим разделитель
        pygame.draw.line(screen, BLUE, 
                        (panel_rect.x + 20, panel_rect.y + y_offset + 10),
                        (panel_rect.x + panel_rect.width - 20, panel_rect.y + y_offset + 10), 2)
    
    def handle_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if self.resource_visibility_button.is_clicked(mouse_pos, event):
            return True


        grid_x = (mouse_pos[0] - 400) // CELL_SIZE
        grid_y = mouse_pos[1] // CELL_SIZE
        self.handle_button_click(mouse_pos, event)
        # Проверка наведения на клетку
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            self.hovered_cell = (grid_y, grid_x)
        else:
            self.hovered_cell = None
        # Обработка клика
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.fase == 0 and self.hovered_cell and not self.show_confirmation:
                # Фаза выбора места для ратуши
                self.confirmation_pos = self.hovered_cell
                self.show_confirmation = True
                self.confirmation_type = "townhall"
                event = None
            elif self.fase == 1 and self.hovered_cell and self.selected_building and not self.show_confirmation_building:
                # Фаза строительства других зданий
                self.confirmation_pos = self.hovered_cell
                self.show_confirmation_building = True
                self.confirmation_type = "building"
                event = None
            
        window_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 75, 300, 150)
        self.yes_button = pygame.Rect(window_rect.x + 50, window_rect.y + 80, 80, 40)
        self.no_button = pygame.Rect(window_rect.x + 170, window_rect.y + 80, 80, 40)
        
        # Обработка кнопок подтверждения
        if event != None:
            if (self.show_confirmation or self.show_confirmation_building) and event.type == MOUSEBUTTONDOWN:
                
                if self.yes_button.collidepoint(event.pos):
                    if self.confirmation_type == "townhall":
                        self.place_townhall()
                    else:
                        self.place_building()
                    self.show_confirmation = False
                    self.show_confirmation_building = False
                elif self.no_button.collidepoint(event.pos):
                    self.show_confirmation = False
                    self.show_confirmation_building = False
    

    def can_build(self, building_num, row, col):
        """Проверяет, можно ли построить здание в указанной клетке"""
        # Проверка, что клетка не занята (кроме расширения территории)
        if building_num != 12 and self.data["buildings"][row][col] != 0:
            return False
            
        # Проверка территории (кроме колонии и расширения)
        if building_num not in [7, 12] and [col, row] not in self.data["townhall"]:
            return False
        
        # Проверка стоимости
        cost = self.costs.get(building_num, {})
        for resource, amount in cost.items():
            if self.data["user_balance"].get(resource, 0) < amount:
                return False
        
        # Для колонии - должна быть на границе территории
        if building_num == 7:
            is_border = False
            for i in range(row-1, row+2):
                for j in range(col-1, col+2):
                    if 0 <= i < GRID_HEIGHT and 0 <= j < GRID_WIDTH:
                        if [j, i] not in self.data["townhall"]:
                            is_border = True
                            break
            if not is_border:
                return False
        
        # Для расширения территории - клетка должна быть смежной с существующей территорией
        if building_num == 12:
            is_adjacent = False
            for i in range(row-1, row+2):
                for j in range(col-1, col+2):
                    if 0 <= i < GRID_HEIGHT and 0 <= j < GRID_WIDTH:
                        if [j, i] in self.data["townhall"] and (i != row or j != col):
                            is_adjacent = True
                            break
            if not is_adjacent:
                return False
        
        # Нельзя удалять ратушу (здание типа 1)
        if building_num == 0 and self.data["buildings"][row][col] == 1:
            return False
        
        return True

    def draw_grid(self):
        """Отрисовка игровой сетки"""
        try:
            for row in range(GRID_HEIGHT):
                for col in range(GRID_WIDTH):
                    x = col * CELL_SIZE + 400
                    y = row * CELL_SIZE
                    
                    cell_value = self.data.get("field", [[1]*GRID_WIDTH]*GRID_HEIGHT)[row][col]
                    color = self.get_cell_color(cell_value)

                    pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)
                    
                    # Отрисовка здания (если есть)
                    building_num = self.data["buildings"][row][col] if self.data["buildings"] else 0
                    if building_num > 0 and building_num in self.building_images and self.building_images[building_num]:
                        if building_num in [3, 6]:
                            pygame.draw.rect(screen, YELLOW, (x, y, CELL_SIZE, CELL_SIZE))
                        if building_num in [4, 11]:
                            pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE))
                        screen.blit(self.building_images[building_num], (x, y))
                    
                    # Отрисовка территории (если есть)
                    if [col, row] in self.data["townhall"]:
                        pygame.draw.rect(screen, BLUE, (x, y, CELL_SIZE, CELL_SIZE), 2)
                    
                    if self.resource_visibility_button.active and [col, row] in self.data["townhall"]:
                        resource = self.data["resources"][row][col]
                        if resource in self.resource_icons and self.resource_icons[resource]:
                            # Рисуем в левом нижнем углу клетки
                            icon_x = x + 2
                            icon_y = y + CELL_SIZE - 42
                            screen.blit(self.resource_icons[resource], (icon_x, icon_y))
                            
                            # Проверяем наведение на иконку
                            mouse_pos = pygame.mouse.get_pos()
                            icon_rect = pygame.Rect(icon_x, icon_y, 40, 40)
                            if icon_rect.collidepoint(mouse_pos):
                                self.hovered_resource = resource
                                self.hovered_resource_pos = (icon_x, icon_y)
            
            # Отрисовка выделения при наведении (только в фазе 0)
            if self.fase == 0 and self.hovered_cell and not self.confirmation_pos:
                hover_row, hover_col = self.hovered_cell
                self.hovered_cells = []
                self.cur_cell = self.hovered_cell
                for i in range(hover_row - 2, hover_row + 3):
                    for j in range(hover_col - 2, hover_col + 3):
                        if 0 <= i < GRID_HEIGHT and 0 <= j < GRID_WIDTH:
                            self.hovered_cells.append([j,i])
                if self.hovered_cells:
                    for el in self.hovered_cells:
                        x = el[0] * CELL_SIZE + 400
                        y = el[1] * CELL_SIZE
                        pygame.draw.rect(screen, RED, (x, y, CELL_SIZE, CELL_SIZE), 2)
            
            # Отрисовка предпросмотра здания (в фазе 1)
            if self.fase == 1 and self.hovered_cell and self.selected_building and not self.show_confirmation_building:
                hover_row, hover_col = self.hovered_cell
                building_num = {
                    'house': 2, 'farm': 3, 'Factorio': 4, 'Mine': 5,
                    'Barn': 6, 'Kolonisation': 7, 'Mint': 8,
                    'Sawmill': 9, 'Workshop': 10, 'Factorio2': 11
                }.get(self.selected_building, 0)
                
                if building_num > 0 and building_num in self.building_images:
                    x = hover_col * CELL_SIZE + 400
                    y = hover_row * CELL_SIZE
                    
                    # Проверяем можно ли построить
                    can_build = self.can_build(building_num, hover_row, hover_col)
                    border_color = BLUE if can_build else RED
                    
                    # Создаем полупрозрачную поверхность для предпросмотра
                    preview = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    preview.fill((255, 255, 255, 128))
                    preview.blit(self.building_images[building_num], (0, 0))
                    screen.blit(preview, (x, y))
                    pygame.draw.rect(screen, border_color, (x, y, CELL_SIZE, CELL_SIZE), 2)
                
        except Exception as e:
            print(f"Ошибка при отрисовке сетки: {e}")

    def draw_resource_tooltip(self):
        """Отрисовывает подсказку с названием ресурса при наведении"""
        if self.hovered_resource and self.hovered_resource_pos and self.resource_visibility_button.active:
            # Определяем название ресурса
            resource_names = {
                'ugol': 'Уголь',
                'diamond': 'Алмаз',
                'gold': 'Золото',
                'iron': 'Железо'
            }
            name = resource_names.get(self.hovered_resource, self.hovered_resource)
            
            # Создаем поверхность для подсказки
            text_surface = font.render(name, True, WHITE)
            text_width = text_surface.get_width()
            text_height = text_surface.get_height()
            
            # Позиционируем подсказку рядом с иконкой (снизу)
            pos_x, pos_y = self.hovered_resource_pos
            tooltip_x = pos_x
            tooltip_y = pos_y + 25  # Под иконкой
            
            # Рисуем фон подсказки
            pygame.draw.rect(screen, (70, 70, 90), 
                            (tooltip_x - 5, tooltip_y - 2, 
                            text_width + 10, text_height + 4))
            pygame.draw.rect(screen, WHITE, 
                            (tooltip_x - 5, tooltip_y - 2, 
                            text_width + 10, text_height + 4), 1)
            
            # Рисуем текст
            screen.blit(text_surface, (tooltip_x, tooltip_y))

    def place_building(self):
        """Установка выбранного здания"""
        if not self.confirmation_pos or not self.selected_building:
            return
            
        row, col = self.confirmation_pos
        
        # Получаем номер здания
        building_num = {
            'house': 2, 'farm': 3, 'Factorio': 4, 'Mine': 5,
            'Barn': 6, 'Kolonisation': 7, 'Mint': 8,
            'Sawmill': 9, 'Workshop': 10, 'Factorio2': 11,
            'remove': 0, 'expand': 12,
        }.get(self.selected_building, 0)
        
        # Проверяем можно ли построить/удалить
        if not self.can_build(building_num, row, col):
            print("Нельзя выполнить это действие здесь!")
            return
        
        # Для расширения территории - просто добавляем клетку
        if building_num == 12: 
            # Проверяем стоимость
            cost = self.costs.get(building_num, {})
            for resource, amount in cost.items():
                if self.data["user_balance"].get(resource, 0) < amount:
                    print(f"Не хватает ресурса {resource}!")
                    return
            
            # Добавляем клетку в территорию
            if [col, row] not in self.data["townhall"]:
                self.data["townhall"].append([col, row])
            
            # Списываем ресурсы
            for resource, amount in cost.items():
                self.data["user_balance"][resource] -= amount
            
            self.save_data()
            return

        # Для удаления зданий
        if building_num == 0:
            # Нельзя удалять ратушу
            if self.data["buildings"][row][col] == 1:
                print("Нельзя удалить ратушу!")
                return
                
            # Удаляем здание
            self.data["buildings"][row][col] = 0
            self.save_data()
            return

        # Для обычных зданий
        # Проверяем стоимость
        cost = self.costs.get(building_num, {})
        for resource, amount in cost.items():
            if self.data["user_balance"].get(resource, 0) < amount:
                print(f"Не хватает ресурса {resource}!")
                return
        
        # Устанавливаем здание
        self.data["buildings"][row][col] = building_num
        
        # Если это колония, добавляем территорию вокруг
        if building_num == 7:
            new_territory = []
            for i in range(row - 1, row + 2):
                for j in range(col - 1, col + 2):
                    if 0 <= i < GRID_HEIGHT and 0 <= j < GRID_WIDTH:
                        if [j, i] not in self.data["townhall"]:
                            new_territory.append([j, i])
            self.data["townhall"].extend(new_territory)
        
        # Списываем ресурсы
        for resource, amount in cost.items():
            self.data["user_balance"][resource] -= amount
        

        cost = 10
        for row in self.data["buildings"]:
            for build in row:
                if build == 5:
                    cost += 5
        
        self.costs[5]['coin_profits'] = cost
        
        self.save_data()

    def draw_confirmation_building(self):
        """Отрисовка окна подтверждения"""
        if not self.show_confirmation_building:
            return
            
        # Создаем полупрозрачную поверхность
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        screen.blit(s, (0, 0))
        
        # Рисуем окно подтверждения
        window_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 75, 300, 150)
        pygame.draw.rect(screen, WHITE, window_rect)
        pygame.draw.rect(screen, BLACK, window_rect, 2)
        
        # Текст вопроса
        if self.confirmation_type == "townhall":
            question = "Поставить ратушу здесь?"
        else:
            building_name = {
                'house': "Жилой дом",
                'farm': "Ферму",
                'Factorio': "Фабрику",
                'Mine': "Рудник",
                'Barn': "Амбар",
                'Kolonisation': "Колонию",
                'Mint': "Монетный двор",
                'Sawmill': "Лесопилку",
                'Workshop': "Мастерскую",
                'Factorio2': "Улучшение завода",
                'remove': "Удалить здание"
            }.get(self.selected_building, "здание")
            question = f"Поставить {building_name} здесь?"
        
        question_text = title_font.render(question, True, BLACK)
        screen.blit(question_text, (window_rect.x + 20, window_rect.y + 30))
        
        # Отображение стоимости (только для зданий)
        if self.confirmation_type == "building":
            building_num = {
                'house': 2,
                'farm': 3,
                'Factorio': 4,
                'Mine': 5,
                'Barn': 6,
                'Kolonisation': 7,
                'Mint': 8,
                'Sawmill': 9,
                'Workshop': 10,
                'Factorio2': 11
            }.get(self.selected_building, 0)
            
            if building_num in self.costs:
                cost_text = "Стоимость: " + ", ".join(
                    f"{k}: {v}" for k, v in self.costs[building_num].items())
                cost_surface = font.render(cost_text, True, BLACK)
                screen.blit(cost_surface, (window_rect.x + 20, window_rect.y + 60))
        
        # Кнопки Да/Нет
        self.yes_button = pygame.Rect(window_rect.x + 50, window_rect.y + 80, 80, 40)
        self.no_button = pygame.Rect(window_rect.x + 170, window_rect.y + 80, 80, 40)
        
        pygame.draw.rect(screen, GREEN, self.yes_button)
        pygame.draw.rect(screen, RED, self.no_button)
        
        yes_text = font.render("Да", True, WHITE)
        no_text = font.render("Нет", True, WHITE)
        
        screen.blit(yes_text, (self.yes_button.x + 30, self.yes_button.y + 10))
        screen.blit(no_text, (self.no_button.x + 30, self.no_button.y + 10))
    
    def place_townhall(self):
        """Установка ратуши и территории"""
        if not self.confirmation_pos:
            return
        
        territory = self.hovered_cells
        hover_row, hover_col = self.cur_cell
        center_col = hover_col
        center_row = hover_row
        # Устанавливаем ратушу в центре
        if not self.data["buildings"]:
            self.data["buildings"] = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.data["buildings"][center_row][center_col] = 1  # 1 - ратуша
        
        # Сохраняем территорию
        self.data["townhall"] = territory
        
        # Переходим к следующей фазе игры
        self.fase = 1
        self.hovered_cells = None
        # Сохраняем изменения
        self.save_data()
    
    def draw_confirmation(self):
        """Отрисовка окна подтверждения"""
        if not self.show_confirmation:
            return
            
        # Создаем полупрозрачную поверхность
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))  # Черный с прозрачностью 50%
        screen.blit(s, (0, 0))
        
        # Рисуем окно подтверждения
        window_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 75, 300, 150)
        pygame.draw.rect(screen, WHITE, window_rect)
        pygame.draw.rect(screen, BLACK, window_rect, 2)
        
        # Текст вопроса
        question = title_font.render("Поставить ратушу здесь?", True, BLACK)
        screen.blit(question, (window_rect.x + 20, window_rect.y + 30))
        
        # Кнопки Да/Нет
        self.yes_button = pygame.Rect(window_rect.x + 50, window_rect.y + 80, 80, 40)
        self.no_button = pygame.Rect(window_rect.x + 170, window_rect.y + 80, 80, 40)
        
        pygame.draw.rect(screen, GREEN, self.yes_button)
        pygame.draw.rect(screen, RED, self.no_button)
        
        yes_text = font.render("Да", True, WHITE)
        no_text = font.render("Нет", True, WHITE)
        
        screen.blit(yes_text, (self.yes_button.x + 30, self.yes_button.y + 10))
        screen.blit(no_text, (self.no_button.x + 30, self.no_button.y + 10))
    
    def calculate_upcoming_changes(self):
        """Рассчитывает какие изменения произойдут при завершении хода"""
        profits = [[{} for _ in range(20)] for __ in range(20)]
        upcoming = {
            'people': 0,
            'coin_profits': 0,
            'food_profits': 0,
            'wood': 0,
            'hammers': 0,
            'ugol': 0,
            'iron': 0,
            'diamond': 0,
            'gold': 0
        }
        
        for r in range(20):
            for c in range(20):
                cell_type = self.data["buildings"][r][c]
                
                if cell_type == 1:  # Ратуша
                    profits[r][c] = {'people': 3, 'coin_profits': 60, 'food_profits': 1}
                elif cell_type == 2:  # Дом
                    profits[r][c] = {'people': 3, 'coin_profits': -5}
                elif cell_type == 3:  # Ферма
                    neighbours = 0
                    barns = 0
                    factorios = 0
                    for i in range(r - 1, r + 2):
                        for j in range(c - 1, c + 2):
                            if i < 0 or i > 19 or j < 0 or j > 19 or (j == c and i == r):
                                continue
                            if self.data["buildings"][i][j] == 3:
                                neighbours += 1
                            elif self.data["buildings"][i][j] == 6:
                                barns += 1
                            elif self.data["buildings"][i][j] == 4:
                                factorios += 1
                    
                    food = round(2 * (1 + neighbours * 0.2 + barns * 2 - factorios * 0.5), 3)
                    profits[r][c] = {
                        'people': -1,
                        'coin_profits': 0,
                        'food_profits': food if food > 0 else 0
                    }
                    
                elif cell_type == 4:  # Завод
                    neighbours = 0
                    update_factorios = 0
                    for i in range(r - 1, r + 2):
                        for j in range(c - 1, c + 2):
                            if i < 0 or i > 19 or j < 0 or j > 19 or (j == c and i == r):
                                continue
                            if self.data["buildings"][i][j] == 4:
                                neighbours += 1
                            elif self.data["buildings"][i][j] == 11:
                                update_factorios += 1
                    
                    coin = round(20 * (1 + update_factorios * 0.4 + neighbours * 0.2), 3)
                    profits[r][c] = {
                        'people': -3,
                        'coin_profits': coin if coin > 0 else 0,
                        'food_profits': -2,
                        'hammers': 1 * (update_factorios + 1)
                    }
                    
                elif cell_type == 5:  # Рудник
                    resource = self.data["resources"][r][c]
                    profits[r][c] = {
                        'people': -1,
                        resource: 1 if resource != 'nothng' else 0,
                        'food_profits': -1
                    }
                    
                elif cell_type == 7:  # Колония
                    profits[r][c] = {'people': 2, 'coin_profits': 30}
                    
                elif cell_type == 8:  # Монетный двор
                    profits[r][c] = {'people': -1, 'gold': -2, 'coin_profits': 60}
                    
                elif cell_type == 9:  # Лесопилка
                    forests = 0
                    for i in range(r - 1, r + 2):
                        for j in range(c - 1, c + 2):
                            if i < 0 or i > 19 or j < 0 or j > 19:
                                continue
                            elif self.data["field"][i][j] == 2:
                                forests += 1
                    profits[r][c] = {
                        'people': -1 * (forests // 3),
                        'wood': 1 * forests
                    }
                    
                elif cell_type == 10:  # Мастерская
                    factorios = 0
                    for i in range(r - 1, r + 2):
                        for j in range(c - 1, c + 2):
                            if i < 0 or i > 19 or j < 0 or j > 19:
                                continue
                            elif self.data["buildings"][i][j] == 4:
                                factorios += 1
                    profits[r][c] = {
                        'people': -2,
                        'iron': -1,
                        'wood': -2,
                        'hammers': 0.5 * factorios
                    }
        
        # Суммируем все изменения
        for row in profits:
            for cell in row:
                for key, value in cell.items():
                    if key in upcoming:
                        upcoming[key] += value
        
        # Применяем штрафы (если нужно)
        if upcoming['people'] <= 0:
            for key in ['coin_profits', 'food_profits', 'wood', 'hammers']:
                if upcoming[key] > 0:
                    upcoming[key] = round(upcoming[key] * (1 + (0.2 * upcoming['people'])), 3)
        
        if upcoming['food_profits'] <= 0:
            for key in ['coin_profits', 'wood', 'hammers']:
                if upcoming[key] > 0:
                    upcoming[key] = round(upcoming[key] * (1 + (0.2 * upcoming['food_profits'])), 3)
        
        return upcoming

    def draw(self):
        """Основной метод отрисовки"""
        screen.fill(BLACK)
        self.draw_resources_panel()
        self.draw_grid()
        # Отрисовываем подсказку с ресурсом (поверх всего)
        
        
        if self.fase == 1:  # В основной фазе рисуем кнопки
            self.draw_buttons()
            self.draw_resource_tooltip()
            self.draw_deficits_bonuses() 
            self.draw_selected_info()  # Добавляем отрисовку информации
        
        if self.show_confirmation:
            self.draw_confirmation()

        if self.show_confirmation_building:
            self.draw_confirmation_building()
        
        pygame.display.flip()
    
    def create_buttons(self):
        buildings = [
            ('house', 'Жилой дом'),
            ('farm', 'Ферма'),
            ('Factorio', 'Фабрика'),
            ('Mine', 'Рудник'),
            ('Barn', 'Амбар'),
            ('Kolonisation', 'Колония'),
            ('Mint', 'Монетный двор'),
            ('Sawmill', 'Лесопилка'),
            ('Workshop', 'Мастерская'),
            ('Factorio2', 'Улуч. завода'),
            ('expand', 'Расширить территорию'),
            ('remove', 'Удалить')
        
        ]
        
        buttons = []
        start_x = SCREEN_WIDTH - 360
        start_y = 50
        button_width = 150
        button_height = 80
        button_spacing = 20
        
        # Располагаем кнопки в 2 столбца
        for i, (b_type, b_text) in enumerate(buildings):
            col = i // 6  # 6 кнопок в столбце
            row = i % 6
            x = start_x + col * (button_width + button_spacing)
            y = start_y + row * (button_height + button_spacing)
            buttons.append(Button_bld(b_type, b_text, x, y, button_width, button_height))
        
        # Создаем кнопку "Конец хода" отдельно
        self.end_turn_button = EndTurnButton(
            start_x, 
            SCREEN_HEIGHT - PANEL_HEIGHT - 100,
            button_width * 2 + button_spacing, 
            60
        )
        
        return buttons

    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Рисуем панель для кнопок
        panel_rect = pygame.Rect(
            SCREEN_WIDTH - 370, 40, 
            340, SCREEN_HEIGHT - PANEL_HEIGHT - 400)
        pygame.draw.rect(screen, (50, 50, 80), panel_rect, border_radius=10)
        pygame.draw.rect(screen, BLUE, panel_rect, 2, border_radius=10)
        
        # Заголовок панели
        title = title_font.render("Постройки", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH - 250, 10))
        
        # Рисуем кнопки зданий
        for button in self.buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)
            
            # Подсветка выбранной кнопки
            if self.selected_building == button.type:
                pygame.draw.rect(screen, GREEN, button.rect, 3, border_radius=8)
        
            # Рисуем кнопку видимости ресурсов
        self.resource_visibility_button.check_hover(mouse_pos)
        self.resource_visibility_button.draw(screen)
        
        

        # Рисуем кнопку "Конец хода"
        self.end_turn_button.check_hover(mouse_pos)
        self.end_turn_button.draw(screen)

    def handle_button_click(self, pos, event):
        # Проверяем кнопку "Конец хода"
        if self.end_turn_button.is_clicked(pos, event):
            profits = self.calculate_profits()
            
            # Формируем сообщение с результатами хода
            profit_text = "Результаты хода:\n"
            for resource, value in profits.items():
                if value != 0:
                    sign = "+" if value > 0 else ""
                    profit_text += f"{resource}: {sign}{value}\n"
            
            self.selected_info = profit_text
            self.selected_info_timer = 300  # Показывать 5 секунд
            return True
        
        # Проверяем остальные кнопки
        for button in self.buttons:
            if button.is_clicked(pos, event):
                self.selected_building = button.type
                building_num = self.get_building_num(button.txt)
                cost = self.costs.get(building_num, {})
                
                cost_text = ", ".join([f"{k}: {v}" for k, v in cost.items()])
                self.selected_info = f"Выбрано: {button.txt}\nСтоимость: {cost_text}"
                self.selected_info_timer = 180
                return True
        return False
    
    def draw_deficits_bonuses(self):
        """Отрисовка предстоящих изменений ресурсов"""
        upcoming = self.calculate_upcoming_changes()
        
        # Рассчитываем налоги отдельно
        territory_taxes = self.calculate_territory_taxes()
        
        # Рисуем фон
        panel_rect = pygame.Rect(30, SCREEN_HEIGHT - PANEL_HEIGHT - 150, 340, 300)
        pygame.draw.rect(screen, RESOURCE_PANEL_COLOR, panel_rect, border_radius=10)
        pygame.draw.rect(screen, BLUE, panel_rect, 2, border_radius=10)
        
        # Заголовок
        title = font.render("Предстоящие изменения:", True, WHITE)
        screen.blit(title, (panel_rect.x + 20, panel_rect.y + 10))
        
        y_offset = 40
        
        # Отображаем налоги
        y_offset += 20
        
        # Отображаем все значимые изменения
        for resource, change in upcoming.items():
            if resource == "coin_profits":
                # Для монет учитываем уже налоги
                total = change - territory_taxes
                color = GREEN if total > 0 else RED
                text = f"{self.translate(resource)}: {'+' if total > 0 else ''}{total * 1000 // 10 / 100}"
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (panel_rect.x + 30, panel_rect.y + y_offset))
                y_offset += 20
            elif change != 0 and resource != "coin_profits":
                color = GREEN if change > 0 else RED
                text = f"{self.translate(resource)}: {'+' if change > 0 else ''}{change * 1000 // 10 / 100}"
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (panel_rect.x + 30, panel_rect.y + y_offset))
                y_offset += 20
        
        # Добавим подсказку
        if y_offset == 40:  # Если нет изменений
            text = font.render("Нет значимых изменений", True, WHITE)
            screen.blit(text, (panel_rect.x + 30, panel_rect.y + y_offset))


    def save_data(self):
        try:
            for key in self.data["user_balance"].keys():
                self.data["user_balance"][key] = self.data["user_balance"][key] * 1000 // 10 / 100
            with open(f'middleage/games/{self.f}', 'w', encoding='utf-8') as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении игры: {e}")

    

    def calculate_profits(self):
        """Рассчитывает и применяет доходы/расходы за ход"""
        upcoming = self.calculate_upcoming_changes()
        
        # Добавляем налоги за территорию
        territory_taxes = self.calculate_territory_taxes()
        upcoming["coin_profits"] -= territory_taxes
        
        # Применяем изменения к балансу
        for resource, change in upcoming.items():
            if resource in ['people', 'food_profits']:
                self.data["user_balance"][resource] = change
            elif resource in self.data["user_balance"]:
                self.data["user_balance"][resource] += change
        
        # Проверяем баланс монет
        if self.data["user_balance"].get("coin_profits", 0) < 0:
            self.reset_game()  # Сбрасываем игру при отрицательном балансе
        
        self.save_data()
        return upcoming

    def draw_selected_info(self):
        if self.selected_info:
            # Уменьшаем таймер
            self.selected_info_timer -= 1
            
            # Разбиваем текст на строки
            lines = self.selected_info.split('\n')
            
            # Вычисляем размеры блока текста
            line_height = font.get_linesize()
            total_height = len(lines) * line_height
            max_width = max(font.size(line)[0] for line in lines)
            
            # Позиция для отображения (например, внизу слева)
            x = 20
            y = SCREEN_HEIGHT - PANEL_HEIGHT - total_height - 20
            
            # Рисуем полупрозрачный фон
            info_rect = pygame.Rect(x - 10, y - 150, max_width + 20, total_height + 20)
            s = pygame.Surface((info_rect.width, info_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))  # Черный с прозрачностью
            screen.blit(s, info_rect)
            
            # Рисуем текст
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, WHITE)
                screen.blit(text_surface, (x, y - 140 + i * line_height))


    def check_data(self):
        data = self.data
        keys = data.keys()
        modified = False
        
        for el in Model:
            if el not in keys:
                data[el] = self.create(el)
                modified = True
                
        if modified:
            self.save_data()
            
        return True

    def create(self, el):
        if el == "field":
            z = 20
            matrix = [[0 for _ in range(z)] for _ in range(z)]
            for i in range(z):
                for j in range(z):
                    delta = 15
                    persent_forest = 30
                    persent_lug = 70
                
                    # Условия для изменения вероятностей
                    if i + 1 < z and matrix[i + 1][j] == 2:
                        persent_forest += delta
                        persent_lug -= delta
                    if j + 1 < z and matrix[i][j + 1] == 2:
                        persent_forest += delta
                        persent_lug -= delta
                    if j - 1 >= 0 and matrix[i][j - 1] == 2:
                        persent_forest += delta
                        persent_lug -= delta
                    if i - 1 >= 0 and matrix[i - 1][j] == 2:
                        persent_forest += delta
                        persent_lug -= delta
                        
                    rand = random.randint(0, 100)
                    
                    if rand <= persent_lug:
                        matrix[i][j] = 1  # поле
                    else:
                        matrix[i][j] = 2  # лес
            return matrix

        elif el == "resources":
            z = 20
            matrix = [['nothng' for _ in range(z)] for _ in range(z)]
            resources = ['gold'] * 5 + ['ugol'] * 20 + ['iron'] * 10 + ['diamond'] * 4 + ['nothng'] * 61
            
            for i in range(z):
                for j in range(z):
                    matrix[i][j] = random.choice(resources)
            return matrix
            
        elif el == "townhall":
            return []
        elif el == "buildings":
            return [[0 for _ in range(20)] for _ in range(20)]
        elif el == "user_balance": 
            return {
                "coin_profits": 100,
                "wood": 20,
                "hammers": 10,
                "food_profits": 0,
                "people": 0,
                "ugol": 0,
                "iron": 0,
                "diamond": 0,
                "gold": 0
            }
        elif el == "costs":
            return {
                "coin_profits": 0
            }

    def get_cell_color(self, c):
        if c == 1:
            return LIGHT_GREEN
        elif c == 2:
            return DARK_GREEN
        return GRAY
    
    def reset_game(self):
        """Полностью сбрасывает игру"""
        print("Игра сброшена из-за отрицательного баланса монет!")
        self.data = {el: self.create(el) for el in Model}
        self.fase = 0
        self.selected_building = None
        self.hovered_cell = None
        self.show_confirmation = False
        self.confirmation_pos = None
        self.save_data()

# Проверяем существование директории
if not os.path.exists('middleage/games'):
    os.makedirs('middleage/games')

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Развивай свою цивилизацию")
    clock = pygame.time.Clock()
    
    menu = MainMenu()
    current_screen = "menu"
    game = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if current_screen == "game":
                        current_screen = "menu"
                    else:
                        running = False
            
            if current_screen == "menu":
                result = menu.handle_events(event)
                if result == "exit":
                    running = False
                elif result == "back":
                    continue  # Уже обработано в меню
                elif result and result.endswith('.JSON'):
                    try:
                        game = Game(result)
                        current_screen = "game"
                    except Exception as e:
                        print(f"Ошибка загрузки игры: {e}")
            elif current_screen == "game":
                game.handle_events(event)
        
        # Отрисовка
        if current_screen == "menu":
            menu.draw(screen)
        elif current_screen == "game":
            game.draw()
            # Кнопка "В меню"
            back_btn = pygame.Rect(30, SCREEN_HEIGHT - 60, 120, 40)
            pygame.draw.rect(screen, (120, 70, 70), back_btn, border_radius=8)
            pygame.draw.rect(screen, BLACK, back_btn, 2, border_radius=8)
            back_text = font.render("В меню", True, WHITE)
            screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, 
                                  back_btn.centery - back_text.get_height()//2))
            
            # Проверка клика
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0] and back_btn.collidepoint(mouse_pos):
                current_screen = "menu"
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    # Проверяем существование директории
    if not os.path.exists('middleage/games'):
        os.makedirs('middleage/games')
    main()