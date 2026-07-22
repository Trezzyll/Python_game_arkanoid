import pygame
import random
import settings as cfg
from screens.game_screen import run as game_screen
from game.entities import Paddle, Brick, Ball, PowerUp
from game.level import load_level

def _bounce_off_rect(ball: Ball, rect: pygame.Rect):
    """ Checks if the Ball collides with the given rect. """

    # Calculate ball's overlaps and find the smallest one
    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top

    min_overlap = min(
        overlap_bottom,
        overlap_left,
        overlap_right,
        overlap_top)
    
    # Calculate the Ball's final velocities
    if min_overlap == overlap_top and ball.vy > 0:
        print('top')
        ball.rect.bottom = rect.top
        ball.vy *= -1
    elif min_overlap == overlap_bottom and ball.vy < 0:
        print('bottom')

        ball.rect.top = rect.bottom
        ball.vy *= -1
    elif min_overlap == overlap_left and ball.vx > 0:
        print('left')

        ball.rect.right = rect.left
        ball.vx *= -1
    elif min_overlap == overlap_right and ball.vx < 0:
        print('right')

        ball.rect.left = rect.right
        ball.vx *= -1

def _handle_ball_vs_bricks(
    ball: Ball,
    bricks: list[Brick],
    powerups,
    hit_sound,
) -> int:

    scored = 0
    for brick in bricks[:]:  
        if not ball.rect.colliderect(brick.rect):
            continue
        _bounce_off_rect(ball, brick.rect)
        if brick.hp == -1: 
            continue
        brick.hit()

        if brick.hp <= 0:
            hit_sound.play()
            if random.random() < cfg.BONUS_PROBABILITY:
                bonus_type = random.choice(cfg.BONUS_TYPES)

                powerups.append(
                    PowerUp(
                        brick.rect.centerx,
                        brick.rect.centery,
                        bonus_type
                    )
                )

            bricks.remove(brick)
            scored += 10
    return scored
def _handle_ball_vs_paddle(ball: Ball, paddle: Paddle, hit_sound) -> None:
    """ Handles Ball bounce over the Paddle. """
    hit_sound.play()
    _bounce_off_rect(ball, paddle.rect)
    offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
    max_vx = cfg.MAX_BALL_SPEED_X
    ball.vx = max(-max_vx, min(max_vx, offset * max_vx))

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid")
    pygame.mixer.music.load("assets/music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop forever
    hit_sound = pygame.mixer.Sound("assets/hit.mp3")
    bonus_sound = pygame.mixer.Sound("assets/bonus.mp3")
    clock = pygame.time.Clock()

    running = True
    paddle = Paddle()

    bricks, rows, cols = load_level(1)
    ball = Ball(cfg.WIDTH // 2, cfg.HEIGHT - 80)

    powerups = []

    shrink_end_time = 0
    NORMAL_PADDLE_WIDTH = cfg.PADDLE_WIDTH
    SHRUNK_PADDLE_WIDTH = 60

    muted = False

    mute_button = pygame.Rect(cfg.WIDTH - 110, 10, 90, 35)
    button_font = pygame.font.SysFont(None, 28)
    title_font = pygame.font.SysFont(None, 72)

    while running:
        # Main Loop
        screen.fill(cfg.BLACK)

        # Update Section
        keys = pygame.key.get_pressed()

        paddle.move(keys)
        if (
                shrink_end_time > 0
                and pygame.time.get_ticks() >= shrink_end_time
                and paddle.rect.width != NORMAL_PADDLE_WIDTH
        ):
            center = paddle.rect.centerx
            paddle.rect.width = NORMAL_PADDLE_WIDTH
            paddle.rect.centerx = center
            shrink_end_time = 0

        _handle_ball_vs_bricks(ball, bricks, powerups, hit_sound)

        # Win condition
        remaining = [brick for brick in bricks if brick.hp > 0]

        if len(remaining) == 0:
            text = title_font.render("YOU WIN!", True, (0, 255, 0))

            screen.blit(
                text,
                (
                    cfg.WIDTH // 2 - text.get_width() // 2,
                    cfg.HEIGHT // 2 - text.get_height() // 2,
                ),
            )

            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

        if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
            _handle_ball_vs_paddle(ball, paddle, hit_sound)

        for brick in bricks:
            brick.draw(screen)

        ball.update()
        # Lose condition
        if ball.rect.bottom >= cfg.HEIGHT:
            text = title_font.render("GAME OVER", True, (255, 0, 0))

            screen.blit(
                text,
                (
                    cfg.WIDTH // 2 - text.get_width() // 2,
                    cfg.HEIGHT // 2 - text.get_height() // 2,
                ),
            )

            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

        # Update powerups
        for powerup in powerups[:]:
            powerup.update()

            if powerup.rect.colliderect(paddle.rect):

                if powerup.type == "shrink":
                    center = paddle.rect.centerx
                    paddle.rect.width = SHRUNK_PADDLE_WIDTH
                    paddle.rect.centerx = center

                    shrink_end_time = pygame.time.get_ticks() + 10000

                elif powerup.type == "speed_up":
                    ball.vx *= 1.3
                    ball.vy *= 1.3

                    if abs(ball.vx) > 10:
                        ball.vx = 10 if ball.vx > 0 else -10

                    if abs(ball.vy) > 10:
                        ball.vy = 10 if ball.vy > 0 else -10

                elif powerup.type == "speed_down":
                    ball.vx *= 0.7
                    ball.vy *= 0.7

                    if abs(ball.vx) < 2:
                        ball.vx = 2 if ball.vx > 0 else -2

                    if abs(ball.vy) < 2:
                        ball.vy = 2 if ball.vy > 0 else -2
                bonus_sound.play()
                powerups.remove(powerup)

            elif powerup.rect.top > cfg.HEIGHT:
                powerups.remove(powerup)


        # Draw Section
        paddle.draw(screen)
        ball.draw(screen)

        for powerup in powerups:
            powerup.draw(screen)

        # Draw mute button
        pygame.draw.rect(screen, (70, 70, 70), mute_button, border_radius=8)

        text = "Mute" if not muted else "Unmute"
        label = button_font.render(text, True, (255, 255, 255))

        screen.blit(
            label,
            (
                mute_button.centerx - label.get_width() // 2,
                mute_button.centery - label.get_height() // 2,
            ),
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if mute_button.collidepoint(event.pos):

                    muted = not muted

                    if muted:
                        pygame.mixer.music.set_volume(0)
                        hit_sound.set_volume(0)
                        bonus_sound.set_volume(0)
                    else:
                        pygame.mixer.music.set_volume(0.5)
                        hit_sound.set_volume(1)
                        bonus_sound.set_volume(1)

        pygame.display.flip()   # Screen Update
        clock.tick(cfg.FPS)         # FPS (Frames Per Second)

    pygame.quit()

if __name__ == "__main__":
    main()
