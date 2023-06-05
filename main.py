import pygame as pg
import random
import pickle
from os import path
from pygame import mixer


pg.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pg.init()

clock = pg.time.Clock()
fps = 20
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
level = 5
x_distance = 0
deaths = 0
enemies_killed = 0
save_cooldown = 0

font = pg.font.Font("Turok.ttf", 40)
big_font = pg.font.Font("Turok.ttf", 70)
small_font = pg.font.Font("Turok.ttf", 20)
very_big_font = pg.font.Font("Turok.ttf", 150)

screen_width = 1400
screen_height = 800

screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Adventure")

bg = pg.transform.scale(pg.image.load("images/Layers/bgimage.jpg").convert_alpha(), (screen_width, screen_height))


#Sounds
pg.mixer.music.load("sounds/music.mp3")
pg.mixer.music.set_volume(0.5)
weapon_sounds = [pg.mixer.Sound("sounds/mixkit-fast-sword-whoosh-2792.wav"), pg.mixer.Sound("sounds/mixkit-metal-hit-woosh-1485.wav"), pg.mixer.Sound("sounds/mixkit-sword-strikes-armor-2765.wav"), pg.mixer.Sound("sounds/mixkit-boxing-punch-2051.wav"), pg.mixer.Sound("sounds/mixkit-cartoon-punch-2149.wav"), pg.mixer.Sound("sounds/mixkit-weak-hit-impact-2148.wav")]
enemy_death_sound = [pg.mixer.Sound("sounds/mixkit-creature-cry-of-hurt-2208.wav"), pg.mixer.Sound("sounds/mixkit-wild-beast-roar-12.wav"), pg.mixer.Sound("sounds/mixkit-exclamation-of-pain-from-a-zombie-2207.wav"), pg.mixer.Sound("sounds/mixkit-cartoon-fail-blow-fart-3053.wav"), pg.mixer.Sound("sounds/mixkit-fantasy-monster-grunt-1977.wav"), pg.mixer.Sound("sounds/mixkit-angry-beast-roar-1728.wav"), pg.mixer.Sound("sounds/mixkit-monster-dying-in-pain-1960.wav"), pg.mixer.Sound("sounds/mixkit-cartoon-girl-saying-no-no-no-2257.wav"), pg.mixer.Sound("sounds/mixkit-lost-kid-sobbing-474.wav")]
player_death_sound = [pg.mixer.Sound("sounds/mixkit-man-in-pain-2197.wav"), pg.mixer.Sound("sounds/mixkit-farting-doubt-male-laugh-3054.wav"), pg.mixer.Sound("sounds/mixkit-male-falling-scream-392.wav")]
lava_sound = pg.mixer.Sound("sounds/mixkit-big-volcano-lava-bubble-burst-2448.wav")
fall_sound = pg.mixer.Sound("sounds/mixkit-quest-game-heavy-stomp-v-3049.wav")
starting_sound = pg.mixer.Sound("sounds/mixkit-atmospheric-prelude-drum-roll-569.wav")
spell_explosion_sound = pg.mixer.Sound("sounds/mixkit-fast-game-explosion-1688.wav")
spell_casting_sound = pg.mixer.Sound("sounds/mixkit-vacuum-swoosh-transition-1465.wav")
coin_sound = pg.mixer.Sound("sounds/mixkit-happy-bell-alert-601.wav")


class Player:
    def __init__(self, x, y, player_num, weapon, shield):
        self.x = x
        self.y = y
        self.animation_num = 0
        self.animation = "IDLE"
        self.player_num = player_num
        self.vel_y = 0
        self.jumped = False
        self.attacking = False
        self.weapon = weapon
        self.shield = shield
        self.rect = pg.Rect(self.x, self.y, 40, 80)
        self.all_animations = [[pg.transform.scale(pg.image.load(f"images/{self.player_num}_KNIGHT/Knight_0{self.player_num}__IDLE_00{i}.png").convert_alpha(), (300, 160)) for i in range(0, 10)], [pg.transform.scale(pg.image.load(f"images/{self.player_num}_KNIGHT/Knight_0{self.player_num}__RUN_00{i}.png").convert_alpha(), (300, 160)) for i in range(0, 10)], [pg.transform.scale(pg.image.load(f"images/{self.player_num}_KNIGHT/Knight_0{self.player_num}__ATTACK_00{i}.png").convert_alpha(), (300, 160)) for i in range(0, 10)], [pg.transform.scale(pg.image.load(f"images/{self.player_num}_KNIGHT/Knight_0{self.player_num}__JUMP_00{i}.png").convert_alpha(), (300, 160)) for i in range(0, 10)], [pg.transform.scale(pg.image.load(f"images/{self.player_num}_KNIGHT/Knight_0{self.player_num}__DIE_00{i}.png").convert_alpha(), (300, 160)) for i in range(0, 10)]]
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
            weapon_sounds[random.randint(0, 2)].play()
            attack = Attack(self.x, self.y, 1, flip, self.dmg)
            attack.update()
            self.attacking = True
        if self.animation_num != 7:
            self.attacking = False
        if self.animation_num > 9 and anm != "DIE":
            self.animation_num = 0
        if anm == "DIE" and self.animation_num >= 9:
            self.animation_num = 9
        if anm == "IDLE":
            img = pg.transform.flip(self.all_animations[0][self.animation_num], flip, False)
        elif anm == "RUN":
            img = pg.transform.flip(self.all_animations[1][self.animation_num], flip, False)
        elif anm == "ATTACK":
            img = pg.transform.flip(self.all_animations[2][self.animation_num], flip, False)
        elif anm == "JUMP":
            img = pg.transform.flip(self.all_animations[3][self.animation_num], flip, False)
        else:
            img = pg.transform.flip(self.all_animations[4][self.animation_num], flip, False)

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
            self.all_animations = [[pg.transform.scale(pg.image.load(f"images/{self.type}{self.model}/Idle/{self.type}_0{self.model}_Idle_00{i}.png").convert_alpha(), (135, 97)) for i in range(0, 12)], [pg.transform.scale(pg.image.load(f"images/{self.type}{self.model}/Walking/{self.type}_0{self.model}_Walking_00{i}.png").convert_alpha(), (135, 97)) for i in range(0, 12)], [pg.transform.scale(pg.image.load(f"images/{self.type}{self.model}/Attacking/{self.type}_0{self.model}_Attacking_00{i}.png").convert_alpha(), (135, 97)) for i in range(0, 12)], [pg.transform.scale(pg.image.load(f"images/{self.type}{self.model}/Dying/{self.type}_0{self.model}_Dying_00{i}.png").convert_alpha(), (135, 97)) for i in range(0, 15)], [pg.transform.scale(pg.image.load(f"images/{self.type}{self.model}/Casting Spells/{self.type}_0{self.model}_Casting Spells_00{i}.png").convert_alpha(), (135, 97)) for i in range(0, 18)]]
        elif self.type == "Fallen_Angels":
            self.all_animations = [[pg.transform.scale(pg.image.load(
                f"images/{self.type}{self.model}/Idle/{self.type}_0{self.model}_Idle_00{i}.png").convert_alpha(),
                                                       (135, 97)) for i in range(0, 12)], [pg.transform.scale(
                pg.image.load(
                    f"images/{self.type}{self.model}/Walking/{self.type}_0{self.model}_Walking_00{i}.png").convert_alpha(),
                (135, 97)) for i in range(0, 18)], [pg.transform.scale(pg.image.load(
                f"images/{self.type}{self.model}/Attacking/{self.type}_0{self.model}_Attacking_00{i}.png").convert_alpha(),
                                                                       (135, 97)) for i in range(0, 12)], [
                                       pg.transform.scale(pg.image.load(
                                           f"images/{self.type}{self.model}/Dying/{self.type}_0{self.model}_Dying_00{i}.png").convert_alpha(),
                                                          (135, 97)) for i in range(0, 15)], [pg.transform.scale(
                pg.image.load(
                    f"images/{self.type}{self.model}/Casting Spells/{self.type}_0{self.model}_Casting Spells_00{i}.png").convert_alpha(),
                (135, 97)) for i in range(0, 12)]]

        else:
            self.all_animations = [[pg.transform.scale(pg.image.load(
                f"images/{self.type}{self.model}/Idle/{self.type}_0{self.model}_Idle_00{i}.png").convert_alpha(),
                                                       (135, 97)) for i in range(0, 12)], [pg.transform.scale(
                pg.image.load(
                    f"images/{self.type}{self.model}/Walking/{self.type}_0{self.model}_Walking_00{i}.png").convert_alpha(),
                (135, 97)) for i in range(0, 18)], [pg.transform.scale(pg.image.load(
                f"images/{self.type}{self.model}/Attacking/{self.type}_0{self.model}_Attacking_00{i}.png").convert_alpha(),
                                                                       (135, 97)) for i in range(0, 12)], [
                                       pg.transform.scale(pg.image.load(
                                           f"images/{self.type}{self.model}/Dying/{self.type}_0{self.model}_Dying_00{i}.png").convert_alpha(),
                                                          (135, 97)) for i in range(0, 15)]]

    def update(self, enemies_killed):
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

            # check for collision in y direction
            if block.rect.colliderect(self.rect.x, self.rect.y + dy, 40, 80) and self.animation != "Dying":

                if self.vel_y > 0:
                    dy = block.rect.top - self.rect.bottom
                    self.vel_y = 0

        if self.animation != "Dying":
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
                    if self.type == "Fallen_Angels":
                        player_death_sound[random.randint(0, 2)].play()
                    elif self.type == "Wraith":
                        enemy_death_sound[random.randint(6, 8)].play()
                    else:
                        enemy_death_sound[random.randint(0, 5)].play()
                    enemies_killed += 1
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
        if self.animation == "Casting Spells" and self.animation_num == 11:
            self.casting = False
        if self.animation == "Attacking" and self.animation_num == 8 and not self.attacking:
            attack = Attack(self.x, self.y, 0, self.flip, self.damage)
            attack.update()
            self.attacking = True
        if self.animation == "Attacking" and self.animation_num == 9:
            self.attacking = False
        if self.animation != "Attacking" and self.animation != "Dying" and self.animation != "Casting Spells":
            if 0 < self.x - player.x < 350 and self.flip and self.spell_cooldown == 0 and self.x > player.x and (self.type == "Wraith" or self.type == "Fallen_Angels") or 0 < self.x - player.x < 350 and self.spell_cooldown == 0 and self.x < player.x and (self.type == "Wraith" or self.type == "Fallen_Angels"):
                if abs(player.y - self.y) < 60 or abs(self.y - player.y) < 60 and self.seen_player:
                    self.animation = "Casting Spells"
                    spell_casting_sound.play()
                    self.spell_cooldown = 100
                    if self.type == "Wraith":
                        self.animation_cap = 17
                    else:
                        self.animation_cap = 11
                    self.animation_num = 0
            if 0 < self.x - player.x < 60 and self.flip and (abs(player.y - self.y) < 60 or abs(self.y - player.y) < 60):
                if self.type == "Fallen_Angels":
                    weapon_sounds[random.randint(0, 2)].play()
                else:
                    weapon_sounds[random.randint(3, 4)].play()
                self.animation = "Attacking"
                self.animation_cap = 11
                self.animation_num = 0
            elif 0 < player.x - self.x < 60 and not self.flip and (-60 < abs(player.y - self.y) < 60 or -60 < abs(self.y - player.y) < 60):
                if self.type == "Fallen_Angels":
                    weapon_sounds[random.randint(0, 2)].play()
                else:
                    weapon_sounds[random.randint(3, 4)].play()
                self.animation = "Attacking"
                self.animation_cap = 11
                self.animation_num = 0
            else:
                # checking if player is close
                if 0 < self.x - player.x < 350 and self.flip or 0 < self.x - player.x < 150 or 0 < self.x - player.x < 350 and self.seen_player:
                    if abs(player.y - self.y) < 60 or abs(self.y - player.y) < 60:
                        self.x -= self.speed*2
                        self.flip = True
                        self.seen_player = True
                        self.follow_player = True
                elif 0 < player.x - self.x < 350 and not self.flip or 0 < player.x - self.x < 150 or 0 < player.x - self.x < 350 and self.seen_player:
                    if abs(player.y - self.y) < 60 or abs(self.y - player.y) < 60:
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
                            if self.walk > 0:
                                self.flip = False
                            else:
                                self.flip = True
                        else:
                            self.distance = 0
                            self.walk *= -1
                            if self.walk > 0:
                                self.flip = False
                            else:
                                self.flip = True

        self.speed = 4
        if self.animation == "Idle":
            img = pg.transform.flip(self.all_animations[0][self.animation_num], self.flip, False)
        elif self.animation == "Walking":
            img = pg.transform.flip(self.all_animations[1][self.animation_num], self.flip, False)
        elif self.animation == "Attacking":
            img = pg.transform.flip(self.all_animations[2][self.animation_num], self.flip, False)
        elif self.animation == "Dying":
            img = pg.transform.flip(self.all_animations[3][self.animation_num], self.flip, False)
        else:
            img = pg.transform.flip(self.all_animations[4][self.animation_num], self.flip, False)
        #img = pg.transform.flip(pg.transform.scale(pg.image.load(f"images/{self.type}{self.model}/{self.animation}/{self.type}_0{self.model}_{self.animation}_00{self.animation_num}.png").convert_alpha(), (135, 97)), self.flip, False)
        self.rect = pg.Rect(self.x, self.y, 40, 80)


        if self.type == "Satyr" or self.type == "Wraith" or self.type == "Fallen_Angels":
            screen.blit(img, (self.rect.x - 45, self.rect.y + 5))
        else:
            screen.blit(img, (self.rect.x - 45, self.rect.y - 10))
        return enemies_killed


class Fireball(pg.sprite.Sprite):
    def __init__(self, x, y, flip):
        super().__init__()
        self.x = x
        self.y = y
        self.flip = flip
        self.image = pg.transform.scale(pg.image.load("images/laserRedBurst.png").convert_alpha(), (20, 20))
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
            spell_explosion_sound.play()
            self.kill()
        for block in block_group:
            if pg.Rect.colliderect(self.rect, block.rect):
                spell_explosion_sound.play()
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
                    player.hp -= self.damage - player.shield
            else:
                for enemy in enemy_group:
                    if pg.Rect.colliderect(self.rect, enemy.rect):
                        if enemy.hp > 0:
                            enemy.hp -= player.dmg + player.weapon
                            health_bar(enemy.hp, enemy.max_hp, enemy.x, enemy.y)

                for block in block_group:
                    if block.box:
                        if pg.Rect.colliderect(self.rect, block.rect):
                            chance = random.randint(1, 2)
                            if chance == 1:
                                player.hp += 25
                            elif chance == 2:
                                enemy1 = Enemy(block.rect.x + 10, block.rect.y, "Wraith", random.randint(15, 25),
                                               random.randint(5, 7))
                                enemy_group.add(enemy1)
                            block.kill()

            self.kill()

        else:
            if self.attacker == 1 and player.player_num == 1:
                self.rect = pg.Rect(self.x + 35, self.y, 65, 100)
            else:
                self.rect = pg.Rect(self.x+25, self.y, 65, 100)
            if self.attacker != 1:
                if pg.Rect.colliderect(self.rect, player.rect):
                    player.hp -= self.damage - player.shield
            else:
                for enemy in enemy_group:
                    if pg.Rect.colliderect(self.rect, enemy.rect):
                        if enemy.hp > 0:
                            enemy.hp -= player.dmg + player.weapon
                            health_bar(enemy.hp, enemy.max_hp, enemy.x, enemy.y)

                for block in block_group:
                    if block.box:
                        if pg.Rect.colliderect(self.rect, block.rect):
                            chance = random.randint(1, 2)
                            if chance == 1:
                                player.hp += 25
                            elif chance == 2:
                                enemy1 = Enemy(block.rect.x + 10, block.rect.y, "Wraith", random.randint(15, 25),
                                               random.randint(5, 7))
                                enemy_group.add(enemy1)
                            block.kill()
            self.kill()


class Button:
    def __init__(self, x, y, x_size, y_size):
        self.rect = pg.Rect((x, y), (x_size, y_size))
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
        self.mouse_on = False

    def draw(self):
        action = False
        pos = pg.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.mouse_on = True
            pg.draw.rect(screen, (255, 100, 100), self.rect, 0, 30)
            if pg.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True
        else:
            self.mouse_on = False

        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action


class Block(pg.sprite.Sprite):
    def __init__(self, x, y, img, x_move, y_move, box, broken):
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
        self.box = box
        self.broken = broken
        if self.broken:
            self.hp = 30

    def update(self):
        if self.x_move != 0 or self.y_move != 0:
            if self.move_dist >= 100:
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
        self.image = pg.transform.flip(pg.transform.scale(pg.image.load("images/spikes.png").convert_alpha(), (50, 80)), False, self.flip)
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
            if pg.sprite.spritecollide(enemy, spikes_group, False):
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
            self.image = pg.transform.scale(pg.image.load("images/liquidLavaTop_mid.png").convert_alpha(), (50, 50))
        else:
            self.image = pg.transform.scale(pg.image.load("images/liquidLava.png").convert_alpha(), (50, 50))
        self.rect = pg.Rect(x, y, 50, 50)
        self.rect.x = x
        self.rect.y = y

    def update(self, x, y):
        self.rect = pg.Rect(x, y, 50, 50)
        for enemy in enemy_group:
            if pg.sprite.spritecollide(enemy, lava_group, False):
                enemy.hp -= 5
                lava_sound.play()
                if enemy.animation == "Dying" and enemy.animation_num == 14:
                    enemy.kill()
        if not self.falling:
            screen.blit(self.image, (self.rect.x, self.rect.y-20))
        else:
            screen.blit(self.image, (self.rect.x, self.rect.y))


class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.transform.scale(pg.image.load("images/coinGold.png").convert_alpha(), (20, 20))
        self.rect = pg.Rect(x, y, 20, 20)
        self.rect.x = x
        self.rect.y = y

    def update(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Exit(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.transform.scale(pg.image.load("images/signExit.png").convert_alpha(), (50, 50))
        self.rect = pg.Rect(x, y, 50, 50)
        self.rect.x = x
        self.rect.y = y

    def update(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class World:
    def __init__(self, data):
        #load images
        dirt_img = pg.transform.scale(pg.image.load('images/blocks/dirt.png').convert_alpha(), (50, 50))
        grass_img = pg.transform.scale(pg.image.load('images/blocks/dirtCenter.png').convert_alpha(), (50, 50))
        small_img = pg.transform.scale(pg.image.load("images/blocks/dirtHalf.png").convert_alpha(), (50, 25))
        box_img = pg.transform.scale(pg.image.load("images/blocks/boxItem.png").convert_alpha(), (50, 50))
        brokendirt_img = pg.transform.scale(pg.image.load("images/blocks/brokendirt.png").convert_alpha(), (50, 50))

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 0:
                    pass
                elif tile == 1:
                    block = Block(col_count*50, row_count*50, grass_img, 0, 0, False, False)
                    block_group.add(block)
                elif tile == 2:
                    block = Block(col_count * 50, row_count * 50, dirt_img, 0, 0, False, False)
                    block_group.add(block)
                elif tile == 3:
                    spikes = Spikes(col_count * 50, row_count * 50, False)
                    spikes_group.add(spikes)
                elif tile == 4:
                    spikes = Spikes(col_count * 50, row_count * 50, True)
                    spikes_group.add(spikes)
                elif tile == 5:
                    enemy1 = Enemy(col_count * 50, row_count * 50 - 55, "Wraith", random.randint(15, 25), random.randint(5, 7))
                    enemy_group.add(enemy1)
                elif tile == 6:
                    enemy2 = Enemy(col_count * 50, row_count * 50 - 55, "Minotaur", random.randint(25, 35), random.randint(8, 11))
                    enemy_group.add(enemy2)
                elif tile == 7:
                    enemy3 = Enemy(col_count * 50, row_count * 50 - 55, "Satyr", random.randint(20, 30), random.randint(7, 8))
                    enemy_group.add(enemy3)
                elif tile == 8:
                    enemy4 = Enemy(col_count * 50, row_count * 50 - 55, "Reaper_Man", random.randint(20, 30), random.randint(8, 12))
                    enemy_group.add(enemy4)
                elif tile == 9:
                    enemy5 = Enemy(col_count * 50, row_count * 50 - 55, "Fallen_Angels", random.randint(30, 40), random.randint(9, 14))
                    enemy_group.add(enemy5)
                elif tile == 10:
                    lava = Lava(col_count * 50, row_count * 50 + 20, False)
                    lava_group.add(lava)
                elif tile == 11:
                    coin = Coin(col_count * 50 + 15, row_count * 50 + 15)
                    coin_group.add(coin)
                elif tile == 12:
                    exit = Exit(col_count * 50, row_count * 50)
                    exit_group.add(exit)
                elif tile == 13:
                    block = Block(col_count*50, row_count*50, small_img, 1, 0, False, False)
                    block_group.add(block)
                elif tile == 14:
                    block = Block(col_count*50, row_count*50, small_img, 0, 1, False, False)
                    block_group.add(block)
                elif tile == 15:
                    block = Block(col_count*50, row_count*50, small_img, -1, 0, False, False)
                    block_group.add(block)
                elif tile == 16:
                    block = Block(col_count*50, row_count*50, small_img, 0, -1, False, False)
                    block_group.add(block)
                elif tile == 17:
                    block = Block(col_count*50, row_count*50, small_img, 1, 1, False, False)
                    block_group.add(block)
                elif tile == 18:
                    block = Block(col_count*50, row_count*50, small_img, -1, 1, False, False)
                    block_group.add(block)
                elif tile == 19:
                    lava = Lava(col_count * 50, row_count * 50, True)
                    lava_group.add(lava)
                elif tile == 20:
                    block = Block(col_count*50, row_count*50, box_img, 0, 0, True, False)
                    block_group.add(block)
                elif tile == 21:
                    block = Block(col_count*50, row_count*50, brokendirt_img, 0, 0, False, True)
                    block_group.add(block)
                col_count += 1
            row_count += 1


def menu():
    button1 = Button(550, 450, 300, 70)
    button2 = Button(550, 550, 300, 70)
    button3 = Button(550, 650, 300, 70)
    not_started = True
    run = True
    continue_game = False
    images = [pg.transform.scale(pg.image.load(f"images/1_KNIGHT/Knight_01__JUMP_006.png").convert_alpha(), (1620, 1050)), pg.transform.flip(pg.transform.scale(pg.image.load(f"images/2_KNIGHT/Knight_02__ATTACK_003.png").convert_alpha(), (1620, 1050)), True, False), pg.transform.flip(pg.transform.scale(pg.image.load(f"images/3_KNIGHT/Knight_03__ATTACK_005.png").convert_alpha(), (1620, 1050)), True, False)]
    bg = (pg.transform.scale(pg.image.load("images/Layers/redbg.jpg").convert_alpha(), (screen_width, screen_height)))
    starting_sound.play()
    while not_started:
        clock.tick(20)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
        screen.blit(bg, (0, 0))
        screen.blit(images[0], (-550, 100))
        screen.blit(images[1], (-100, -50))
        screen.blit(images[2], (350, 0))
        draw_text("Adventure", very_big_font, (255, 255, 255), 355, 80)
        if button1.draw():
            not_started = False
        pg.draw.rect(screen, (255, 150, 150), (555, 455, 290, 60), 0, 30)
        draw_text("START GAME", font, (255, 250, 250), 595, 460)
        if button2.draw():
            continue_game = True
            not_started = False
        pg.draw.rect(screen, (255, 150, 150), (555, 555, 290, 60), 0, 30)
        draw_text("CONTINUE", font, (255, 250, 250), 625, 560)
        if button3.draw():
            run = False
            not_started = False
        pg.draw.rect(screen, (255, 150, 150), (555, 655, 290, 60), 0, 30)
        draw_text("EXIT GAME", font, (255, 250, 250), 610, 660)
        pg.display.update()
    return run, continue_game


def game_start():
    button1 = Button(100, 150, 300, 400)
    button2 = Button(550, 150, 300, 400)
    button3 = Button(1000, 150, 300, 400)
    controls_button = Button(1250, 40, 80, 80)
    not_started = True
    num = 0
    knights_animations = [[pg.transform.scale(pg.image.load(f"images/1_KNIGHT/Knight_01__IDLE_00{i}.png").convert_alpha(), (1080, 700)) for i in range(0, 10)], [pg.transform.scale(pg.image.load(f"images/2_KNIGHT/Knight_02__IDLE_00{i}.png").convert_alpha(), (1080, 700)) for i in range(0, 10)], [pg.transform.scale(pg.image.load(f"images/3_KNIGHT/Knight_03__IDLE_00{i}.png").convert_alpha(), (1080, 700)) for i in range(0, 10)], [pg.transform.scale(pg.image.load(f"images/1_KNIGHT/Knight_01__ATTACK_00{i}.png").convert_alpha(), (1080, 700)) for i in range(0, 10)], [pg.transform.scale(pg.image.load(f"images/2_KNIGHT/Knight_02__ATTACK_00{i}.png").convert_alpha(), (1080, 700)) for i in range(0, 10)], [pg.transform.scale(pg.image.load(f"images/3_KNIGHT/Knight_03__ATTACK_00{i}.png").convert_alpha(), (1080, 700)) for i in range(0, 10)]]
    bg = (pg.transform.scale(pg.image.load("images/Layers/redbg.jpg").convert_alpha(), (screen_width, screen_height)))
    control = False
    while not_started:
        clock.tick(15)
        pg.display.update()
        if num > 9:
            num = 0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
        screen.blit(bg, (0, 0))
        if not control:
            if button1.draw():
                player = 1
                not_started = False
            if button1.mouse_on:
                screen.blit(knights_animations[3][num], (-330, 50))
            else:
                screen.blit(knights_animations[0][num], (-330, 50))
            pg.draw.rect(screen, (255, 100, 100), (100, 650, 300, 60), 0, 30)
            draw_text("longer range", font, (255, 250, 250), 135, 650)
            if button2.draw():
                player = 2
                not_started = False
            if button2.mouse_on:
                screen.blit(knights_animations[4][num], (120, 50))
            else:
                screen.blit(knights_animations[1][num], (120, 50))
            pg.draw.rect(screen, (255, 100, 100), (550, 650, 300, 60), 0, 30)
            draw_text("more damage", font, (255, 250, 250), 590, 650)
            if button3.draw():
                player = 3
                not_started = False
            pg.draw.rect(screen, (255, 150, 150), (1255, 45, 70, 70), 0, 30)
            draw_text("?", big_font, (255, 250, 250), 1278, 40)
            if button3.mouse_on:
                screen.blit(knights_animations[5][num], (570, 50))
            else:
                screen.blit(knights_animations[2][num], (570, 50))
            pg.draw.rect(screen, (255, 100, 100), (1000, 650, 300, 60), 0, 30)
            draw_text("higher health", font, (255, 250, 250), 1032, 650)
            draw_text("CHOOSE YOUR WARRIOR", (pg.font.Font("Turok.ttf", 50+num*2)), (255, 255-num*16, 255-num*16), 450-num*5, 70)
            num += 1
        else:
            draw_text("CONTROLS", big_font, (255, 250, 250), 600, 100)
            draw_text("move left - arrow left", font, (255, 250, 250), 120, 200)
            draw_text("move right - arrow right", font, (255, 250, 250), 120, 270)
            draw_text("jump - w", font, (255, 250, 250), 120, 340)
            draw_text("attack - space", font, (255, 250, 250), 120, 410)
            draw_text("pause - p", font, (255, 250, 250), 120, 480)
            draw_text("unpause - i", font, (255, 250, 250), 120, 550)
            pg.draw.rect(screen, (255, 150, 150), (1255, 45, 70, 70), 0, 30)
            draw_text("<-", big_font, (255, 250, 250), 1270, 31)
        if controls_button.draw():
            if not control:
                control = True
            else:
                control = False

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
bg_images = [pg.transform.scale(pg.image.load(f"images/Layers/{i}.png").convert_alpha(), (screen_width + 100, screen_height)) for i in range(2, 9)]

def draw_bg():
    for x in range(7):
        speed = 1
        for i in bg_images:
           screen.blit(i, (((x-1) * screen_width) - scroll * speed, 0))
           speed += 0.1


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def restart_level(score, level_score, world_data):
    score = level_score
    block_group.empty()
    enemy_group.empty()
    spikes_group.empty()
    spells_group.empty()
    lava_group.empty()
    coin_group.empty()
    exit_group.empty()
    player = Player(700, 350, player_num, weapon, shield)
    world = World(world_data)
    x_distance = 0
    pg.mixer.music.play(-1)
    return player, world, x_distance, score


def next_level(level, world_data, score, level_score):
    level_score = score
    block_group.empty()
    enemy_group.empty()
    spikes_group.empty()
    spells_group.empty()
    lava_group.empty()
    coin_group.empty()
    exit_group.empty()
    player = Player(700, 350, player_num, weapon, shield)
    if path.exists(f"world_data{level}.pkl"):
        pickle_in = open(f"world_data{level}.pkl", "rb")
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    x_distance = 0
    return player, world, x_distance, world_data, level_score


def pause(run, num, deaths, enemies_killed, weapon, shield, score, hp, max_hp):
    pg.mixer.music.fadeout(3000)
    game_paused = True
    heart_image = pg.transform.scale(pg.image.load("images/blocks/heart.png"), (100, 100))
    sword_imgs = [pg.transform.scale(pg.image.load("images/blocks/sword1.png").convert_alpha(), (100, 100)), pg.transform.scale(pg.image.load("images/blocks/sword2.png").convert_alpha(), (100, 100)), pg.transform.scale(pg.image.load("images/blocks/sword3.png").convert_alpha(), (100, 100))]
    shield_imgs = [pg.transform.scale(pg.image.load("images/blocks/shield1.png").convert_alpha(), (100, 100)), pg.transform.scale(pg.image.load("images/blocks/shield2.png").convert_alpha(), (100, 100)), pg.transform.scale(pg.image.load("images/blocks/shield3.png").convert_alpha(), (100, 100))]
    coin_image = pg.transform.scale(pg.image.load("images/coinGold.png").convert_alpha(), (40, 40))
    bg_pause = pg.transform.scale(pg.image.load("images/Layers/redbg.jpg").convert_alpha(), (screen_width, screen_height))
    player_image = pg.transform.scale(pg.image.load(f"images/{num}_KNIGHT/Knight_0{num}__IDLE_000.png").convert_alpha(), (1080, 700))
    sword_button = Button(1000, 450, 100, 100)
    shield_button = Button(1000, 300, 100, 100)
    heart_button = Button(1000, 600, 100, 100)
    check = 5
    while game_paused:
        if check > 0:
            check -= 1
        key = pg.key.get_pressed()
        for event in pg.event.get():

            if event.type == pg.QUIT:
                game_paused = False
                run = False
        if key[pg.K_i] and check == 0:
            game_paused = False

        screen.blit(bg_pause, (0, 0))
        screen.blit(player_image, (-350, 150))
        if shield < 3:
            screen.blit(shield_imgs[shield], (1000, 300))
            draw_text("-1 damage received = 20", small_font, (255, 250, 250), 1120, 330)
            screen.blit(coin_image, (1320, 320))
            if shield_button.draw():
                screen.blit(shield_imgs[shield], (1000, 300))
                if score >= 20:
                    score -= 20
                    shield += 1
                    coin_sound.play()

        if weapon < 3:
            screen.blit(sword_imgs[weapon], (1000, 450))
            draw_text("-1 damage received = 20", small_font, (255, 250, 250), 1120, 480)
            screen.blit(coin_image, (1320, 470))
            if sword_button.draw():
                screen.blit(sword_imgs[weapon], (1000, 450))
                if score >= 20:
                    score -= 20
                    weapon += 1
                    coin_sound.play()

        screen.blit(heart_image, (1000, 575))
        draw_text("25hp healed = 3", small_font, (255, 250, 250), 1120, 630)
        screen.blit(coin_image, (1320, 620))
        if heart_button.draw():
            if score >= 3:
                hp += 25
                score -= 3
                coin_sound.play()
                if hp > max_hp:
                    hp = max_hp

        health_bar(hp, max_hp, 60, 60)

        pg.draw.rect(screen, (255, 100, 100), (460, 150, 440, 90), 0, 30)
        draw_text("GAME PAUSED", big_font, (255, 250, 250), (screen_width // 2) - 220, (screen_height // 2) - 250)
        pg.draw.rect(screen, (255, 100, 100), (480, 420, 260, 50), 0, 30)
        draw_text(f"score: {score}", font, (255, 250, 250), 500, 420)
        pg.draw.rect(screen, (255, 100, 100), (480, 500, 260, 50), 0, 30)
        draw_text(f"deaths: {deaths}", font, (255, 250, 250), 500, 500)
        pg.draw.rect(screen, (255, 100, 100), (480, 580, 370, 50), 0, 30)
        draw_text(f"enemies killed: {enemies_killed}", font, (255, 250, 250), 500, 580)
        pg.display.update()
    pg.mixer.music.play(-1)
    return run, weapon, shield, score, hp

paused = False
dead = False
restart_button = Button(550, 375, 300, 100)
dx = 0
weapon, shield = 0, 0

run, continue_game = menu()
if not continue_game:
    if run:
        player_num = game_start()
    player = Player(700, 400, player_num, weapon, shield)
else:
    if path.exists("saved_level.dat"):
        saves = pickle.load(open("saved_level.dat", "rb"))
        level, level_score, weapon, shield, player_num = saves[0], saves[1], saves[2], saves[3], saves[4]
        player = Player(700, 400, player_num, weapon, shield)
    else:
        player_num = game_start()
        player = Player(700, 400, player_num, weapon, shield)

score = level_score
if path.exists(f"world_data{level}.pkl"):
    pickle_in = open(f"world_data{level}.pkl", "rb")
    world_data = pickle.load(pickle_in)
world = World(world_data)
pg.mixer.music.play(-1)

while run:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    #draw_bg()
    if player.y > screen_width:
        player.hp = 0

    if paused:
        run, player.weapon, player.shield, score, player.hp = pause(run, player.player_num, deaths, enemies_killed, player.weapon, player.shield, score, player.hp, player.max_hp)
    paused = False

    for exit in exit_group:
        if pg.Rect.colliderect(player.rect, exit.rect):
            weapon = player.weapon
            shield = player.shield
            level += 1
            player, world, x_distance, world_data, level_score = next_level(level, world_data, score, level_score)
            dead = False
            anm = "IDLE"

    dy = 0
    dx = 0

    if anm != "ATTACK":
        if anm != "DIE":
            anm = "IDLE"
    key = pg.key.get_pressed()
    if anm != "DIE":
        if key[pg.K_p]:
            paused = True

        if key[pg.K_u]:
            if save_cooldown == 0:
                saves = [level, level_score, weapon, shield, player.player_num]
                pickle.dump(saves, open("saved_level.dat", "wb"))
                save_cooldown = 100

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


    for enemy in enemy_group:
        if enemy.animation != "Dying":
            if enemy.rect.colliderect(player.x - dx, player.y, 40, 80):
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
        enemies_killed = enemy.update(enemies_killed)
        enemy.x += dx

    for coin in coin_group:
        coin.update()
        coin.rect.x += dx
        if pg.Rect.colliderect(coin.rect, player.rect):
            score += 1
            coin_sound.play()
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
            if not dead:
                lava_sound.play()
                player.hp -= 10

    player.jumped = True
    for block in block_group:
        block.update()
        block.rect.x += dx
    for block in block_group:
        # check for collision in y direction
        if block.rect.colliderect(player.rect.x, player.rect.y + dy + 5, 40, 80):
            if block.broken:
                block.hp -= 1
                if block.hp <= 0:
                    block.kill()
            # check for jumping
            if player.vel_y < 0:
                dy = block.rect.bottom - player.rect.top
                player.vel_y = 0
            # check for falling
            elif player.vel_y > 0:
                dy = block.rect.top - player.rect.bottom
                player.x += block.move * block.x_move
                if player.vel_y > 15:
                    fall_sound.play()
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

    if player.hp <= 0:
        anm = "DIE"
        if not dead:
            deaths += 1
            pg.mixer.music.fadeout(4000)
            player_death_sound[random.randint(0, 2)].play()
            dead = True
        if restart_button.draw():
            anm = "IDLE"
            dead = False
            player, world, x_distance, score = restart_level(score, level_score, world_data)
            level_score = 0
        pg.draw.rect(screen, (225, 100, 100), (560, 385, 280, 80), 0, 30)
        draw_text("RESTART", font, (255, 250, 250), 625, 400)

    health_bar(player.hp, player.max_hp, 60, 60)
    draw_text(f"score: {score}", font, (255, 250, 250), 1200, 20)

    if save_cooldown > 0:
        draw_text("GAME SAVED", font, (255, 255, 255), (screen_width - 220), (screen_height - 100))
        save_cooldown -= 1

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    pg.display.update()

pg.quit()