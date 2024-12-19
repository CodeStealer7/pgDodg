import random
import pygame as pg

pg.init()

OKNO_SIRKA = 800
OKNO_VYSKA = 600

BILA = (255, 255, 255)
CERNA = (0, 0, 0)

okno = pg.display.set_mode((OKNO_SIRKA, OKNO_VYSKA))
pg.display.set_caption("shooter")

hodiny = pg.time.Clock()
FPS = 60

score_font = pg.font.Font("freesansbold.ttf", 32)

# Event definitions for spawning coins and game over
SPAWN_ENEMY_EVENT = pg.USEREVENT + 1
SPAWN_KAZDYCH_X = 2
pg.time.set_timer(SPAWN_ENEMY_EVENT, SPAWN_KAZDYCH_X * 1000)

GAME_OVER_EVENT = pg.USEREVENT + 2
GAME_OVER_X = 20
pg.time.set_timer(GAME_OVER_EVENT, GAME_OVER_X * 1000)

ULTIMATE_CHARGE_EVENT = pg.USEREVENT + 3
ULTIMATE_CHARGE_SEC = 5
pg.time.set_timer(ULTIMATE_CHARGE_EVENT, ULTIMATE_CHARGE_SEC * 1000)


class GameObject(pg.sprite.Sprite):
    def __init__(self, x, y, rychlost, obrazek, scale=1):
        super().__init__()
        self.image = pg.image.load(obrazek)
        self.image = pg.transform.scale(
            self.image,
            (int(self.image.get_width() * scale), int(self.image.get_height() * scale)),
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rychlost = rychlost


class Hrac(GameObject):
    def __init__(self, x, y, rychlost, obrazek, scale):
        super().__init__(x, y, rychlost, obrazek, scale)
        self.skore = 0

    def update(self):
        self.pohyb()
        self.zkontroluj_hranice()

    def pohyb(self):
        keys = pg.key.get_pressed()
        move_x = 0
        move_y = 0

        if keys[pg.K_LEFT]:
            move_x = -self.rychlost
        if keys[pg.K_RIGHT]:
            move_x = self.rychlost
        if keys[pg.K_UP]:
            move_y = -self.rychlost
        if keys[pg.K_DOWN]:
            move_y = self.rychlost

        self.rect.x += move_x
        self.rect.y += move_y

    def zkontroluj_hranice(self):
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > OKNO_SIRKA - self.rect.width:
            self.rect.x = OKNO_SIRKA - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > OKNO_VYSKA - self.rect.height:
            self.rect.y = OKNO_VYSKA - self.rect.height


class Enemy1(GameObject):
    def __init__(self, x, y, obrazek, scale):
        super().__init__(x, y, 5, obrazek, scale)

    def update(self):
        self.rect.x -= self.rychlost
        if self.rect.right < 0:
            self.rect.left = OKNO_SIRKA


class Enemy2(GameObject):
    def __init__(self, x, y, obrazek, scale):
        super().__init__(x, y, 5, obrazek, scale)

    def update(self):
        self.rect.x += self.rychlost
        if self.rect.left > OKNO_SIRKA:
            self.rect.right = 0


class Enemy3(GameObject):
    def __init__(self, x, y, obrazek, scale):
        super().__init__(x, y, 5, obrazek, scale)

    def update(self):
        self.rect.y -= self.rychlost
        if self.rect.bottom < 0:
            self.rect.top = OKNO_VYSKA


class Enemy4(GameObject):
    def __init__(self, x, y, obrazek, scale):
        super().__init__(x, y, 5, obrazek, scale)

    def update(self):
        self.rect.y += self.rychlost
        if self.rect.top > OKNO_VYSKA:
            self.rect.bottom = 0


class Strela(GameObject):
    def __init__(self, x, y, obrazek, scale):
        super().__init__(x, y, 10, obrazek, scale)

    def update(self):
        self.rect.x += self.rychlost
        if self.rect.left > OKNO_SIRKA:
            self.kill()


def game_over_screen(skore):
    game_over_font = pg.font.Font("freesansbold.ttf", 50)
    score_text = score_font.render(f"Skóre: {skore}", True, CERNA)
    game_over_text = game_over_font.render("Game Over", True, CERNA)

    okno.fill(BILA)
    okno.blit(game_over_text, (OKNO_SIRKA // 2 - game_over_text.get_width() // 2, OKNO_VYSKA // 3))
    okno.blit(score_text, (OKNO_SIRKA // 2 - score_text.get_width() // 2, OKNO_VYSKA // 2))


# Initialize the player and enemies
def restart_game():
    player = Hrac(OKNO_SIRKA // 10, OKNO_VYSKA // 2, 5, "sprites/zbran.png", 1)

    hrac_group = pg.sprite.Group()
    hrac_group.add(player)

    strela_group = pg.sprite.Group()

    enemy_group = pg.sprite.Group()

    return player, hrac_group, enemy_group, strela_group


player, hrac_group, enemy_group, strela_group = restart_game()

enemy_count = 0  # Initialize the enemy count
game_over = False  # Add a flag to track game over state

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == SPAWN_ENEMY_EVENT:
            # Randomly choose an enemy type and spawn from different sides
            enemy_type = random.choice([Enemy1, Enemy2, Enemy3, Enemy4])
            if enemy_type == Enemy1:
                pos_x = random.randint(OKNO_SIRKA - 50, OKNO_SIRKA)
                pos_y = random.randint(0, OKNO_VYSKA - 50)
            elif enemy_type == Enemy2:
                pos_x = random.randint(-50, 0)
                pos_y = random.randint(0, OKNO_VYSKA - 50)
            elif enemy_type == Enemy3:
                pos_x = random.randint(0, OKNO_SIRKA - 50)
                pos_y = random.randint(OKNO_VYSKA, OKNO_VYSKA + 50)
            else:  # Enemy4
                pos_x = random.randint(0, OKNO_SIRKA - 50)
                pos_y = random.randint(-50, 0)

            enemy = enemy_type(pos_x, pos_y, "sprites/enemy.png", 2)
            enemy_group.add(enemy)
            enemy_count += 1

            pg.time.set_timer(ULTIMATE_CHARGE_EVENT, ULTIMATE_CHARGE_SEC * 1000)

        if event.type == pg.KEYDOWN and event.key == pg.K_u:
            pocet_enemy = len(enemy_group)
            player.skore += 1
            enemy_group.empty()
            pg.time.set_timer(ULTIMATE_CHARGE_EVENT, ULTIMATE_CHARGE_SEC * 1000)

        if event.type == ULTIMATE_CHARGE_EVENT:
            can_use_u = True

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                pos_1x = player.rect.x
                pos_1y = player.rect.y
                strela = Strela(pos_1x, pos_1y, "sprites/strela.png", 2)
                strela_group.add(strela)

        if event.type == GAME_OVER_EVENT:
            game_over = True  # Set the game over flag to True

    if pg.sprite.spritecollide(player, enemy_group, True):
        game_over = True  # Set the game over flag to True
        print("Zemřel jsi!")

    if game_over:
        # Show the game over screen
        game_over_screen(player.skore)
        pg.display.flip()  # Update display
        pg.time.wait(2000)  # Wait for 2 seconds to show the game over screen
        running = False  # End the game loop

    # Main game logic (only runs if the game is not over)
    if not game_over:
        hrac_group.update()
        enemy_group.update()
        strela_group.update()

        collisions = pg.sprite.groupcollide(strela_group, enemy_group, True, True)
        if collisions:
            player.skore += 1
            print("Už daleko nedojdeš chlapečku!")

        okno.fill(BILA)
        hrac_group.draw(okno)
        enemy_group.draw(okno)
        strela_group.draw(okno)

        # Display the score and enemy count
        skore_text = score_font.render(f"Skóre: {player.skore}", True, CERNA)
        enemy_count_text = score_font.render(f"Enemies: {enemy_count}", True, CERNA)
        okno.blit(skore_text, (10, 10))
        okno.blit(enemy_count_text, (10, 50))  # Display enemy count below score

        pg.display.flip()
    hodiny.tick(FPS)

pg.quit()
