import pygame as pg
import random


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