import pygame
import time
from chip8 import Chip8

def draw_display(screen, display):
    pixel_array = pygame.PixelArray(screen)
    for y in range(32):
        for x in range(64):
            color = (255, 255, 255) if display[y * 64 + x] == 1 else (0, 0, 0)
            pixel_array[x * 10:(x + 1) * 10, y * 10:(y + 1) * 10] = color
    del pixel_array

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 320))
    pygame.display.set_caption("Chip-8 Emulator")
    clock = pygame.time.Clock()
    chip8 = Chip8()
    chip8.load_rom('Roms/INVADERS')

    running = True
    while running:
        running = chip8.handle_input()

        # Emulate multiple cycles per frame to keep up with the 60Hz refresh rate
        for _ in range(10):
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