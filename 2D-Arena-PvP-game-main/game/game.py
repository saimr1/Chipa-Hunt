import pygame, time, random, math
from entities.player import Player, PLAYER_HEIGHT, PLAYER_WIDTH, BOUNDS_X, BOUNDS_Y
from entities.GameObjects import GameObjects
from entities.projectile import shoot, check_collisions
from entities.enemy import Enemy, enemy_spawner, update_particles, draw_particles, ENEMY_WIDTH, ENEMY_HEIGHT, particles
from entities.potion import Potion
from game.state_manager import state
from game.states.menu_state import menu_state
from game.states.pause_state import pause_state
from game.states.name_entry_state import name_entry_state
from game.highscores import init_db, save_score
from game.audio import load_sound

pygame.init()
pygame.mixer.init()
pygame.font.get_init()
 
TEXT_FONT = pygame.font.Font("assets/images/font.otf", 32)
 
WIDTH, HEIGHT = 1280, 720
shoot_cooldown = 300
FRAME_RATE = 120
ANIMATION_FRAME_RATE = 10
MAX_BULLET_BOUNCES = 2
def screen_shake(intensity, amplitude):
    s = -1
    for _ in range(3):
        for x in range(0, amplitude, intensity):
            yield (x * s, 0)
        for x in range(amplitude, 0, -intensity):
            yield (x * s, 0)
        s *= -1
 
 
class Game:
    def __init__(self):
        pygame.init()
        self.state = "playing"
        self.width = WIDTH
        self.height = HEIGHT
        self.shake_gen = None
        self.shake_offset = (0, 0)
        self.cursor_scale = 1
        self.score = 0
        self.invulnerable_until = 0
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chippa Hunter")
        
        self.clock = pygame.time.Clock()
        self.last_shot_time = 0
 
        self.player1 = Player(WIDTH // 2 - PLAYER_WIDTH // 2,HEIGHT // 2 - PLAYER_HEIGHT // 2,PLAYER_WIDTH,PLAYER_HEIGHT,"assets/images/player-sheet.png",5)
 
        self.enemies = []
        self.enemy_gen = enemy_spawner(self.player1, self.enemies)
 
        self.bullets = []
        self.sparks = []
        self.potions = []
 
        self.bg = pygame.image.load("assets/images/background.png")
        self.bg = pygame.transform.smoothscale(self.bg, (self.width, self.height))
 
        self.cursor_img = pygame.image.load("assets/images/cursor.png").convert_alpha()
        self.cursor_img = pygame.transform.scale(self.cursor_img, (self.cursor_img.get_width()*2, self.cursor_img.get_height()*2))
        self.cursor_rect = self.cursor_img.get_rect()
        pygame.mouse.set_visible(False)
 
        self.game_over = False
        self.death_screen_done = False
        self.running = True
        self.player_name = "Player"

        self.big_font = pygame.font.Font("assets/images/font.otf", 84)
        self.medium_font = pygame.font.Font("assets/images/font.otf", 40)

        self.death_sound = load_sound("assets/sounds/amongus.ogg", 0.4)
        self.meme_sound = load_sound("assets/sounds/tur_gaye_yar_loud.ogg", 1.0)
        self.eek_sound = load_sound("assets/sounds/eek.ogg", 0.6)
        self.bounce_sound = load_sound("assets/sounds/bounce.ogg", 0.75)
        self.potion_sound = load_sound("assets/sounds/potion.ogg", 0.75)

        self.potion_image = pygame.transform.scale(
            pygame.image.load("assets/images/potion.png").convert_alpha(), (40, 40)
        )
        self.chippa_cake = pygame.image.load("assets/images/chippa_cake.png").convert_alpha()
        self.next_potion_time = pygame.time.get_ticks() + 6000

        init_db()

        self.state_stack = []
        menu = menu_state(self)
        menu.enter_state()
        name_entry = name_entry_state(self)
        name_entry.enter_state()
        
 
    def handle_events(self):
        events = pygame.event.get()
        stack_before = len(self.state_stack)
 
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
 
            if event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_r:
                    self.restart_game()
 
                if self.game_over and event.key == pygame.K_m:
                    self.restart_game()
                    menu = menu_state(self)
                    menu.enter_state()

                if self.game_over and not self.death_screen_done:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                        self.death_screen_done = True
                        self.meme_sound.stop()
 
                if not self.game_over and len(self.state_stack) == 0:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        pause = pause_state(self)
                        pause.enter_state()
 
        if self.state_stack and len(self.state_stack) == stack_before:
            self.state_stack[-1].update(events)
 
    def display_score(self):
        score_text = TEXT_FONT.render(f'Score: {self.score}', True, (0, 0, 0))
        self.screen.blit(score_text, (score_text.get_width() // 2, 25))

    def knockback(self, enemy):
        ex, ey = enemy.get_center()
        px, py = self.player1.rect.center
        dx = px - ex
        dy = py - ey
        distance = math.hypot(dx, dy)
        if distance == 0:
            dx, dy, distance = 1, 0, 1

        push = 70
        self.player1.rect.x += int(dx / distance * push)
        self.player1.rect.y += int(dy / distance * push)
        self.player1.rect.x = max(BOUNDS_X[0], min(self.player1.rect.x, BOUNDS_X[1] - PLAYER_WIDTH))
        self.player1.rect.y = max(BOUNDS_Y[0], min(self.player1.rect.y, BOUNDS_Y[1] - PLAYER_HEIGHT))

    def spawn_potion(self):
        size = self.potion_image.get_width()
        x = BOUNDS_X[0]
        y = BOUNDS_Y[0]
        for _ in range(25):
            x = random.randint(BOUNDS_X[0], BOUNDS_X[1] - size)
            y = random.randint(BOUNDS_Y[0], BOUNDS_Y[1] - size)
            if math.hypot(x - self.player1.rect.centerx, y - self.player1.rect.centery) > 180:
                break
        self.potions.append(Potion(x, y, self.potion_image))

    def restart_game(self):
        self.player1.health = self.player1.max_health
        self.player1.rect.x = self.width // 2 - PLAYER_WIDTH // 2
        self.player1.rect.y = self.height // 2 - PLAYER_HEIGHT // 2
        self.player1.alive = True
 
        self.enemies.clear()
        self.bullets.clear()
        self.sparks.clear()
        self.potions.clear()
        particles.clear()
        self.death_sound.stop()
        self.meme_sound.stop()
        pygame.mixer.music.set_volume(0.1)

        pygame.mouse.set_visible(False)
        self.game_over = False
        self.death_screen_done = False
        self.score = 0
        self.shake_gen = None
        self.shake_offset = (0, 0)
        self.last_shot_time = 0
        self.cursor_scale = 1
        self.invulnerable_until = pygame.time.get_ticks() + 1000
        self.next_potion_time = pygame.time.get_ticks() + 6000
   

 
    def update(self):
 
        if self.state_stack or self.game_over:
            return


        keys = pygame.key.get_pressed()
        self.player1.update(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, self.width, self.height)
 
        if self.player1.alive:
            for enemy in self.enemies[:]:
                enemy.update(self.player1)
            next(self.enemy_gen)
            
        mouse_pressed = pygame.mouse.get_pressed()
        current_time = pygame.time.get_ticks()
        if mouse_pressed[0] and (current_time - self.last_shot_time >= shoot_cooldown):
            shoot(self.player1, pygame.mouse.get_pos(), self.bullets)
            self.last_shot_time = current_time
            self.cursor_scale = 1.4
 
 
        left, right = BOUNDS_X
        top, bottom = BOUNDS_Y

        for bullet in self.bullets[:]:
            bullet.update()
            bounced = False

            if bullet.rect.left <= left and bullet.velocity[0] < 0:
                bullet.rect.left = left
                bullet.velocity[0] = -bullet.velocity[0]
                bounced = True
            elif bullet.rect.right >= right and bullet.velocity[0] > 0:
                bullet.rect.right = right
                bullet.velocity[0] = -bullet.velocity[0]
                bounced = True

            if bullet.rect.top <= top and bullet.velocity[1] < 0:
                bullet.rect.top = top
                bullet.velocity[1] = -bullet.velocity[1]
                bounced = True
            elif bullet.rect.bottom >= bottom and bullet.velocity[1] > 0:
                bullet.rect.bottom = bottom
                bullet.velocity[1] = -bullet.velocity[1]
                bounced = True

            if bounced:
                bullet.bounces += 1
                if bullet.bounces > MAX_BULLET_BOUNCES:
                    self.bullets.remove(bullet)
                else:
                    self.bounce_sound.play()
                    self.sparks.append({
                        "x": bullet.rect.centerx,
                        "y": bullet.rect.centery,
                        "age": 0,
                    })

        for spark in self.sparks[:]:
            spark["age"] += 1
            if spark["age"] > 18:
                self.sparks.remove(spark)
         
 
        now = pygame.time.get_ticks()

        if now >= self.next_potion_time and len(self.potions) < 2:
            self.spawn_potion()
            self.next_potion_time = now + 12000

        for potion in self.potions[:]:
            potion.update()
            if self.player1.health < self.player1.max_health and self.player1.rect.colliderect(potion.rect):
                self.player1.health += 1
                self.potion_sound.play()
                self.sparks.append({
                    "x": potion.rect.centerx,
                    "y": potion.rect.centery,
                    "age": 0,
                })
                self.potions.remove(potion)

        for e in self.enemies[:]:
            if now >= self.invulnerable_until and check_collisions(self.player1, e):
                self.player1.health = max(0, self.player1.health - 1)
                self.eek_sound.play()
                self.invulnerable_until = now + 800
                self.knockback(e)
                self.player1.check_death()
                e.destroy(self.enemies, play_sound=False)
                continue
            for b in self.bullets[:]:
                if check_collisions(e, b):
                    e.take_damage(1, self.enemies)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    if e.health <= 0:
                        self.score += 1
                        self.shake_gen = screen_shake(5, 20)
 
        if self.shake_gen:
            try:
                self.shake_offset = next(self.shake_gen)
            except StopIteration:
                self.shake_gen = None
                self.shake_offset = (0, 0)
 
        self.player1.check_death()
        if not self.player1.alive:
            self.game_over = True
            self.death_screen_done = False
            save_score(self.player_name, self.score)
            self.death_sound.play()
            self.meme_sound.play(loops=-1, fade_ms=400)
            pygame.mixer.music.set_volume(0)
 
        update_particles()
 
 
        if self.cursor_scale > 1:
            self.cursor_scale -= 0.04
            if self.cursor_scale < 1:
                self.cursor_scale = 1
 
 
        self.cursor_rect.center = pygame.mouse.get_pos()
 
    def draw(self):
        if not self.game_over:
            ox, oy = self.shake_offset
            self.screen.blit(self.bg, (ox, oy))
            draw_particles(self.screen, ox, oy)
 
            for enemy in self.enemies:
                enemy.draw(self.screen, ox, oy)
 
            for potion in self.potions:
                potion.draw(self.screen, ox, oy)
 
            for bullet in self.bullets:
                bullet.draw(self.screen, ox, oy)

            for spark in self.sparks:
                radius = 5 + spark["age"]
                alpha = max(0, 240 - spark["age"] * 13)
                ring = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(ring, (255, 235, 150, alpha), (radius + 2, radius + 2), radius, 2)
                self.screen.blit(ring, (spark["x"] - radius - 2 + ox, spark["y"] - radius - 2 + oy))

            now = pygame.time.get_ticks()
            if now >= self.invulnerable_until or (now // 100) % 2 == 0:
                self.player1.draw(self.screen, ox, oy)
 
            self.player1.display_ui(self.screen)
            self.display_score()
 
            scaled_cursor = pygame.transform.scale(self.cursor_img, (int(self.cursor_img.get_width() * self.cursor_scale), int(self.cursor_img.get_height() * self.cursor_scale)))
            rect = scaled_cursor.get_rect(center=pygame.mouse.get_pos())
            self.screen.blit(scaled_cursor, rect)
 
            if self.state_stack:
                self.state_stack[-1].render(self.screen)
 
        
        else:
            self.screen.fill((0, 0, 0))
            pygame.mouse.set_visible(True)

            if not self.death_screen_done:
                line1 = self.big_font.render("CHIPPA SAHAB!", True, (255, 255, 255))
                line2 = self.medium_font.render("yeh chappal from Chippa Sahab", True, (255, 200, 120))
                line3 = self.medium_font.render("skill issue", True, (150, 150, 150))
                skip_text = TEXT_FONT.render("press [SPACE] to continue", True, (110, 110, 110))

                self.screen.blit(line1, line1.get_rect(center=(self.width // 2, self.height // 2 - 60)))
                self.screen.blit(line2, line2.get_rect(center=(self.width // 2, self.height // 2 + 20)))
                self.screen.blit(line3, line3.get_rect(center=(self.width // 2, self.height // 2 + 80)))
                cake_rect = self.chippa_cake.get_rect(center=(self.width // 2, 165))
                self.screen.blit(self.chippa_cake, cake_rect)
                self.screen.blit(skip_text, skip_text.get_rect(center=(self.width // 2, self.height - 60)))
            else:
                game_over_text = TEXT_FONT.render("Game Over!", True, (255, 255, 255))
                sus_text = TEXT_FONT.render("you were ejected (SUS)", True, (170, 170, 170))
                score_text = TEXT_FONT.render(f"Score: {self.score}", True, (255, 255, 255))
                restart_text = TEXT_FONT.render("Press [R] to Restart", True, (255, 255, 255))
                menu_text = TEXT_FONT.render("Press [M] for Main Menu", True, (255, 255, 255))

                self.screen.blit(game_over_text, game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 80)))
                self.screen.blit(sus_text, sus_text.get_rect(center=(self.width // 2, self.height // 2 - 130)))
                self.screen.blit(score_text, score_text.get_rect(center=(self.width // 2, self.height // 2 - 20)))
                self.screen.blit(restart_text, restart_text.get_rect(center=(self.width // 2, self.height // 2 + 40)))
                self.screen.blit(menu_text, menu_text.get_rect(center=(self.width // 2, self.height // 2 + 100)))

        pygame.display.update()

    async def run(self):
        import asyncio

        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
            await asyncio.sleep(0)

        pygame.quit()
