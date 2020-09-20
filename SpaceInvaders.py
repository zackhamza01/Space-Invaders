import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 650, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

#Ship images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))

#Player Ship image
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#Lasers
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#Background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

#Music
music = pygame.mixer.music.load("mainmusic.mp3")
pygame.mixer.music.play(-1)

#SoundEffect
enemykilled = pygame.mixer.Sound("enemykilled.wav")
playerlaser = pygame.mixer.Sound("playerlaser.wav")
enemylaser = pygame.mixer.Sound("enemylaser.wav")

#Laser class
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

#Ship class
class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            if laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            playerlaser.play()

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

#Player class
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.shotenemy = False

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        enemykilled.play()
                        self.shotenemy = True
                        if laser not in self.lasers:
                            continue
                        else:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

#Enemy Class
class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        laser = Laser(int(self.x - self.get_width() / 4), self.y, self.laser_img)
        if not(laser.off_screen(HEIGHT)):
            enemylaser.play()
        self.lasers.append(laser)
        self.cool_down_counter = 1


def collide(obj1, obj2): #Checks if an object collides with another object
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,  (offset_x, offset_y)) != None

def main():
    #Setting game attributes
    run = True
    fps = 60
    level = 0
    lives = 5
    points = 0
    main_font = pygame.font.SysFont("comicsans", 50)
    gamover_font = pygame.font.SysFont("comicsans", 60)
    levelup_font = pygame.font.SysFont("comicsans", 50)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 500)

    clock = pygame.time.Clock()

    gameover = False
    gameover_count = 0

    def redraw_window(): #Redrawing the window every frame
        WIN.blit(BACKGROUND, (0,0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        points_label = main_font.render(f"Points: {points}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH-level_label.get_width()-10, 10))
        WIN.blit(points_label, (WIDTH/2-points_label.get_width()/2, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if gameover:
            gameover_label = gamover_font.render("GAME OVER", 1, (255,0,0))
            WIN.blit(gameover_label, (WIDTH/2-gameover_label.get_width()/2, HEIGHT/2 + 20))

        pygame.display.update()
    while run:
        clock.tick(fps)
        redraw_window()

        def levelupscreen():
            level_up_count = 0
            levelup_label = levelup_font.render("Level Up!", 1, (255,255,255))
            WIN.blit(levelup_label, (WIDTH/2-levelup_label.get_width()/2, HEIGHT/2))
            while level_up_count < fps*3:
                level_up_count += 1
                WIN.blit(levelup_label, (WIDTH / 2 - levelup_label.get_width() / 2, HEIGHT / 2))



        points += 1

        if lives <= 0 or player.health <= 0:
            gameover = True
            gameover_count += 1

        if gameover:
            if gameover_count > fps * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            #levelupscreen()
            player.health = 100
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1300, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: #Goes left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: #Goes right
            player.x += player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 20 < HEIGHT: #Goes down
            player.y += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0 : #Goes up
            player.y -= player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*fps) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                enemykilled.play()
                points += 100

            if player.shotenemy:
                points += 100
                player.shotenemy = False

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
                points -= 100



        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    firsttime = True
    while run:
        if firsttime:
            WIN.blit(BACKGROUND, (0,0))
            title_label = title_font.render("Welcome to Space Invaders!", 1, (255,255,255))
            title_label2 = title_font.render("Press any key to begin.", 1, (255,255,255))
            WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 200))
            WIN.blit(title_label2, (WIDTH/2-title_label2.get_width()/2, 500))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    firsttime = False
                    main()

        else:
            WIN.blit(BACKGROUND, (0, 0))
            title_label = title_font.render("Press any key to start again.", 1, (255, 255, 255))
            WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    main()


    pygame.quit()

main_menu()