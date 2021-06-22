import os.path
import random
import pickle
import neat
import pygame
from PIL import Image
from car import Car
pygame.font.init()
# importing all pictures
filename = "background8.png"
trackpx = Image.open(filename)
BG_IMG = pygame.image.load(filename)
window = pygame.display.set_mode((trackpx.size[0], trackpx.size[1]))
# initialising the font
font = pygame.font.SysFont("comicsans", 50)
gen = 0

class Track:
    def __init__(self):
        self.size = trackpx.size[0], trackpx.size[1]
        self.track = Image.open("background8.png")
        self.gen = 0

    def collide(self, car):
        # Getting the pixel in the front and back of the car, then looking if it's red or green pixel and if true
        # return True
        front_x, back_x, front_y, back_y = car.get_ends()
        r, g, b, *a = self.track.getpixel((front_x, front_y))
        r2, g2, b2, *a= self.track.getpixel((back_x, back_y))
        #print(self.track.getpixel((front_x, front_y)))
        if (r>155 and b<100) or (r2>155 and b2<100) or (g>155 and b<100) or (g2>155 and b<100):
            #print("Collided: , "+ str(r) + "  " + str(g) + "  " + str(b))
            if r<50 and b<50 and g<50:
                return False
            return True
        #print("Not collided")

    def draw(self, win):
        # draws track on window
        win.blit(self.track, (0, 0))


def draw_screen(screen, cars, BG_IMG, generation, lap_count, seconds, cars_len):
    # Drawing all of the window, using the draw methods of the Track and Car class and then drawing all info that's
    # wanted, so Generation, Time, Laps, and the Cars Alive
    screen.blit(BG_IMG, (0, 0))
    for car in cars:
        car.draw(screen)
        """front_x, back_x, front_y, back_y = car.get_ends()
        pygame.draw.rect(screen, (255, 0, 0), (front_x, front_y, 5, 5))
        pygame.draw.rect(screen, (255, 0, 0), (back_x, back_y, 5, 5))
        pygame.draw.rect(screen, (255, 0, 0), (car.x, car.y, 5, 5))
        pygame.draw.rect(screen, (255, 0, 0), (car.x + 16, car.y + 16, 5, 5))"""
    gen = font.render("Gen: " + str(generation), True, (255, 255, 255))
    screen.blit(gen, (10, 10))
    laps = font.render("Laps: " + str(lap_count), True, (255, 255, 255))
    screen.blit(laps, (trackpx.size[0] - laps.get_width(), 10))
    timer = font.render("Time: " + str(seconds), True, (255, 255, 255))
    screen.blit(timer, (trackpx.size[0]/2 - timer.get_width()/2, 10))
    cars_alive = font.render("Cars alive: " + str(cars_len), True, (255, 255, 255))
    #print(trackpx.size[1] - 10 - cars_alive.get_height())
    screen.blit(cars_alive, (10, trackpx.size[1] - 10 - cars_alive.get_height()))
    screen.blit(cars_alive, (10, 500))
    pygame.display.update()




def eval_genomes(genomes, config):
    global gen
    gen += 1
    nets = []
    cars = []
    ge = []
    for genome_id, genome in genomes:
        # adding three lists of all nets and genomes
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        # this is where the Car starts, change the numbers so you can start the car at the start of your track
        cars.append(Car(900, 70, trackpx))
        genome.fitness = 0
        ge.append(genome)
    clock = pygame.time.Clock()
    track = Track()
    clock.get_time()
    running = True
    begin_time = pygame.time.get_ticks()
    frames = 0
    while running:
        clock.tick(30)
        millis = pygame.time.get_ticks()
        seconds = (millis - begin_time)//1000
        frames += 1
        #print(frames)
        #print(seconds)


        #print(clock.get_fps())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
                break
        laps = cars[0].laps
        for x, car in enumerate(cars):
            #
            gain = car.gain_points()
            if gain[1]:
                print("Gained" + str(70000//frames))
                ge[x].fitness += 70000 // frames
            ge[x].fitness += gain[0]
            #print(ge[x].fitness)
            if gain[0] == car.lap_reward and car.angle > 180:
                ge[x].fitness -= gain[0]
                print(ge[x].fitness)
                cars.pop(x)
                nets.pop(x)
                ge.pop(x)
                continue
            if track.collide(car) or (frames**2)/10000 - 1 > ge[x].fitness or (gain[0] == car.lap_reward and car.angle > 180):
                ge[x].fitness -= 1
                print(ge[x].fitness, (frames**2)/10000 - 1)
                print(track.collide(car), (frames**2)/10000 - 1 > ge[x].fitness, (gain[0] == car.lap_reward and car.angle > 180))
                cars.pop(x)
                nets.pop(x)
                ge.pop(x)



        if len(cars) == 0:
            running = False
        for x, car in enumerate(cars):
            #ge[x].fitness += 0.1
            inputs = car.generate_inputs()
            outputs = nets[x].activate((inputs))
            if outputs[1] > 0.5:
                car.accelerate()
                #ge[x].fitness += 1
            elif outputs[1] < -0.5:
                car.decelerate()
            car.move()
            if car.vel >= 1:
                if outputs[0] > 0.5:
                    car.turn_left()
                elif outputs[0] < -0.5:
                    #ge[x].fitness += 0.01
                    car.turn_right()


        draw_screen(window, cars, BG_IMG, gen, laps, seconds, len(cars))


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(eval_genomes, 100)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
