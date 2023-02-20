import pygame as pg
import random
import pickle
from os import path


pg.init()

clock = pg.time.Clock()
fps = 30
block_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
spikes_group = pg.sprite.Group()
spells_group = pg.sprite.Group()
lava_group = pg.sprite.Group()
coin_group = pg.sprite.Group()
exit_group = pg.sprite.Group()

flip = False
anm = "IDLE"
score = 0
level_score = 0
level = 1
x_distance = 0

font = pg.font.Font("Turok.ttf", 40)

screen_width = 1400
screen_height = 800

screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Adventure")

bg = pg.transform.scale(pg.image.load("Bright/Battleground1.png").convert_alpha(), (screen_width, screen_height))


class Player:
    def __init__(self, x, y, player_num):
        self.x = x
        self.y = y

        self.animation_num = 0
        self.animation = "IDLE"
        self.player_num = player_num
        self.vel_y = 0
        self.jumped = False
        self.attacking = False
        self.rect = pg.Rect(self.x, self.y, 40, 80)
        if self.player_num == 3:
            self.max_hp = 130
        else:
            self.max_hp = 100
        self.hp = self.max_hp
        if self.player_num == 2:
            self.dmg = 10
        else:
            self.dmg = 7

    def update(self, flip, anm):
        if self.jumped:
            anm = "JUMP"
        if self.animation != anm:
            self.animation_num = 0
            self.attacking = False
        self.animation = anm

        self.animation_num += 1
        if self.animation_num > 9 and self.animation == "ATTACK":
            anm = "IDLE"
        if self.animation_num == 7 and self.animation == "ATTACK" and not self.attacking:
            attack = Attack(self.x, self.y, 1, flip, self.dmg)
            attack.update()
            self.attacking = True
        if self.animation_num != 7:
            self.attacking = False
        if self.animation_num > 9:
            self.animation_num = 0
        img = pg.transform.flip(pg.transform.scale(pg.image.load(f"{self.player_num}_KNIGHT/Knight_0{self.player_num}__{self.animation}_00{self.animation_num}.png").convert_alpha(), (300, 160)), flip, False)
        self.rect = pg.Rect(self.x, self.y, 40, 80)

        screen.blit(img, (self.rect.x-130, self.rect.y-30))
        return anm


class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y, type, max_hp, damage):
        super().__init__()
        self.x = x
        self.y = y
        self.type = type
        self.animation_num = 0
        self.flip = False
        self.distance = 0
        self.speed = 6
        self.animation = "Walking"
        self.animation_cap = 17
        self.model = random.randint(1, 3)
        self.seen_player = False
        self.max_hp = max_hp
        self.hp = self.max_hp
        self.damage = damage
        self.vel_y = 0
        self.rect = pg.Rect(self.x, self.y, 40, 80)
        self.walk = 6
        self.follow_player = False
        self.attacking = False
        self.casting = False
        self.spell_cooldown = 0
        if self.type == "Wraith":
            self.animation_cap = 11

    def update(self):
        self.follow_player = False
        dy = 0
        self.vel_y += 1
        if self.vel_y > 20:
            self.vel_y = 20
        dy += self.vel_y

        for block in block_group:
            # check for collision in x direction
            if self.flip:
                if block.rect.colliderect(self.x - 15, self.y, 40, 80):
                    self.speed = 0
                    self.walk *= -1
                    self.distance = 0
                    if self.walk > 0:
                        self.flip = False
                    else:
                        self.flip = True
            if not self.flip:
                if block.rect.colliderect(self.x + 15, self.y, 40, 80):
                    self.speed = 0
                    self.walk *= -1
                    self.distance = 0
                    if self.walk > 0:
                        self.flip = False
                    else:
                        self.flip = True

        for block in block_group:
            # check for collision in y direction
            if block.rect.colliderect(self.rect.x, self.rect.y + dy, 40, 80):

                if self.vel_y > 0:
                    dy = block.rect.top - self.rect.bottom
                    self.vel_y = 0

        self.y += dy

        if self.animation == "Dying" and self.animation_num == 14:
            pass
        else:
            self.animation_num += 1
            if self.animation_num > self.animation_cap:
                self.animation_num = 0
                if self.animation == "Casting Spells":
                    self.animation = "Walking"
                    self.animation_num = 0
                    self.animation_cap = 11
                if self.animation == "Attacking":
                    self.animation = "Walking"
                if self.animation == "Idle":
                    self.animation = "Walking"
                if self.hp <= 0:
                    self.animation = "Dying"
                    self.animation_num = 0
                    self.animation_cap = 14

        # attack
        if self.spell_cooldown > 0:
            self.spell_cooldown -= 1
        if self.animation == "Casting Spells" and self.animation_num == 11 and not self.casting:
            spell = Fireball(self.x, self.y, self.flip)
            spells_group.add(spell)
            self.casting = True
        if self.animation == "Casting Spells" and self.animation_num == 12:
            self.casting = False
        if self.animation == "Attacking" and self.animation_num == 8 and not self.attacking:
            attack = Attack(self.x, self.y, 0, self.flip, self.damage)
            attack.update()
            self.attacking = True
        if self.animation == "Attacking" and self.animation_num == 9:
            self.attacking = False
        if self.animation != "Attacking" and self.animation != "Dying" and self.animation != "Casting Spells":
            if 0 < self.x - player.x < 350 and self.flip and self.spell_cooldown == 0 and self.type == "Wraith" or 0 < self.x - player.x < 350 and self.spell_cooldown == 0 and self.type == "Wraith":
                if -60 < abs(player.y - self.y) < 60 or -60 < abs(self.y - player.y) < 60:
                    self.animation = "Casting Spells"
                    self.spell_cooldown = 100
                    self.animation_cap = 17
                    self.animation_num = 0
            if 0 < self.x - player.x < 60 and self.flip and (-60 < abs(player.y - self.y) < 60 or -60 < abs(self.y - player.y) < 60):
                self.animation = "Attacking"
                self.animation_cap = 11
                self.animation_num = 0
            elif 0 < player.x - self.x < 60 and not self.flip and (-60 < abs(player.y - self.y) < 60 or -60 < abs(self.y - player.y) < 60):
                self.animation = "Attacking"
                self.animation_cap = 11
                self.animation_num = 0
            else:
                # checking if player is close
                if 0 < self.x - player.x < 350 and self.flip or 0 < self.x - player.x < 150 or 0 < self.x - player.x < 350 and self.seen_player:
                    if -60 < abs(player.y - self.y) < 60 or -60 < abs(self.y - player.y) < 60:
                        self.x -= self.speed*2
                        self.flip = True
                        self.seen_player = True
                        self.follow_player = True
                elif 0 < player.x - self.x < 350 and not self.flip or 0 < player.x - self.x < 150 or 0 < player.x - self.x < 350 and self.seen_player:
                    if -60 < abs(player.y - self.y) < 60 or -60 < abs(self.y - player.y) < 60:
                        self.x += self.speed*2
                        self.flip = False
                        self.seen_player = True
                        self.follow_player = True
                if not self.follow_player:
                    if self.animation != "Idle":
                        idle = random.randint(0, 30)
                        if idle == 10:
                            # idle
                            self.animation = "Idle"
                            self.animation_cap = 11
                            self.animation_num = 0
                    # walking
                    if self.animation == "Walking":

                        if self.distance < 150:
                            self.distance += abs(self.walk)
                            self.x += self.walk
                        else:
                            self.distance = 0
                            self.walk *= -1
                            if self.walk > 0:
                                self.flip = False
                            else:
                                self.flip = True

        self.speed = 4
        img = pg.transform.flip(pg.transform.scale(pg.image.load(f"{self.type}{self.model}/{self.animation}/{self.type}_0{self.model}_{self.animation}_00{self.animation_num}.png").convert_alpha(), (135, 97)), self.flip, False)
        self.rect = pg.Rect(self.x, self.y, 40, 80)

        if self.type == "Satyr" or self.type == "Wraith" or self.type == "Fallen_Angels":
            screen.blit(img, (self.rect.x - 45, self.rect.y + 5))
        else:
            screen.blit(img, (self.rect.x - 45, self.rect.y - 10))


class Fireball(pg.sprite.Sprite):
    def __init__(self, x, y, flip):
        super().__init__()
        self.x = x
        self.y = y
        self.flip = flip
        self.image = pg.transform.scale(pg.image.load("laserRedBurst.png").convert_alpha(), (20, 20))
        if self.flip:
            self.rect = pg.Rect(self.x, self.y + 30, 20, 20)
        else:
            self.rect = pg.Rect(self.x + 40, self.y + 30, 20, 20)

    def update(self):
        if self.flip:
            self.rect.x -= 12
        else:
            self.rect.x += 12
        if pg.Rect.colliderect(self.rect, player.rect):
            player.hp -= 10
            self.kill()
        for block in block_group:
            if pg.Rect.colliderect(self.rect, block.rect):
                self.kill()
        if 0 < self.rect.x < 1400:
            pass
        else:
            self.kill()
        screen.blit(self.image, self.rect)


class Attack(pg.sprite.Sprite):
    def __init__(self, x, y, attacker, flip, damage):
        super().__init__()
        self.x = x
        self.y = y
        self.attacker = attacker
        self.flip = flip
        self.damage = damage

    def update(self):
        if self.flip:
            if self.attacker == 1 and player.player_num == 1:
                self.rect = pg.Rect(self.x - 65, self.y, 65, 100)
            else:
                self.rect = pg.Rect(self.x-50, self.y, 65, 100)
            if self.attacker != 1:
                if pg.Rect.colliderect(self.rect, player.rect):
                    player.hp -= self.damage
            else:
                for enemy in enemy_group:
                    if pg.Rect.colliderect(self.rect, enemy.rect):
                        if enemy.hp > 0:
                            enemy.hp -= player.dmg
                            health_bar(enemy.hp, enemy.max_hp, enemy.x, enemy.y)
            self.kill()

        else:
            if self.attacker == 1 and player.player_num == 1:
                self.rect = pg.Rect(self.x + 35, self.y, 65, 100)
            else:
                self.rect = pg.Rect(self.x+25, self.y, 65, 100)
            if self.attacker != 1:
                if pg.Rect.colliderect(self.rect, player.rect):
                    player.hp -= self.damage
            else:
                for enemy in enemy_group:
                    if pg.Rect.colliderect(self.rect, enemy.rect):
                        if enemy.hp > 0:
                            enemy.hp -= player.dmg
                            health_bar(enemy.hp, enemy.max_hp, enemy.x, enemy.y)
            self.kill()


class Button:
    def __init__(self, x, y, x_size, y_size):
        self.rect = pg.Rect((x, y), (x_size, y_size))
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self, x, y):
        action = False
        pos = pg.mouse.get_pos()
        if self.rect.collidepoint(pos):
            pg.draw.rect(screen, (255, 100, 100), self.rect, 0, 30)
            if pg.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action


class Block(pg.sprite.Sprite):
    def __init__(self, x, y, img, x_move, y_move):
        super().__init__()
        self.img = img
        self.x = x
        self.y = y
        self.x_move = x_move
        self.y_move = y_move
        self.move = 5
        self.move_dist = 0
        if self.x_move == 0 and self.y_move == 0:
            self.rect = pg.Rect(self.x, self.y, 50, 50)
        else:
            self.rect = pg.Rect(self.x, self.y, 50, 25)

    def update(self):
        if self.x_move != 0 or self.y_move != 0:
            if self.move_dist >= 50:
                self.move *= -1
                self.move_dist = 0
            self.rect.x += self.move * self.x_move
            self.rect.y += self.move * self.y_move
            self.move_dist += abs(self.move)
        screen.blit(self.img, self.rect)


class Spikes(pg.sprite.Sprite):
    def __init__(self, x, y, flip):
        super().__init__()
        self.flip = flip
        self.image = pg.transform.flip(pg.transform.scale(pg.image.load("spikes.png").convert_alpha(), (50, 80)), False, self.flip)
        self.rect = pg.Rect(x, y, 50, 50)
        self.rect.x = x
        self.rect.y = y
        self.cooldown = 0
        self.move = 0
        self.way = 1
        if self.flip:
            self.way *= -1

    def update(self, x, y):
        self.rect = pg.Rect(x, y, 50, 50)
        self.rect.x = x
        self.rect.y = y
        for enemy in enemy_group:
            if pg.sprite.spritecollide(enemy, lava_group, False):
                enemy.hp -= 1
        if self.cooldown <= 0:
            self.rect.y += self.way
            self.move += 1
        else:
            self.cooldown -= 1
        if self.move >= 50:
            self.cooldown = 70
            self.way *= -1
            self.move = 0
        if not self.flip:
            screen.blit(self.image, (self.rect.x, self.rect.y-30))
        else:
            screen.blit(self.image, (self.rect.x, self.rect.y))


class Lava(pg.sprite.Sprite):
    def __init__(self, x, y, falling):
        super().__init__()
        self.falling = falling
        if not self.falling:
            self.image = pg.transform.scale(pg.image.load("liquidLavaTop_mid.png").convert_alpha(), (50, 50))
        else:
            self.image = pg.transform.scale(pg.image.load("liquidLava.png").convert_alpha(), (50, 50))
        self.rect = pg.Rect(x, y, 50, 50)
        self.rect.x = x
        self.rect.y = y

    def update(self, x, y):
        self.rect = pg.Rect(x, y, 50, 50)
        for enemy in enemy_group:
            if pg.sprite.spritecollide(enemy, lava_group, False):
                enemy.hp -= 5
                if enemy.animation == "Dying" and enemy.animation_num == 14:
                    enemy.kill()
        if not self.falling:
            screen.blit(self.image, (self.rect.x, self.rect.y-20))
        else:
            screen.blit(self.image, (self.rect.x, self.rect.y))


class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.transform.scale(pg.image.load("coinGold.png").convert_alpha(), (20, 20))
        self.rect = pg.Rect(x, y, 20, 20)
        self.rect.x = x
        self.rect.y = y

    def update(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Exit(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.transform.scale(pg.image.load("signExit.png").convert_alpha(), (50, 50))
        self.rect = pg.Rect(x, y, 50, 50)
        self.rect.x = x
        self.rect.y = y

    def update(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class World:
    def __init__(self, data):
        #load images
        dirt_img = pg.transform.scale(pg.image.load('blocks/dirt.png').convert_alpha(), (50, 50))
        grass_img = pg.transform.scale(pg.image.load('blocks/dirtCenter.png').convert_alpha(), (50, 50))
        small_img = pg.transform.scale(pg.image.load("blocks/dirtHalf.png").convert_alpha(), (50, 25))

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    block = Block(col_count*50, row_count*50, grass_img, 0, 0)
                    block_group.add(block)
                if tile == 2:
                    block = Block(col_count * 50, row_count * 50, dirt_img, 0, 0)
                    block_group.add(block)
                if tile == 3:
                    spikes = Spikes(col_count * 50, row_count * 50, False)
                    spikes_group.add(spikes)
                if tile == 4:
                    spikes = Spikes(col_count * 50, row_count * 50, True)
                    spikes_group.add(spikes)
                if tile == 5:
                    enemy1 = Enemy(col_count * 50, row_count * 50 - 55, "Wraith", random.randint(15, 25), random.randint(4, 6))
                    enemy_group.add(enemy1)
                if tile == 6:
                    enemy2 = Enemy(col_count * 50, row_count * 50 - 55, "Minotaur", random.randint(25, 35), random.randint(7, 10))
                    enemy_group.add(enemy2)
                if tile == 7:
                    enemy3 = Enemy(col_count * 50, row_count * 50 - 55, "Satyr", random.randint(20, 30), random.randint(6, 8))
                    enemy_group.add(enemy3)
                if tile == 8:
                    enemy4 = Enemy(col_count * 50, row_count * 50 - 55, "Reaper_Man", random.randint(20, 30), random.randint(8, 12))
                    enemy_group.add(enemy4)
                if tile == 9:
                    enemy5 = Enemy(col_count * 50, row_count * 50 - 55, "Fallen_Angels", random.randint(30, 40), random.randint(9, 13))
                    enemy_group.add(enemy5)
                if tile == 10:
                    lava = Lava(col_count * 50, row_count * 50 + 20, False)
                    lava_group.add(lava)
                if tile == 11:
                    coin = Coin(col_count * 50 + 15, row_count * 50 + 15)
                    coin_group.add(coin)
                if tile == 12:
                    exit = Exit(col_count * 50, row_count * 50)
                    exit_group.add(exit)
                if tile == 13:
                    block = Block(col_count*50, row_count*50, small_img, 1, 0)
                    block_group.add(block)
                if tile == 14:
                    block = Block(col_count*50, row_count*50, small_img, 0, 1)
                    block_group.add(block)
                if tile == 15:
                    block = Block(col_count*50, row_count*50, small_img, -1, 0)
                    block_group.add(block)
                if tile == 16:
                    block = Block(col_count*50, row_count*50, small_img, 0, -1)
                    block_group.add(block)
                if tile == 17:
                    block = Block(col_count*50, row_count*50, small_img, 1, 1)
                    block_group.add(block)
                if tile == 18:
                    block = Block(col_count*50, row_count*50, small_img, -1, 1)
                    block_group.add(block)
                if tile == 19:
                    lava = Lava(col_count * 50, row_count * 50, True)
                    lava_group.add(lava)
                col_count += 1
            row_count += 1


def game_start():
    button1 = Button(100, 150, 300, 400)
    button2 = Button(550, 150, 300, 400)
    button3 = Button(1000, 150, 300, 400)
    not_started = True
    num = 0
    while not_started:
        pg.display.update()
        if num > 9:
            num = 0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
        screen.blit(pg.transform.scale(pg.image.load("Layers/2.png").convert_alpha(), (screen_width, screen_height)), (0, 0))
        if button1.draw(button1.rect.x, button1.rect.y):
            player = 1
            not_started = False
        screen.blit(pg.transform.scale(pg.image.load(f"1_KNIGHT/Knight_01__IDLE_00{num}.png").convert_alpha(), (1080, 700)), (-330, 50))
        pg.draw.rect(screen, (255, 100, 100), (100, 650, 300, 60), 0, 30)
        draw_text("longer range", font, (255, 250, 250), 135, 650)
        if button2.draw(button1.rect.x, button1.rect.y):
            player = 2
            not_started = False
        screen.blit(pg.transform.scale(pg.image.load(f"2_KNIGHT/Knight_02__IDLE_00{num}.png").convert_alpha(), (1080, 700)), (110, 50))
        pg.draw.rect(screen, (255, 100, 100), (550, 650, 300, 60), 0, 30)
        draw_text("more damage", font, (255, 250, 250), 590, 650)
        if button3.draw(button1.rect.x, button1.rect.y):
            player = 3
            not_started = False
        screen.blit(pg.transform.scale(pg.image.load(f"3_KNIGHT/Knight_03__IDLE_00{num}.png").convert_alpha(), (1080, 700)), (570, 50))
        pg.draw.rect(screen, (255, 100, 100), (1000, 650, 300, 60), 0, 30)
        draw_text("higher health", font, (255, 250, 250), 1032, 650)
        draw_text("CHOOSE YOUR WARRIOR", (pg.font.Font("Turok.ttf", 50+num*2)), (255, 255-num*16, 255-num*16), 450-num*5, 70)
        num += 1
    return player


def health_bar(hp, max_hp, x, y):
    color1 = round(255/max_hp*hp)
    color2 = 255-color1
    if color1 < 0:
        color1 = 0
    if color2 < 0:
        color2 = 0
    if color1 > 255:
        color1 = 255
    if color2 > 255:
        color2 = 255
    pg.draw.rect(screen, (0, 0, 0), pg.Rect(x-30, y-30, 2*max_hp+6, 36))
    pg.draw.rect(screen, (color2, color1, 0), pg.Rect(x-27, y-27, 2*hp, 30))


scroll = 0
bg_images = [pg.transform.scale(pg.image.load(f"Layers/{i}.png").convert_alpha(), (screen_width + 100, screen_height)) for i in range(2, 9)]
"""for i in range(1, 9):
   bg_image = pg.transform.scale(pg.image.load(f"Layers/{i}.png").convert_alpha(), (screen_width, screen_height))
   bg_images.append(bg_image)"""


def draw_bg():
    for x in range(7):
        speed = 1
        for i in bg_images:
           screen.blit(i, (((x-1) * screen_width) - scroll * speed, 0))
           speed += 0.1


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def restart_level(score, level_score):
    score -= level_score
    block_group.empty()
    enemy_group.empty()
    spikes_group.empty()
    spells_group.empty()
    lava_group.empty()
    coin_group.empty()
    exit_group.empty()
    player = Player(700, 350, player_num)
    world = World(world_data)
    x_distance = 0
    return player, world, x_distance, score


def next_level(level):
    level += 1
    block_group.empty()
    enemy_group.empty()
    spikes_group.empty()
    spells_group.empty()
    lava_group.empty()
    coin_group.empty()
    exit_group.empty()
    player = Player(700, 350, player_num)
    if path.exists(f"world_data{level}.pkl"):
        pickle_in = open(f"world_data{level}.pkl", "rb")
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    x_distance = 0
    return player, world, x_distance


"""world_data = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0,11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 7, 0, 0,11, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,11, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 3, 0, 0, 0, 0, 2, 0, 6, 0, 0, 0, 3, 0, 4, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0,11, 0, 6, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0,11, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0],
[2, 5, 0,11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0],
[1, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 2,10,10,10,10,10,10,10,10, 2, 0, 0,11, 0, 5, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 6, 0, 0, 2, 3, 3, 3, 3, 3, 3, 2, 0, 0, 6, 0, 7, 0, 2, 1, 1,10,10,10,10,10,10,10,10,10,10, 1, 2, 0, 0, 0, 7, 6, 0,11,12, 0, 0],
[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
]"""

if path.exists(f"world_data{level}.pkl"):
    pickle_in = open(f"world_data{level}.pkl", "rb")
    world_data = pickle.load(pickle_in)
world = World(world_data)


dx = 0
player_num = game_start()
player = Player(700, 400, player_num)
#world = World(world_data)

run = True

while run:
    clock.tick(fps)
    #screen.blit(bg, (0, 0))
    draw_bg()

    for exit in exit_group:
        if pg.Rect.colliderect(player.rect, exit.rect):
            player, world, x_distance = next_level(level)
            level_score = 0

    if player.hp <= 0:
        player, world, x_distance, score = restart_level(score, level_score)
        level_score = 0

    dy = 0
    dx = 0

    if anm != "ATTACK":
        anm = "IDLE"
    key = pg.key.get_pressed()
    if key[pg.K_UP] and not player.jumped:
        player.vel_y = -11
        player.jumped = True
        anm = "JUMP"
    if key[pg.K_SPACE]:
        anm = "ATTACK"
    elif key[pg.K_LEFT]:
        dx = 10
        flip = True
        anm = "RUN"
    elif key[pg.K_RIGHT]:
        dx = -10
        flip = False
        anm = "RUN"

    player.vel_y += 1
    if player.vel_y > 0:
        fall = 1
    else:
        fall = -1
    dy += ((player.vel_y + 4*fall)**2) * 0.2 * fall

    for block in block_group:
        # check for collision in x direction
        if block.rect.colliderect(player.x - dx, player.y, 40, 80):
            dx = 0

    if 0 <= x_distance <= 2900:
        x_distance -= dx
    else:
        if 0 < player.x and dx > 0:
            x_distance -= dx
            player.x -= dx
        elif player.x < 1360 and dx < 0:
            x_distance -= dx
            player.x -= dx
        dx = 0
    for enemy in enemy_group:
        if enemy.animation != "Dying":
            if enemy.rect.colliderect(player.x - dx, player.y, 40, 80):
                dx = 0
        enemy.update()
        enemy.x += dx
    for coin in coin_group:
        coin.update()
        coin.rect.x += dx
        if pg.Rect.colliderect(coin.rect, player.rect):
            score += 1
            level_score += 1
            coin.kill()
    for exit in exit_group:
        exit.update()
        exit.rect.x += dx
    for spell in spells_group:
        spell.update()
        spell.rect.x += dx
    for spikes in spikes_group:
        spikes.update(spikes.rect.x, spikes.rect.y)
        spikes.rect.x += dx
        if pg.Rect.colliderect(spikes.rect, player.rect):
            player.hp -= 5
    for lava in lava_group:
        lava.update(lava.rect.x, lava.rect.y)
        lava.rect.x += dx
        if pg.Rect.colliderect(lava.rect, player.rect):
            player.hp -= 10

    for block in block_group:
        block.update()
        block.rect.x += dx
    for block in block_group:
        # check for collision in y direction
        if block.rect.colliderect(player.rect.x, player.rect.y + dy, 40, 80):
            # check for jumping
            if player.vel_y < 0:
                dy = block.rect.bottom - player.rect.top
                player.vel_y = 0
            # check for falling
            elif player.vel_y > 0:
                dy = block.rect.top - player.rect.bottom
                player.x += block.move * block.x_move
                if player.vel_y > 15:
                    player.hp -= player.vel_y
                player.vel_y = 0
                player.jumped = False

    if scroll > 0:
        scroll += dx/5
    if scroll < 6000:
        scroll += dx/5

    dx = 0
    player.y += dy

    if player.rect.bottom > screen_height:
        player.rect.bottom = screen_height
        dy = 0

    anm = player.update(flip, anm)

    health_bar(player.hp, player.max_hp, 60, 60)
    draw_text(f"score: {score}", font, (255, 250, 250), 1200, 20)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    pg.display.update()

pg.quit()