import random
import pygame
import math
class Car:
    def __init__(self, x, y, track_img):
        self.x = x
        self.y = y
        self.vel = 0
        self.angle = 90
        self.img = pygame.image.load("car.png")
        self.front_x = self.x + 16 + 16 * math.sin(math.radians(self.angle))
        self.back_x = self.x + 16 - 16 * math.sin(math.radians(self.angle))
        self.front_y = self.y + 16 + 16 * math.cos(math.radians(self.angle))
        self.back_y = self.y + 16 - 16 * math.cos(math.radians(self.angle))
        self.track_img = track_img
        self.laps = 0
        self.color = "BLACK"
        self.lap_reward = 10
        self.checkpoint_reward = 2

    def move(self):
        self.x = self.x + math.sin(math.radians(self.angle))*self.vel
        self.y = self.y + math.cos(math.radians(self.angle))*self.vel

    def accelerate(self):
        if self.vel < 15:
            self.vel += 0.5

    def decelerate(self):
        if self.vel > 1:
            #print("Decelerating")
            self.vel -= 0.5

    def turn_right(self):
        if self.vel > 0:
            self.angle -= 2 + self.vel*0.3
            if self.angle < 0:
                self.angle += 360

    def turn_left(self):
        if self.vel > 0:
            self.angle += 2 + self.vel*0.3
            if self.angle > 360:
                self.angle -= 360

    def draw(self, win):
        rotated_img = pygame.transform.rotate(self.img, self.angle)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft= (self.x, self.y)).center)
        win.blit(rotated_img, new_rect.topleft)

    def get_ends(self):
        self.front_x = self.x + 16 + 16*math.sin(math.radians(self.angle))
        self.back_x = self.x + 16 - 16*math.sin(math.radians(self.angle))
        self.front_y = self.y + 16 + 16*math.cos(math.radians(self.angle))
        self.back_y = self.y + 16 - 16*math.cos(math.radians(self.angle))
        return self.front_x, self.back_x, self.front_y, self.back_y

    def calc_distance(self, angle):
        r, g, b, d = 0, 0, 0, 0
        while r < 155 or b > 100:
            d += 1
            #print(self.front_x + d * math.sin(math.radians(self.angle)),
             #     self.front_y + d * math.cos(math.radians(self.angle)))
            if self.front_x + d*math.sin(math.radians(self.angle)) > 1920 or self.front_y + d*math.cos(math.radians(self.angle)) > 1080:
                break

            r, g, b, *a = self.track_img.getpixel((self.front_x + d * math.sin(math.radians(self.angle + angle)),
                                              self.front_y + d * math.cos(math.radians(self.angle + angle))))
            #print(r, g, b)
        return d

    def generate_inputs(self):
        inputs = [self.angle]
        for i in range(-90, 135, 45):
            d = self.calc_distance(i)
            inputs.append(d)
        #print(inputs)
        return inputs

    def gain_points(self):
        r, g, b, a = self.track_img.getpixel((self.back_x, self.back_y))
        if g < 150 and b > 180 and self.color == "BLACK":
            self.color = "BLUE"
            return self.checkpoint_reward, False
        elif r > 180 and g > 180 and b > 180 and (self.color == "BLACK" or self.color == "BLUE"):
            self.color = "WHITE"
            self.laps += 1
            return self.lap_reward, "WHITE"
        elif (self.color == "BLUE" or self.color == "WHITE") and (r < 50 and b<50 and g<50):
            #print("Here")
            self.color = "BLACK"
            return self.checkpoint_reward, False
        return 0, False