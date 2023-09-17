#importing modules
import pygame
from pygame.locals import *
from pygame import mixer
import os
import time
import random

#initializing pygame font module and mixer module
pygame.font.init()
pygame.mixer.init(44100, -16, 2, 512)

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shootah")

#loading background music
pygame.mixer.music.load("assets/music.mp3")
#setting background music volume
pygame.mixer.music.set_volume(0.009)
#setting .play to -1 so that the background music plays repetitively
pygame.mixer.music.play(-1)
#loading sounds and setting their volumes
game_over_fx = pygame.mixer.Sound("assets/game_over.mp3")
game_over_fx.set_volume(0.08)
hit = pygame.mixer.Sound("assets/gugu.mp3")
hit.set_volume(0.04)
Level_inc = pygame.mixer.Sound("assets/Level_inc.mp3")
Level_inc.set_volume(0.06)


#Loading Enemy Ships
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "Coconut_lady.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "Guatemala.png"))

#Loading Healer Ship
FOOD_SPACE_SHIP = pygame.image.load(os.path.join("assets", "Garifuna.png"))

#Loading Player Ship
PLAYER_SPACE_SHIP = pygame.image.load(os.path.join("assets", "Choco.png"))

#Loading Food Laser for the healer ship
FOOD_LASER = pygame.image.load(os.path.join("assets", "R_B.png"))

#Loading Enemy Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "Coco.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "Machette.png"))


#Loading Background Image and setting it's dimensions to be the same as the size of the window
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

#class to serve as an outline for enemy lasers
class Laser:
    # calling __init__ to initialize the attributes of the class
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    #function to display the lasers
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    #function to move the lasers
    def move(self, vel):
        self.y += vel

    #function that doesn't return the position of the lasers in the y axis
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    #function that returns the instance of the class and obj for which a laser collides with
    def collision(self, obj):
        return collide(self, obj)

class Food:
    # calling __init__ to initialize the attributes of the class
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    # function to display the food laser
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # function to move the food laser
    def move(self, vel):
        self.y += vel

    # function that doesn't return the position of the lasers in the y axis
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    # function that returns the instance of the class and obj for which a laser collides with
    def collision(self, obj):
        return collide(self, obj)


class Ship:
    #setting the variable COOLDOWN to 30
    COOLDOWN = 30
    #calling __init__ to initialize the attributes of the class
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        #creating a list for lasers
        self.lasers = []
        self.cool_down_counter = 0

    #function that draws the image of the enemy and enemy lasers and player ships on the screen
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    #function that controls what happens to the lasers depending on specific conditions
    def move_lasers(self, vel, obj):
        self.cooldown()
        #checking if an instance of the class Laser is in the list of lasers and moving it if it is
        for laser in self.lasers:
            laser.move(vel)
            #checking if the laser is behind or past the height of the window
            if laser.off_screen(HEIGHT):
                #if it is past the height of the window then the laser is deleted
                self.lasers.remove(laser)
            #checking if the laser collides with the player
            elif laser.collision(obj):
                #removing 10 health points if it does
                obj.health -= 10
                #playing a sound if it collides
                hit.play(0)
                #removing laser upon impact
                self.lasers.remove(laser)

    #function that handles the cool down before the next shot
    def cooldown(self):
        #if the counter is more than or equal to 30(COOLDOWN) it is reset and the enemy can fire again
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        #if it is less than 30 then it increases and the cooldown continues until the counter more than or equal to COOLDOWN
        elif self.cool_down_counter > 0:
            #Increasing the counter
            self.cool_down_counter += 1

    #function allows shots to be fired if the cooldown is 0
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y)
            #adds the laser to the list which allows it to be shot
            self.lasers.append(laser)
            #after the shot is fired, the counter is set to 1
            self.cool_down_counter = 1

    #function that returns the width of the ship
    def get_width(self):
        return self.ship_img.get_width()

    #function that returns the height of the ship
    def get_height(self):
        return self.ship_img.get_height()

#class for healer ship(Garifuna)
class Healer_Ship:
    COOLDOWN = 30
    #initializing attributed
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        # creating a list for rice and beans
        self.foods = []
        self.cool_down_counter = 0

    # function that draws the image of the healer ship and the laser(Rice and Beans) the screen
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        #Checks for the R&B in the foods list and draws it
        for food in self.foods:
            food.draw(window)

    # function that controls what happens to the R&B depending on specific conditions
    def move_foods(self, vel, obj):
        self.cooldown()
        # checking if an instance of the class food is in the list of lasers and moving it if it is
        for food in self.foods:
            food.move(vel)
            # checking if the R&B is behind or past the height of the window
            if food.off_screen(HEIGHT):
                # if it is past the height of the window then the laser is deleted
                self.foods.remove(food)
            # checking if the laser collides with the player
            elif food.collision(obj):
                # adding 10 health points if it does
                obj.health += 10
                #if to make sure that the health of the player doesn't increase more than a 100 after being healed by the healer
                if obj.health > 100:
                    obj.health = 100
                #removing R&B after impact
                self.foods.remove(food)

    # function that handles the cool down before the next shot
    def cooldown(self):
        # if the counter is more than or equal to 30(COOLDOWN) it is reset and the enemy can fire again
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        # if it is less than 30 then it increases and the cooldown continues until the counter more than or equal to COOLDOWN
        elif self.cool_down_counter > 0:
            # Increasing the counter
            self.cool_down_counter += 1

    # function allows the R&B to be fired if the
    def shoot(self):
        if self.cool_down_counter == 0:
            food = Food(self.x, self.y, self.food_img)
            # adds the R&B to the list which allows it to be shot
            self.food.append(food)
            # after the shot is fired, the counter is set to 1
            self.cool_down_counter = 1

    # function that returns the width of the ship
    def get_width(self):
        return self.ship_img.get_width()

    # function that returns the height of the ship
    def get_height(self):
        return self.ship_img.get_height()

#class for player that calls the class Ship as to use its attributes
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        #assigning the image of the player ship to a variable 'ship_img'
        self.ship_img = PLAYER_SPACE_SHIP
        #setting the size of the ship
        self.ship_img = pygame.transform.scale(self.ship_img,(80, 65))
        #creating a mask so that collision can be perfectly detected
        self.mask = pygame.mask.from_surface(self.ship_img)
        #setting max health to the current health(100). Therefore, start health is a 100
        self.max_health = health

    #function that draws to the window
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    #function that creates the healthbar using two rectangles. Here, the color and size of both is set.
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


#class for the enemy ship that makes use of the Ship class attributes
class Enemy(Ship):
    #so that the images can be assigned at the same time
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        #assigning the image of the enemy ships and the lasers to the variable ship_img and laser_img
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        #setting the size of the enemy ships
        self.ship_img = pygame.transform.scale(self.ship_img, (80, 65))
        #creating a mask to detect perfect collisions
        self.mask = pygame.mask.from_surface(self.ship_img)

    #function that moves the ship
    def move(self, vel):
        self.y += vel

    #function that controls when the ships shoot
    def shoot(self):
        #if the counter is 0 then a laser is appended to the list
        if self.cool_down_counter == 0:
            #using attributes of the Laser class to get a laser
            laser = Laser(self.x-20, self.y, self.laser_img)
            #appending the laser to the list
            self.lasers.append(laser)
            #counter is set to one
            self.cool_down_counter = 1

#class for the healer ship that makes use of the Healer_Ship class attributes
class Healer(Healer_Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        #assigning the image of the healer ships and the R&B to the variable ship_img and laser_img. Their sizes are also set here.
        self.ship_img = FOOD_SPACE_SHIP
        self.ship_img = pygame.transform.scale(self.ship_img, (80, 65))
        self.food_img = FOOD_LASER
        self.food_img = pygame.transform.scale(self.food_img, (65, 65))
        # creating a mask to detect perfect collisions
        self.mask = pygame.mask.from_surface(self.ship_img)

    # function that moves the ship
    def move(self, vel):
        self.y += vel

    #function that controls when the ship shoots
    def shoot(self):
        #if the counter is 0 then a R&B is appended to the list
        if self.cool_down_counter == 0:
            #using attributes of the Food class to get a laser
            laser = Food(self.x-20, self.y, self.food_img)
            # appending the laser to the list
            self.foods.append(laser)
            #counter is set to 1
            self.cool_down_counter = 1


#function that confirms the collsion
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#function that incorporates all the classes and functions
def main():
    #setting run to true so the game can run
    run = True
    #setting fps to 60
    FPS = 60
    #starting at level 0
    level = 0

    #seting the type and size of font for the lost_font and main_font
    main_font = pygame.font.SysFont("Orbitron", 40)
    lost_font = pygame.font.SysFont("Orbitron", 40)

    #creating list items created
    enemies = []
    healers = []

    #settinf game variables
    wave_length = 5
    healer_length = 1
    enemy_vel = 1
    healer_vel = 1
    player_vel = 5
    laser_vel = 5

    #setting the player position
    player = Player(300, 630)

    #tracking time
    clock = pygame.time.Clock()

    #setting lost to False because the player hasn't lost. This way the code can run.
    lost = False
    #setting lost_count to 0 because the player hasn't lost.
    lost_count = 0

    #function that displays everything
    def redraw_window():
        #setting background image position
        WIN.blit(BG, (0,0))
        # draw text
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        WIN.blit(level_label, (WIDTH - level_label.get_width() -290, 10))

        #drawing enemies
        for enemy in enemies:
            enemy.draw(WIN)

        #drawing healer ship
        for healer in healers:
            healer.draw(WIN)

        #drawing the player
        player.draw(WIN)

        #Here we check if the player has lost.
        if lost:
            #if the player lost then the text is displayed
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            #drawing text at a specified position
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        #updating the display
        pygame.display.update()

    #while that runs when the player has not lost
    while run:
        clock.tick(FPS)
        redraw_window()

        #if that checks if the player healht is less than or equal to 0
        if player.health <= 0:
            #if it is then lost is set to true and the user can either exit or restart
            lost = True
            #increasing lost count
            lost_count += 1
            #playing the game_over sound
            game_over_fx.play(0)
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        #if that control the spawning and number of enemy ships
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            Level_inc.play(0)
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue"]))
                enemies.append(enemy)

        # if that control the spawning and number of healer ships
        if len(healers) == 0:
            healer_length += 2
            for i in range(healer_length):
                healer = Healer(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), FOOD_SPACE_SHIP)
                healers.append(healer)

        #checks if the user presses exit(the x on the window) and closes the game if they do
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        #getting key presses
        keys = pygame.key.get_pressed()

        #if's that controls movements
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel

        #calling the function to move ships
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            #calling the collide function for the enemy and player
            if collide(enemy, player):
                #if there is collision then 10 hp is reduced from the health of the player
                player.health -= 10
                #once collision occurs the enemy ship is removed
                enemies.remove(enemy)
            #if the enemy ships are past the margin of the window then they are deleted
            elif enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)

        #calling the function to move healer ships
        for healer in healers[:]:
            healer.move(healer_vel)
            healer.move_foods(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                healer.shoot()

            # calling the collide function for the healer and player
            if collide(healer, player):
                # if there is collision then 10 hp is added to the health of the player
                player.health += 10
                # once collision occurs the enemy ship is removed
                healers.remove(healer)
                #if that makes sure that the player health does not pass 100
                if player.health > 100:
                    player.health = 100

            # if the enemy ships are past the margin of the window then they are deleted
            elif healer.y + healer.get_height() > HEIGHT:
                healers.remove(healer)

        #removing the lasers and R&B
        player.move_lasers(-laser_vel, enemies,)
        player.move_lasers(-laser_vel, healers)

#function that creates and display the main menu
def main_menu():
    #setting font type and size
    title_font = pygame.font.SysFont("Orbitron", 40)
    #setting the variable 'run' that controls whether the game is running or closed
    run = True
    #As long as the game is running then the main menu is able to be displayed
    while run:
        #This allows the background to be displayed. Also, it is being set to fill the entire window
        WIN.blit(BG, (0,0))
        #variable containing the text displayed on the menu and sets the color to white.
        title_label = title_font.render("Press The Mouse to Begin...", 1, (255,255,255))
        #displaying the text and setting its position
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        #allows the main menu to be updated
        pygame.display.update()
        #for loop that checks for events
        for event in pygame.event.get():
            #if the game is quit the run is set to false so that the game can be closed
            if event.type == pygame.QUIT:
                run = False
            # Here we check if mouse buttons are pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                #if any mouse button is pressed, the main function is called
                main()
    pygame.quit()

#calling the main menu so that it can be displayed
main_menu()