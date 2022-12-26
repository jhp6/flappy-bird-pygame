import pygame
import random
from pygame.locals import *
from pygame.sprite import Sprite
from sys import exit

# game statuses
READY = 0  # settings, playbutton
ACTIVE = 1 # jumping, updates, ...
OVER = 2 # falling bird, stop motion, display scores

class Bird(Sprite):
    def __init__(self, fb_game):
        super().__init__()
        self.screen = fb_game.screen
        self.settings = fb_game.settings
        self.screen_rect = fb_game.screen_rect

        # Load the bird image and get its rect
        self.original_image = pygame.image.load("bird.png").convert_alpha()
        self.image = pygame.image.load("bird.png").convert_alpha()
        self.rect = self.image.get_rect()

        # Start each new bird at the center of the screen
        # self.rect.center = self.screen_rect.center
        self.rect.center = (self.screen_rect.centerx // 2, self.screen_rect.centery)

        # Store a decimal value for the bird's vertical position
        self.y = float(self.rect.y)

        # Flag for jumping
        self.isjump = False

        self.rotation_angle = 0
        self.previous_rotation_angle = 0

        self.rotation_range = self.settings.bird_fall_angle

    def update(self):
        """Update the bird's position based on gravity and jumping"""
        if self.isjump:
            self.distance_moved = self.settings.time_passed_seconds * self.settings.bird_jumping_velocity
            self.bird_jumping_gravity = self.settings.time_passed_seconds * self.settings.bird_gravity
            self.y -= self.distance_moved
            self.settings.bird_jumping_height += self.distance_moved

            if self.rotation_angle < self.settings.bird_rise_angle:
                self.rotation_angle = self.settings.bird_jumping_height / self.settings.bird_max_jumping_height * (self.settings.bird_rise_angle + self.previous_rotation_angle) - self.previous_rotation_angle
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
            self.settings.bird_jumping_velocity -= self.bird_jumping_gravity
            if self.settings.bird_jumping_velocity <= 0:
                self.isjump = False
                self.settings.bird_velocity = self.settings.bird_initial_velocity
                self.settings.bird_jumping_velocity = self.settings.bird_initial_jumping_velocity
                self.settings.bird_jumping_height = 0
                self.previous_rotation_angle = abs(self.rotation_angle)
                return

            self.rect.y = self.y
            return

        self.fall()

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def jump(self):
        self.isjump = True
        self.settings.bird_velocity = self.settings.bird_initial_velocity
        self.settings.bird_jumping_velocity = self.settings.bird_initial_jumping_velocity
        self.previous_rotation_angle = -self.rotation_angle

        if self.settings.bird_jumping_height < 0 or self.settings.bird_jumping_height > self.settings.bird_max_jumping_height:
            self.settings.bird_jumping_height = 0
    
    def fall(self):
        self.distance_moved = self.settings.time_passed_seconds * self.settings.bird_velocity
        if self.settings.bird_jumping_height >= self.settings.bird_max_falling_height:
            self.settings.bird_jumping_height -= self.distance_moved
        if self.rotation_angle > self.settings.bird_fall_angle:
            self.rotation_angle = self.settings.bird_jumping_height / self.settings.bird_max_falling_height * (self.settings.bird_fall_angle - self.previous_rotation_angle) + self.previous_rotation_angle
        self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)

        self.bird_gravity = self.settings.time_passed_seconds * self.settings.bird_gravity
        self.y += self.distance_moved

        if self.settings.bird_velocity < self.settings.bird_max_velocity:
            self.settings.bird_velocity += self.bird_gravity

        self.rect.y = self.y

    def lose_fall(self):
        if self.rect.bottom >= self.settings.ground_height:
            return
        self.fall()

    def float(self):
        pass

class MovingBackground(Sprite):
    def __init__(self, fb_game):
        """Initialize the background and set its starting position"""
        self.screen = fb_game.screen
        self.settings = fb_game.settings
        self.screen_rect = self.screen.get_rect()

        # Load the background image and set its rect attribute
        self.image = pygame.image.load("background.jpg").convert()
        self.rect = self.image.get_rect()
        # Location for the second image
        self.rect2 = self.image.get_rect()

        # Start each background at the start top left of the screen
        self.rect.bottomleft = self.screen_rect.bottomleft
        self.rect2.bottomleft = self.rect.bottomright

        # Store the backgrounds' exact horizontal position
        self.x = float(self.rect.x)
        self.x2 = float(self.rect2.x)

        self.background_width = self.image.get_width()
        
    def update(self):
        self.distance_moved = self.settings.time_passed_seconds * self.settings.background_speed
        self.x += self.distance_moved
        self.x2 += self.distance_moved

        if self.x <= -self.background_width:
            self.x = 0
            self.x2 = self.background_width

        self.rect.x = self.x
        self.rect2.x = self.x2 

    def blitme(self):
        self.screen.blit(self.image, self.rect)
        self.screen.blit(self.image, self.rect2)

class GameStats:
    """Track statistics for Fapping Bird."""

    def __init__(self, fb_game):
        """Initialize statistics."""
        self.settings = fb_game.settings
        self.reset_stats()

        self.game_status = READY

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.score = 0

class Ground(Sprite):
    def __init__(self, fb_game):
        """Create a ground next to the last ground. If none, to the leftmost part of the screen."""
        super().__init__()
        self.screen = fb_game.screen
        self.settings = fb_game.settings
        self.screen_rect = fb_game.screen_rect

        # Load the ground image and set its rect attribute
        self.image = pygame.image.load("ground.png").convert_alpha()
        self.rect = self.image.get_rect()
        
        # Start the first ground at the bottom left
        self.rect.y = self.settings.ground_height


        # Store the first ground's exact horizontal position
        self.x = float(self.rect.x)

    def update(self):
        """Move the ground to the left of the screen."""
        self.distance_moved = self.settings.time_passed_seconds * self.settings.ground_speed
        self.x -= self.distance_moved
        
        if self.x <= -self.rect.width:
            self.kill()
        self.rect.x = self.x



class Settings:
    def __init__(self):
        """Initialize the game's static settings."""
        # Screen settings
        self.screen_width = 1000
        self.screen_height = 680
        self.bg_color = (255, 255, 255) # unnecessary because the background image covers the entire background
        self.screen_flags = 0
        self.screen_depth = 32

        # Bird settings
        # gravity
        self.bird_gravity = 2500
        self.bird_initial_velocity = 0
        self.bird_max_velocity = 2000
        # jumping
        self.bird_initial_jumping_velocity = 600
        self.bird_max_jumping_height = self.bird_initial_jumping_velocity / self.bird_gravity / 2 * self.bird_initial_jumping_velocity
        # rotation
        self.bird_rise_angle = 25
        self.bird_fall_angle = -60
        self.bird_max_falling_height = -300
        
        # Ground settings
        self.ground_speed = 200
        self.ground_height = self.screen_height - 100

        # Pipe settings
        self.pipe_speed = self.ground_speed # matches the ground speed because...
        self.pipe_space = 200 # space between the up and down pipes
        self.pipe_distance = self.screen_width - 300 # frequency of pipes
        self.pipe_initial_height = 100
        # pipe facing down
        self.pipe_min_top = self.pipe_initial_height
        self.pipe_max_top = self.ground_height - self.pipe_initial_height - self.pipe_space

        # Background settings
        self.background_speed = -50.0

        # Ready messages settings
        self.ready_font_path = "score_font.ttf" # same as score font
        self.flappy_font_path = self.ready_font_path
        self.flappy_font_size = 100
        self.flappy_text_color = (237, 112, 20)
        self.getready_font_path = self.ready_font_path
        self.getready_font_size = 80
        self.getready_text_color = (60, 176, 67)
        self.press_font_path = self.ready_font_path
        self.press_font_size = 50
        self.press_text_color = (0, 0, 0)

        # Over messages settings
        self.gameover_font_path = self.ready_font_path
        self.gameover_font_size = 100
        self.gameover_text_color = (178, 34, 34)
        self.score_rect_color = (0, 0, 0)
        self.score_font_path = self.ready_font_path
        self.score_font_size = 50
        self.score_text_color = (255, 255, 255)
        self.highscore_font_path = self.score_font_path
        self.highscore_font_size = 50
        self.highscore_text_color = (255, 255, 255)
        self.border_width = 10
        self.border_color = (0, 150, 0)

        # Scoreboard settings
        self.activescore_font_path = self.ready_font_path
        self.activescore_font_size = 100
        self.activescore_color = (0, 0, 0)

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.bird_velocity = self.bird_initial_velocity
        self.bird_jumping_height = 0
        self.bird_falling_height = 0
        self.bird_jumping_velocity = self.bird_initial_jumping_velocity
        self.time_passed_seconds = 0.0
        self.active_time = 0


class Scoreboard:
    """A class to report scoring information while game is ACTIVE."""

    def __init__(self, fb_game):
        """Initialize scorekeeping attributes."""
        self.screen = fb_game.screen
        self.screen_rect = fb_game.screen_rect
        self.settings = fb_game.settings
        self.stats = fb_game.stats

        # Font settings for scoring information
        self.font = pygame.font.Font(self.settings.activescore_font_path, self.settings.activescore_font_size)
        self.color = self.settings.activescore_color

        # Prepare the initial score images.
        self.prep_score()

        self.rect = self.image.get_rect()
        self.rect.midtop = self.screen_rect.midtop


    def prep_score(self):
        """Turn the score into a rendered image."""
        self.image = self.font.render(str(self.stats.score), False, self.color, None)

    def show_score(self):
        """Draw score while game is active"""
        self.screen.blit(self.image, self.rect)

class Ready:
    def __init__(self, fb_game):
        self.settings = fb_game.settings
        self.screen = fb_game.screen
        self.screen_rect = fb_game.screen_rect

        # a text saying FLAPPY BIRD
        self.flappy_font = pygame.font.Font(self.settings.flappy_font_path, self.settings.flappy_font_size)
        self.flappy_text = "FLAPPY BIRD"
        self.flappy_text_color = self.settings.flappy_text_color
        self.flappy_message_image = self.flappy_font.render(self.flappy_text, False, self.flappy_text_color, None)
        self.flappy_message_rect = self.flappy_message_image.get_rect()
        self.flappy_message_rect.center = (self.screen_rect.centerx, self.screen_rect.height // 4)

        # a text saying GET READY!
        self.getready_font = pygame.font.Font(self.settings.getready_font_path, self.settings.getready_font_size)
        self.getready_text = "GET READY!"
        self.getready_text_color = self.settings.getready_text_color
        self.getready_message_image = self.getready_font.render(self.getready_text, False, self.getready_text_color, None) 
        self.getready_message_rect = self.getready_message_image.get_rect()
        self.getready_message_rect.center = (self.screen_rect.centerx, self.screen_rect.height // 4 * 2)

        # a text saying press space to play 
        self.press_font = pygame.font.Font(self.settings.press_font_path, self.settings.press_font_size)
        self.press_text = "press space to play"
        self.press_text_color = self.settings.press_text_color
        self.press_message_image = self.press_font.render(self.press_text, False, self.press_text_color, None) 
        self.press_message_rect = self.press_message_image.get_rect()
        self.press_message_rect.center = (self.screen_rect.centerx, self.screen_rect.height // 4 * 3)


    def show_messages(self):
        """Draw ready message to the screen."""
        self.screen.blit(self.flappy_message_image, self.flappy_message_rect)
        self.screen.blit(self.getready_message_image, self.getready_message_rect)
        self.screen.blit(self.press_message_image, self.press_message_rect)


class Pipe(Sprite):
    """A class to represent a single pipe."""

    def __init__(self, fb_game):
        """Initialize the pipe and set its starting position."""
        super().__init__()
        self.screen = fb_game.screen
        self.settings = fb_game.settings
        self.screen_rect = fb_game.screen_rect

        # store the pipe's exact horizontal position
        self.x = float(self.screen_rect.width)

    def update(self):
        self.distance_moved = self.settings.time_passed_seconds * self.settings.pipe_speed
        self.x -= self.distance_moved
        if self.x <= -self.rect.width:
            self.kill()
        self.rect.x = self.x

class DownPipe(Pipe):
    """A pipe that is facing downwards."""

    def __init__(self, fb_game):
        super(DownPipe, self).__init__(fb_game)

        # Load the pipe image and set its rect attribute.
        self.image = pygame.image.load("downpipe.png").convert_alpha()
        self.rect = self.image.get_rect()
        
        # Start each new pipe outside, "next" to the screen.
        self.rect.x = self.screen_rect.width

class UpPipe(Pipe):
    """A pipe that is facing upwards."""

    def __init__(self, fb_game):
        super(UpPipe, self).__init__(fb_game)

        # Load the pipe image and set its rect attribute.
        self.image = pygame.image.load("uppipe.png").convert_alpha()
        self.rect = self.image.get_rect()

        # Start each new pipe outside, "next" to the screen.
        self.rect.x = self.screen_rect.width
        self.latest = True
        self.scored = False

class Over:
    def __init__(self, fb_game):
        self.settings = fb_game.settings
        self.screen = fb_game.screen
        self.screen_rect = fb_game.screen_rect
        self.stats = fb_game.stats

        # game over text
        self.gameover_font = pygame.font.Font(self.settings.gameover_font_path, self.settings.gameover_font_size)
        self.gameover_text = "GAME OVER"
        self.gameover_text_image = self.gameover_font.render(self.gameover_text, False, self.settings.gameover_text_color, None)
        self.gameover_text_rect = self.gameover_text_image.get_rect()

        self.score_font = pygame.font.Font(self.settings.score_font_path, self.settings.score_font_size)
        self.highscore_font = pygame.font.Font(self.settings.highscore_font_path, self.settings.highscore_font_size)
        self.prep_highscore()
        self.prep_score()

        self.score_text_rect = self.score_text_image.get_rect()
        self.highscore_text_rect = self.highscore_text_image.get_rect()

        # place the texts after creating the images for each element
        self.gameover_text_rect.midtop  = (self.screen_rect.centerx, self.screen_rect.centery - (self.gameover_text_rect.height + self.score_text_rect.height + self.highscore_text_rect.height) // 2)
        self.score_text_rect.midtop = self.gameover_text_rect.midbottom
        self.highscore_text_rect.midtop = self.score_text_rect.midbottom

        # score rectangle
        self.score_rect = pygame.Rect((0, 0), (max(self.gameover_text_rect.width, self.highscore_text_rect.width, self.score_text_rect.width), self.gameover_text_rect.height + self.score_text_rect.height + self.highscore_text_rect.height))
        self.score_rect.center = self.screen_rect.center

        # border
        self.border_rect = pygame.Rect((0, 0), (self.score_rect.width + self.settings.border_width, self.score_rect.height + self.settings.border_width))
        self.border_rect.center = self.score_rect.center

    def show_score(self):
        """Draw game over, score, and highscore texts."""
        pygame.draw.rect(self.screen, self.settings.border_color, self.border_rect)
        pygame.draw.rect(self.screen, self.settings.score_rect_color, self.score_rect)
        self.screen.blit(self.gameover_text_image, self.gameover_text_rect)
        self.screen.blit(self.score_text_image, self.score_text_rect)
        self.screen.blit(self.highscore_text_image, self.highscore_text_rect)

    def prep_score(self):
        """Turn the score into a rendered image."""
        self.score_text = f"Score: {self.stats.score}"
        self.score_text_image = self.score_font.render(self.score_text, False, self.settings.score_text_color, None)

    def prep_highscore(self):
        """Turn the highscore into a rendered image."""
        # find the stored highscore
        with open("highscore.txt", "r") as infile:
            highscore = int(infile.read())
        if highscore< self.stats.score:
            with open("highscore.txt", "w") as outfile:
                outfile.write(str(self.stats.score))
            highscore = self.stats.score
        self.highscore_text = f"Highscore: {highscore}"
        self.highscore_text_image = self.highscore_font.render(self.highscore_text, False, self.settings.highscore_text_color, None)

class FlappyBird:
    def __init__(self):
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height), self.settings.screen_flags, self.settings.screen_depth)
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption("FLAPPY BIRD!")

        # Game elements
        self.bird = Bird(self)
        self.pipes = pygame.sprite.Group()
        self._create_pipe_pair()
        self.grounds = pygame.sprite.Group()
        self._create_grounds()
        self.stats = GameStats(self)
        self.scoreboard = Scoreboard(self)
        self.ready = Ready(self)
        self.moving_background = MovingBackground(self)
        self.over = Over(self)
        self._initialize_sounds()

        self.clock = pygame.time.Clock()

    def run_game(self):
        """Start main loop for the game."""
        while True:
            self.settings.time_passed_seconds = self.clock.tick() / 1000
            self._check_events()

            if self.stats.game_status == ACTIVE:
                self.settings.active_time += self.settings.time_passed_seconds
                self.bird.update()
                self._update_pipes()
                self._update_grounds()
                self.moving_background.update()
            elif self.stats.game_status == OVER:
                self.bird.lose_fall()
                # display scoreboard
            elif self.stats.game_status == READY:
                self._update_grounds()
                self.moving_background.update()
                self.bird.float()
                pass

            self._update_screen()

    def _initialize_sounds(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512, devicename=None, allowedchanges=AUDIO_ALLOW_FREQUENCY_CHANGE | AUDIO_ALLOW_CHANNELS_CHANGE)
        self.die_sound = pygame.mixer.Sound("die.ogg")
        self.hit_sound = pygame.mixer.Sound("hit.ogg")
        self.point_sound = pygame.mixer.Sound("point.ogg")
        self.wing_sound = pygame.mixer.Sound("wing.ogg")

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN:
                self._check_keydown_events(event)
    def _check_keydown_events(self, event):
        if event.key == K_SPACE:
            if self.stats.game_status == ACTIVE:
                self.bird.jump()
                self.wing_sound.play()
            elif self.stats.game_status == READY:
                self.stats.game_status = ACTIVE
                self.bird.jump()
                self.wing_sound.play()
            elif self.stats.game_status == OVER:
                self.stats.game_status = READY
                self.settings.initialize_dynamic_settings()
                self.stats.reset_stats()
                self.pipes.empty()
                self.scoreboard.prep_score()
                self._create_pipe_pair()
                self.bird.rect.center = (self.screen_rect.centerx // 2, self.screen_rect.centery)
                self.bird.y = float(self.bird.rect.y)
                self.bird.rotation_angle = 0
                self.settings.bird_jumping_velocity = self.settings.bird_initial_jumping_velocity
                self.bird.rotation_angle = 0
                self.bird.previous_rotation_angle = 0
                self.bird.image = pygame.transform.rotate(self.bird.original_image, self.bird.rotation_angle)

        elif event.key == K_q:
            pygame.quit()
            exit()

    def _update_pipes(self):
        if self.settings.active_time < 2:
            return

        self.pipes.update()
        pipes = self.pipes.sprites()
        last_pipe = pipes[-1]
        if last_pipe.rect.left <= self.settings.pipe_distance and last_pipe.latest:
            self._create_pipe_pair()
            last_pipe.latest = False

        # Check bird and pipes collisions
        if pygame.sprite.spritecollideany(self.bird, self.pipes):
            self._bird_hit()
            self.die_sound.play()
            self.bird.isjump = False
            self.settings.bird_velocity = self.settings.bird_initial_velocity
            self.settings.bird_jumping_velocity = self.settings.bird_initial_jumping_velocity
            self.settings.bird_jumping_height = 0
            self.bird.previous_rotation_angle = abs(self.bird.rotation_angle)
            return

        # Check if bird crossed the pipe
        for pipe in range(1, len(pipes), 2):
            pipe = pipes[pipe]
            if pipe.rect.left <= self.bird.rect.left and not pipe.scored:
                pipe.scored = True
                self.point_sound.play()
                self.stats.score += 1
                self.scoreboard.prep_score()

    def _create_pipe(self, direction, y):
        """Create a pipe and set its direction and position.

        :param direction: -1 if down and 1 if up
        :type direction: int
        """
        if direction == -1:
            pipe = DownPipe(self)
            pipe.rect.bottom = y
        elif direction == 1:
            pipe = UpPipe(self)
            pipe.rect.top = y
        else:
            return
        self.pipes.add(pipe)

    def _create_pipe_pair(self):
        """Create the pipe pair: One facing down and one facing up."""
        random_height = random.randint(self.settings.pipe_min_top, self.settings.pipe_max_top)
        self._create_pipe(-1, random_height)
        self._create_pipe(1, random_height + self.settings.pipe_space)

    def _bird_hit(self):
        """Sending "bird dead" statuses to elements."""
        self.stats.game_status = OVER
        self.over.prep_score()
        self.over.prep_highscore()
        self.hit_sound.play()

    def _update_grounds(self):
        self.grounds.update()
        last_ground = self.grounds.sprites()[-1]
        if last_ground.rect.right <= self.screen_rect.width:
            ground = Ground(self)
            ground.rect.bottomleft = last_ground.rect.bottomright
            ground.x = float(ground.rect.x)
            self.grounds.add(ground)

        # check if bird hits ground
        if pygame.sprite.spritecollideany(self.bird, self.grounds):
            self._bird_hit()

    def _create_grounds(self):
        for x in range(self.screen_rect.width // Ground(self).rect.width + 1):
            ground = Ground(self)
            ground.rect.x = x * ground.rect.width
            ground.x = ground.rect.x
            self.grounds.add(ground)

    def _update_screen(self):
        """Update images on the screen, and update to the new screen."""
        self.moving_background.blitme()
        self.pipes.draw(self.screen)
        self.grounds.draw(self.screen)
        self.bird.blitme()
        if self.stats.game_status == READY:
            self.ready.show_messages()
        elif self.stats.game_status == OVER:
            self.over.show_score()
        elif self.stats.game_status == ACTIVE:
            self.scoreboard.show_score()
        pygame.display.update()

if __name__ == "__main__":
    fb_game = FlappyBird()
    fb_game.run_game()
