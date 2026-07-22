import pygame


def ApplyBonus(powerup, paddle, ball):
    """
    Applies the effect of a collected power-up.
    """

    if powerup.type == "shrink":
        center = paddle.rect.centerx
        paddle.rect.width = 60
        paddle.rect.centerx = center
        return True

    elif powerup.type == "speed_up":
        ball.vx *= 1.3
        ball.vy *= 1.3

        if abs(ball.vx) > 10:
            ball.vx = 10 if ball.vx > 0 else -10

        if abs(ball.vy) > 10:
            ball.vy = 10 if ball.vy > 0 else -10
        return False

    elif powerup.type == "speed_down":
        ball.vx *= 0.7
        ball.vy *= 0.7

        if abs(ball.vx) < 2:
            ball.vx = 2 if ball.vx > 0 else -2

        if abs(ball.vy) < 2:
            ball.vy = 2 if ball.vy > 0 else -2
        return False
    return False