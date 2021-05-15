
import pygame
import random

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.80) #To integer because it will give you a Float

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PyramidAliens") #Caption for the game window

#framerate
clock = pygame.time.Clock()
FPS = 60

#player action variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False
shoot = False


#images
bullet_img = pygame.image.load("Sprites/Bullet/bullet.png").convert_alpha()
enemy_bullet = pygame.image.load("Sprites/Bullet/enemy_bullet.png").convert_alpha()

#Colours
BG = pygame.image.load("Sprites/Background/main.png").convert_alpha()
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0 ,0)

#font
font = pygame.font.SysFont("Futura", 30)


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
	screen.blit(BG, (0,0))
	
	screen.blit(font.render("Made by Santiago Villa", 1, (255, 255, 240)), (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 25))
	#pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


class Mague(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.shoot_cooldown = 0
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.flip = False
		#here character animation
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#Ai specific variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0

		#image loading
		temp_list = []
		for i in range(4):
			img = pygame.image.load(f"Sprites/{self.char_type}/Standing/{i}.png") #PLAYER IMAGE
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			temp_list.append(img)
		self.animation_list.append(temp_list)
		temp_list = []
		for i in range(3):
			img = pygame.image.load(f"Sprites/{self.char_type}/Walk/{i}.png") #PLAYER IMAGE
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			temp_list.append(img)
		self.animation_list.append(temp_list)
		temp_list = []
		#other animations go here
		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()  #Boundary box of the player, collisions
		self.rect.center = (x,y)

	def update(self):
		self.update_animation()
		self.check_alive()
		#cooldown update
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right, moving_up, moving_down):
		#reset movement variables
		dx = 0
		dy = 0

		#movement variables if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = False
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = True
			self.direction = 1
		if moving_up and self.rect.bottom > 500:
			dy = -self.speed
			self.flip = False
			self.direction = -1
		if moving_down:
			dy = self.speed
			self.flip = False
			self.direction = 1

		#collision
		if self.rect.bottom + dy > SCREEN_HEIGHT:
			dy = SCREEN_HEIGHT - self.rect.bottom
		

		#update rectangle position
		self.rect.x += dx
		self.rect.y += dy


	def shoot(self, image):
		if self.shoot_cooldown == 0:
			self.shoot_cooldown = 30
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, image)
			bullet_group.add(bullet)


	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)
				self.idling = True
				self.idling_counter = 50
			#check if the ai is near the player
			if self.vision.colliderect(player.rect):
				#stop running and face the player
				self.shoot(enemy_bullet)
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					
					
					self.move(ai_moving_left, ai_moving_right, None, None)
					self.move_counter += 1
					#update ai vision as the enemy moves
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
					if self.move_counter > 40:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False




	def update_animation(self):
		ANIMATION_COOLDOWN = 100
		self.image = self.animation_list[self.action][self.frame_index]
		#checking if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#if animation runs out reset back to start
		if self.frame_index >= len(self.animation_list[self.action]):
			self.frame_index = 0

	def update_action(self, new_action):
		#checks if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			#update the animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def check_alive(self):
		if self.health <=0:
			self.health = 0
			self.speed = 0
			self.alive = False



	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#update with new health
		self.health = health
		#health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x,  self.y , 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction, image):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 15
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.center = (round(x), round(y) + 3)
		self.direction = direction

	def update(self):
		#movement of the bullet
		self.rect.x += (self.direction * self.speed)
		#offscreen check
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()

		#check if hit by bullet
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()

		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25 #REDUCE THIS NUMBER TO CHANGE DIFFICULTY
					self.kill()






#sprite groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()



player = Mague("Player", 200,900, 0.65, 5)
health_bar = HealthBar(10, 10, player.health, player.health)

#I am aware this is a bad practice but I still havent figured how to spawn enemies that can move in the x and y axis
enemy = Mague("Enemy", 600, 900, 0.65, 1)
enemy2 = Mague("Enemy", 400, 600, 0.65, 1)
enemy3 = Mague("Enemy", 300, 700, 0.65, 1)
enemy4 = Mague("Enemy", 700, 620, 0.65, 1)
enemy5 = Mague("Enemy", 100, 550, 0.65, 1)
enemy6 = Mague("Enemy", 50, 620, 0.65, 1)
enemy_group.add(enemy)
enemy_group.add(enemy2)
enemy_group.add(enemy3)
enemy_group.add(enemy4)
enemy_group.add(enemy5)
enemy_group.add(enemy6)



run = True
while run:

	clock.tick(FPS)

	draw_bg()

	player.update()
	player.draw()#Accesses draw method in Mague and draws it to the screen for each instance of player
	
	#healthbar
	health_bar.draw(player.health)
	

	for enemy in enemy_group:
		if enemy.alive:
			enemy.ai()
			enemy.update()
			enemy.draw()
	#update and draw groups
	bullet_group.update()
	bullet_group.draw(screen)

	#update player actions
	if player.alive:
		if shoot:
			player.shoot(bullet_img)
		if moving_left or moving_right or moving_up or moving_down:
			player.update_action(1)
		else:
			player.update_action(0)

		player.move(moving_left, moving_right, moving_up, moving_down)

	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#Keyboard press
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_w:
				moving_up = True
			if event.key == pygame.K_s:
				moving_down = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_ESCAPE:
				run = False


		#keyboard button released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_w:
				moving_up = False
			if event.key == pygame.K_s:
				moving_down = False
			if event.key == pygame.K_SPACE:
				shoot = False

	pygame.display.update()
	
pygame.quit()