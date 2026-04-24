# AI RACING SPRINT - FIXED FULL CODE

import pygame
import random
import sys
from dataclasses import dataclass
import asyncio

pygame.init()

# ---------------- SETTINGS ----------------
WIDTH, HEIGHT = 960, 720
FPS = 60
ROAD_WIDTH = 440
ROAD_LEFT = (WIDTH - ROAD_WIDTH) // 2
ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH
FINISH_DISTANCE = 8000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 60)
GREEN = (20, 140, 70)
YELLOW = (255, 220, 0)
RED = (220, 60, 60)
BLUE = (60, 120, 255)
CYAN = (60, 220, 255)
PURPLE = (180, 90, 255)
ORANGE = (255, 150, 60)

CAR_COLORS = [BLUE, RED, YELLOW, CYAN, PURPLE, ORANGE]

LANE_CENTERS = [
    ROAD_LEFT + 75,
    ROAD_LEFT + 185,
    ROAD_LEFT + 295,
    ROAD_LEFT + 405
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Racing Sprint Ultimate")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont("arial", 52, True)
big_font = pygame.font.SysFont("arial", 42, True)
ui_font = pygame.font.SysFont("arial", 24, True)
small_font = pygame.font.SysFont("arial", 18)

# ---------------- DATA ----------------
@dataclass
class Racer:
    name: str
    color: tuple
    x: float
    y: float
    speed: float
    max_speed: float
    accel: float
    distance: float = 0
    finished: bool = False


# ---------------- GAME ----------------
class Game:

    def __init__(self):
        self.state = "menu"
        self.selected_car = 0
        self.reset()

    def reset(self):

        lane1 = LANE_CENTERS[0]
        lane2 = LANE_CENTERS[1]
        lane3 = LANE_CENTERS[2]
        lane4 = LANE_CENTERS[3]

        # PLAYER uses selected menu color
        self.player = Racer(
            "PLAYER 1",
            CAR_COLORS[self.selected_car],
            lane2,
            HEIGHT - 180,
            0,
            11,
            0.15
        )

        # CPU Cars
        self.ai = []

        self.ai.append(Racer(
            "CPU-1",
            RED,
            lane1,
            HEIGHT - 120,
            5.0,
            8.0,
            0.02
        ))

        self.ai.append(Racer(
            "CPU-2",
            YELLOW,
            lane4,
            HEIGHT - 75,
            5.2,
            8.2,
            0.02
        ))

        self.ai.append(Racer(
            "CPU-3",
            CYAN,
            lane3,
            HEIGHT - 30,
            5.4,
            8.4,
            0.02
        ))

        self.all = [self.player] + self.ai

        self.scroll = 0
        self.countdown = 180
        self.result = ""
        self.race_over = False
        self.nitro = 100
        self.rain = True
        self.night = True

        self.raindrops = []
        for i in range(100):
            self.raindrops.append(
                [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
            )

    # ---------------- MENU ----------------
    def draw_menu(self):

        screen.fill((15, 15, 30))

        txt = title_font.render(
            "AI RACING SPRINT",
            True,
            YELLOW
        )
        screen.blit(
            txt,
            (WIDTH // 2 - txt.get_width() // 2, 80)
        )

        txt2 = ui_font.render(
            "Select Car Color (Left / Right)",
            True,
            WHITE
        )
        screen.blit(
            txt2,
            (WIDTH // 2 - txt2.get_width() // 2, 180)
        )

        pygame.draw.rect(
            screen,
            CAR_COLORS[self.selected_car],
            (430, 260, 100, 170),
            border_radius=18
        )

        txt3 = ui_font.render(
            "Press ENTER to Start",
            True,
            WHITE
        )
        screen.blit(
            txt3,
            (WIDTH // 2 - txt3.get_width() // 2, 500)
        )

    # ---------------- INPUT ----------------
    def handle_input(self):

        keys = pygame.key.get_pressed()

        if self.state == "menu":
            return

        if self.countdown > 0 or self.race_over:
            return

        # Speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.speed = min(
                self.player.max_speed,
                self.player.speed + self.player.accel
            )
        else:
            self.player.speed = max(
                3,
                self.player.speed - 0.14
            )

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.speed = max(
                0,
                self.player.speed - 0.16
            )

        # Left Right
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.x -= 5

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.x += 5

        # Nitro
        if keys[pygame.K_SPACE] and self.nitro > 0:
            self.player.speed = min(
                15,
                self.player.speed + 0.35
            )
            self.nitro -= 0.5

        # Boundary
        if self.player.x < ROAD_LEFT + 30:
            self.player.x = ROAD_LEFT + 30

        if self.player.x > ROAD_RIGHT - 30:
            self.player.x = ROAD_RIGHT - 30

    # ---------------- AI ----------------
    def update_ai(self):

        for car in self.ai:

            if car.finished:
                continue

            car.speed = min(
                car.max_speed,
                car.speed + car.accel
            )

            car.distance += car.speed

    # ---------------- UPDATE ----------------
    def update(self):

        if self.state != "game":
            return

        if self.countdown > 0:
            self.countdown -= 1
            return

        if self.race_over:
            return

        self.player.distance += self.player.speed
        self.scroll += self.player.speed

        self.update_ai()
        self.check_finish()

    def check_finish(self):

        for car in self.all:
            if car.distance >= FINISH_DISTANCE:
                car.finished = True

        for car in self.all:
            if car.finished:

                self.race_over = True

                ranking = sorted(
                    self.all,
                    key=lambda c: c.distance,
                    reverse=True
                )

                rank = ranking.index(self.player) + 1

                if rank == 1:
                    self.result = "YOU WIN!"
                elif rank == 2:
                    self.result = "SECOND PLACE!"
                elif rank == 3:
                    self.result = "THIRD PLACE!"
                else:
                    self.result = "YOU LOST!"

                break

    # ---------------- BACKGROUND ----------------
    def draw_bg(self):

        if self.night:
            screen.fill((10, 10, 25))
        else:
            screen.fill(GREEN)

        pygame.draw.rect(
            screen,
            GRAY,
            (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT)
        )

        # lane lines
        for lx in [ROAD_LEFT + 110, ROAD_LEFT + 220, ROAD_LEFT + 330]:
            for y in range(0, HEIGHT, 70):
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (lx, y + (self.scroll % 70), 6, 40)
                )

        # finish line
        fy = HEIGHT - (FINISH_DISTANCE - self.player.distance)

        if -100 <= fy <= HEIGHT:

            for r in range(8):
                for c in range(10):

                    if (r + c) % 2 == 0:
                        col = WHITE
                    else:
                        col = BLACK

                    pygame.draw.rect(
                        screen,
                        col,
                        (ROAD_LEFT + c * 44, fy + r * 10, 44, 10)
                    )

        # rain
        if self.rain:

            for drop in self.raindrops:

                pygame.draw.line(
                    screen,
                    CYAN,
                    (drop[0], drop[1]),
                    (drop[0] - 2, drop[1] + 10),
                    1
                )

                drop[1] += 10

                if drop[1] > HEIGHT:
                    drop[0] = random.randint(0, WIDTH)
                    drop[1] = 0

    # ---------------- DRAW CAR ----------------
    def draw_car(self, car):

        y = car.y - (car.distance - self.player.distance)

        rect = pygame.Rect(
            car.x - 23,
            y - 43,
            46,
            86
        )

        pygame.draw.rect(screen, car.color, rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)

        pygame.draw.rect(
            screen,
            WHITE,
            (rect.x + 8, rect.y + 10, 30, 14)
        )

        pygame.draw.rect(
            screen,
            WHITE,
            (rect.x + 8, rect.y + 60, 30, 12)
        )

        if car == self.player:
            label = small_font.render(
                "PLAYER 1",
                True,
                YELLOW
            )
        else:
            label = small_font.render(
                car.name,
                True,
                WHITE
            )

        screen.blit(
            label,
            (rect.centerx - label.get_width() // 2, rect.y - 22)
        )

    # ---------------- UI ----------------
    def draw_ui(self):

        txt = small_font.render(
            "Distance: " +
            str(int(self.player.distance)) +
            " / " +
            str(FINISH_DISTANCE),
            True,
            WHITE
        )
        screen.blit(txt, (20, 20))

        txt2 = small_font.render(
            "Nitro: " +
            str(int(self.nitro)) +
            "%",
            True,
            YELLOW
        )
        screen.blit(txt2, (20, 50))

        if self.countdown > 0:

            num = self.countdown // 60 + 1

            if num <= 0:
                msg = "GO!"
            else:
                msg = str(num)

            t = big_font.render(
                msg,
                True,
                YELLOW
            )

            screen.blit(t, (WIDTH // 2 - 40, 70))

        if self.race_over:

            pygame.draw.rect(
                screen,
                (20, 20, 40),
                (250, 250, 460, 180),
                border_radius=18
            )

            t = big_font.render(
                self.result,
                True,
                YELLOW
            )

            screen.blit(
                t,
                (WIDTH // 2 - t.get_width() // 2, 310)
            )

            s = small_font.render(
                "Press R to Restart | ESC to Quit",
                True,
                WHITE
            )

            screen.blit(
                s,
                (WIDTH // 2 - s.get_width() // 2, 380)
            )

    # ---------------- DRAW ----------------
    def draw(self):

        if self.state == "menu":
            self.draw_menu()
            return

        self.draw_bg()

        for c in self.ai:
            self.draw_car(c)

        self.draw_car(self.player)
        self.draw_ui()

    


   
# ---------------- RUN ----------------
    async def run(self):
        running = True
        while running:
            # Crucial for pygbag to yield control to the browser
            await asyncio.sleep(0) 
            
            clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle Mouse/Touch for Web
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                    if self.state == "menu":
                        self.reset()
                        self.state = "game"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    if self.state == "menu":
                        if event.key == pygame.K_LEFT:
                            self.selected_car = (self.selected_car - 1) % len(CAR_COLORS)
                        if event.key == pygame.K_RIGHT:
                            self.selected_car = (self.selected_car + 1) % len(CAR_COLORS)
                        if event.key == pygame.K_RETURN:
                            self.reset()
                            self.state = "game"

            # Only process game logic if we aren't in menu
            if self.state == "game":
                self.handle_input()
                self.update()
            
            self.draw()
            pygame.display.flip()

        pygame.quit()

# ---------------- START ----------------
if __name__ == "__main__":
    asyncio.run(Game().run())