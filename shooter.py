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

GAME_OVER_EVENT = pg.USEREVENT + 2  # Changed to a unique event ID for game over
GAME_OVER_X = 50
pg.time.set_timer(GAME_OVER_EVENT, GAME_OVER_X * 1000)


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
        self.rychlost = rychlost
        self.skore = 0

    def update(self):
        self.pohyb()
        self.zkontroluj_hranice()

    def pohyb(self):
        keys = pg.key.get_pressed()
        move_x = 0
        move_y = 0

        if keys[pg.K_LEFT]:
            move_x = 0
        if keys[pg.K_RIGHT]:
            move_x = 0
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


class Enemy(GameObject):
    def __init__(self, x, y, obrazek, scale):
        super().__init__(x, y, 0, obrazek, scale) #musí tam byt rychlost ty kokotko!! uz si na to dvakrat zapomněl

    def update(self, enemy_speed=5):
            self.rect.x -= enemy_speed  # Move the enemy to the left

            # z leva projede znovu do prava
            if self.rect.right < 0:
                self.rect.left = OKNO_SIRKA

class Strela(GameObject):
    def __init__(self, x, y, obrazek, scale):
        super().__init__(x, y, 0, obrazek, scale) #musí tam byt rychlost ty kokotko!! uz si na to dvakrat zapomněl

    def update(self, strela_speed=50):
            self.rect.x += strela_speed

            if self.rect.left > OKNO_SIRKA:
                self.kill()            # offscreen = vymyzaní


def game_over_screen(skore):
    game_over_font = pg.font.Font("freesansbold.ttf", 50)
    score_text = score_font.render(f"Skóre: {skore}", True, CERNA)
    game_over_text = game_over_font.render("Game Over", True, CERNA)

    okno.fill(BILA)
    okno.blit(game_over_text, (OKNO_SIRKA // 2 - game_over_text.get_width() // 2, OKNO_VYSKA // 3))
    okno.blit(score_text, (OKNO_SIRKA // 2 - score_text.get_width() // 2, OKNO_VYSKA // 2))


# Initialize the player and enemies
def restart_game():
    # Create the player centered in the screen
    player = Hrac(OKNO_SIRKA // 10, OKNO_VYSKA // 2, 5 , "sprites/zbran.png", 1) #obcas se obrazek nevykreslí kvuli scalingu

    # Create the groups again
    hrac_group = pg.sprite.Group()
    hrac_group.add(player)

    strela_group = pg.sprite.Group()

    enemy_group = pg.sprite.Group()


    return player, hrac_group, enemy_group, strela_group


player, hrac_group, enemy_group, strela_group = restart_game()


strela_spawned = False

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == SPAWN_ENEMY_EVENT:
            pos_x = random.randint(OKNO_SIRKA - 50, OKNO_SIRKA)
            pos_y = random.randint(0, OKNO_VYSKA - 50)
            enemy = Enemy(pos_x, pos_y, "sprites/enemy.png", 2)
            enemy_group.add(enemy)

        if event.type == pg.KEYDOWN:
            # kontrola zmacnuti mezerníku
            if event.key == pg.K_SPACE:
                pos_1x = player.rect.x
                pos_1y = player.rect.y
                strela = Strela(pos_1x, pos_1y, "sprites/strela.png", 2)
                strela_group.add(strela)
                strela_spawned = True  # Set the flag to prevent multiple spawns
                print("Bang!")

        if event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                strela_spawned = False

        if event.type == GAME_OVER_EVENT:
            game_over_screen(player.skore)  # Display the game over screen
            running = False  # End the game loop after showing the game over screen

    hrac_group.update()
    enemy_group.update()
    strela_group.update()
    
    if pg.sprite.spritecollide(player, enemy_group, True):
        running = False
        print("Zemřel jsi!")

    # kolize mezi (strela_group) a enemies (enemy_group)
    collisions = pg.sprite.groupcollide(strela_group, enemy_group, True, True)
    if collisions:
        player.skore += 1
        print("Už daleko nedojdeš chlapečku!")

    okno.fill(BILA)
    hrac_group.draw(okno)
    enemy_group.draw(okno)
    strela_group.draw(okno)
    skore_text = score_font.render(f"Skóre: {player.skore}", True, CERNA)
    okno.blit(skore_text, (10, 10))

    pg.display.flip()
    hodiny.tick(FPS)

pg.quit()