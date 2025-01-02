import pygame
import time
from chip8 import Chip8

def draw_display(screen, display):
    for y in range(32):
        for x in range(64):
            color = (255, 255, 255) if display[y * 64 + x] == 1 else (0, 0, 0)
            pygame.draw.rect(screen, color, (x * 10, y * 10, 10, 10))

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 320))
    pygame.display.set_caption("Chip-8 Emulator")
    clock = pygame.time.Clock()
    chip8 = Chip8()
    chip8.load_rom('Roms/INVADERS')

    # Set up the key map
    keymap = {
        pygame.K_1: 0x01,
        pygame.K_2: 0x02,
        pygame.K_3: 0x03,
        pygame.K_4: 0x0C,
        pygame.K_q: 0x04,
        pygame.K_w: 0x05,
        pygame.K_e: 0x06,
        pygame.K_r: 0x0D,
        pygame.K_a: 0x07,
        pygame.K_s: 0x08,
        pygame.K_d: 0x09,
        pygame.K_f: 0x0E,
        pygame.K_z: 0x0A,
        pygame.K_x: 0x00,
        pygame.K_c: 0x0B,
        pygame.K_v: 0x0F
    }

    keyboard_cache = [0] * 16
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in keymap:
                    keyboard_cache[keymap[event.key]] = 1
            elif event.type == pygame.KEYUP:
                if event.key in keymap:
                    keyboard_cache[keymap[event.key]] = 0

        chip8.keypad = keyboard_cache

        chip8.emulate_cycle()
        if chip8.draw_flag:
            screen.fill((0, 0, 0))
            draw_display(screen, chip8.display)
            pygame.display.flip()
            chip8.draw_flag = False

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()