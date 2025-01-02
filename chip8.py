import pygame
import time
import random

class Chip8:
    def __init__(self):
        # System memory and configuration
        self.DISPLAY_WIDTH = 64  # Standard CHIP-8 display width
        self.DISPLAY_HEIGHT = 32  # Standard CHIP-8 display height
        self.FONTSET_START_ADDRESS = 0x50  # Memory location where font data starts

        # Initialize memory and registers
        self.memory = bytearray(4096)  # 4K memory
        self.V = bytearray(16)  # 16 8-bit general purpose registers V0-VF
        self.I = 0  # 16-bit index register
        self.pc = 0x200  # Program counter (starts at 0x200)
        self.stack = []  # Stack for storing return addresses

        # Timers
        self.delay_timer = 0  # Delay timer (60Hz)
        self.sound_timer = 0  # Sound timer (60Hz)

        # Display and input
        self.display = [0] * (self.DISPLAY_WIDTH * self.DISPLAY_HEIGHT)  # Display buffer
        self.keypad = [0] * 16  # Hexadecimal keypad (0x0-0xF)
        self.draw_flag = False  # Indicates if screen should be redrawn
        self.waiting_for_key = False  # Flag for key input operations
        self.key_register = 0  # Register waiting for key input

        # Keymap
        self.keymap = {
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

        # Initialize sound
        pygame.mixer.init()
        self.beep_sound = pygame.mixer.Sound('beep.wav')

        # Initialize system
        self.load_fontset()

    def load_fontset(self):
        # Each character is 5 bytes
        fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]
        # Load fontset into memory starting at FONTSET_START_ADDRESS
        for i, byte in enumerate(fontset):
            self.memory[self.FONTSET_START_ADDRESS + i] = byte

    def load_rom(self, rom_file):
        """Load ROM file into memory starting at address 0x200"""
        try:
            with open(rom_file, 'rb') as f:
                rom_data = f.read()
                for i, byte in enumerate(rom_data):
                    if 0x200 + i < len(self.memory):
                        self.memory[0x200 + i] = byte
        except Exception as e:
            print(f"Error loading ROM: {e}")
            raise

    def emulate_cycle(self):
        """Emulate one CPU cycle"""
        if self.waiting_for_key:
            return

        # Fetch opcode - two bytes combined into one 16-bit opcode
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        # Execute the opcode
        self.execute_opcode(opcode)

        # Update timers at 60Hz
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            if self.sound_timer == 1:
                self.beep_sound.play()  # Play sound
            self.sound_timer -= 1

    def execute_opcode(self, opcode):
        """Execute CHIP-8 opcode"""
        # Extract common values from opcode
        x = (opcode & 0x0F00) >> 8  # Second nibble - used as register identifier
        y = (opcode & 0x00F0) >> 4  # Third nibble - used as register identifier
        n = opcode & 0x000F  # Fourth nibble - often used as a 4-bit number
        nn = opcode & 0x00FF  # Last two nibbles - often used as an 8-bit immediate number
        nnn = opcode & 0x0FFF  # Last three nibbles - often used as a memory address

        # Get the first nibble to determine instruction type
        first_nibble = opcode & 0xF000

        # Instruction implementations
        if first_nibble == 0x0000:
            if opcode == 0x00E0:  # 00E0: Clear screen
                self.display = [0] * (self.DISPLAY_WIDTH * self.DISPLAY_HEIGHT)
                self.draw_flag = True
                self.pc += 2
            elif opcode == 0x00EE:  # 00EE: Return from subroutine
                if self.stack:
                    self.pc = self.stack.pop()
                self.pc += 2

        elif first_nibble == 0x1000:  # 1NNN: Jump to address NNN
            self.pc = nnn

        elif first_nibble == 0x2000:  # 2NNN: Call subroutine at NNN
            self.stack.append(self.pc)
            self.pc = nnn

        elif first_nibble == 0x3000:  # 3XNN: Skip next instruction if VX equals NN
            self.pc += 4 if self.V[x] == nn else 2

        elif first_nibble == 0x4000:  # 4XNN: Skip next instruction if VX doesn't equal NN
            self.pc += 4 if self.V[x] != nn else 2

        elif first_nibble == 0x5000:  # 5XY0: Skip next instruction if VX equals VY
            self.pc += 4 if self.V[x] == self.V[y] else 2

        elif first_nibble == 0x6000:  # 6XNN: Set VX to NN
            self.V[x] = nn
            self.pc += 2

        elif first_nibble == 0x7000:  # 7XNN: Add NN to VX (carry flag not changed)
            self.V[x] = (self.V[x] + nn) & 0xFF
            self.pc += 2

        elif first_nibble == 0x8000:  # 8XYN: Arithmetic and logical operations
            if n == 0x0:  # 8XY0: Set VX to value of VY
                self.V[x] = self.V[y]
            elif n == 0x1:  # 8XY1: Set VX to VX OR VY
                self.V[x] |= self.V[y]
            elif n == 0x2:  # 8XY2: Set VX to VX AND VY
                self.V[x] &= self.V[y]
            elif n == 0x3:  # 8XY3: Set VX to VX XOR VY
                self.V[x] ^= self.V[y]
            elif n == 0x4:  # 8XY4: Add VY to VX with carry flag
                result = self.V[x] + self.V[y]
                self.V[0xF] = 1 if result > 0xFF else 0  # Set carry flag
                self.V[x] = result & 0xFF
            elif n == 0x5:  # 8XY5: Subtract VY from VX with borrow flag
                self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0  # Set NOT borrow flag
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
            elif n == 0x6:  # 8XY6: Shift VX right, store LSB in VF
                self.V[0xF] = self.V[x] & 0x1  # Store LSB in VF
                self.V[x] >>= 1
            elif n == 0x7:  # 8XY7: Set VX to VY minus VX with borrow flag
                self.V[0xF] = 1 if self.V[y] >= self.V[x] else 0  # Set NOT borrow flag
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif n == 0xE:  # 8XYE: Shift VX left, store MSB in VF
                self.V[0xF] = (self.V[x] & 0x80) >> 7  # Store MSB in VF
                self.V[x] = (self.V[x] << 1) & 0xFF
            self.pc += 2

        elif first_nibble == 0x9000:  # 9XY0: Skip next instruction if VX doesn't equal VY
            self.pc += 4 if self.V[x] != self.V[y] else 2

        elif first_nibble == 0xA000:  # ANNN: Set index register I to NNN
            self.I = nnn
            self.pc += 2

        elif first_nibble == 0xB000:  # BNNN: Jump to address NNN + V0
            self.pc = nnn + self.V[0]

        elif first_nibble == 0xC000:  # CXNN: Set VX to random number AND NN
            self.V[x] = random.randint(0, 255) & nn
            self.pc += 2

        elif first_nibble == 0xD000:  # DXYN: Draw sprite at (VX, VY) with height N
            x_coord = self.V[x] % self.DISPLAY_WIDTH
            y_coord = self.V[y] % self.DISPLAY_HEIGHT
            self.V[0xF] = 0  # Reset collision flag

            # Loop through each row of the sprite
            for row in range(n):
                if y_coord + row >= self.DISPLAY_HEIGHT:
                    break

                sprite_byte = self.memory[self.I + row]

                # Loop through each bit in the sprite byte
                for col in range(8):
                    if x_coord + col >= self.DISPLAY_WIDTH:
                        break

                    # If current bit is 1, draw/erase the pixel
                    if sprite_byte & (0x80 >> col):
                        pixel_pos = (y_coord + row) * self.DISPLAY_WIDTH + (x_coord + col)
                        if self.display[pixel_pos] == 1:
                            self.V[0xF] = 1  # Set collision flag
                        self.display[pixel_pos] ^= 1  # XOR pixel

            self.draw_flag = True
            self.pc += 2

        elif first_nibble == 0xE000:
            if nn == 0x9E:  # EX9E: Skip next instruction if key VX is pressed
                self.pc += 4 if self.keypad[self.V[x]] else 2
            elif nn == 0xA1:  # EXA1: Skip next instruction if key VX is not pressed
                self.pc += 4 if not self.keypad[self.V[x]] else 2

        elif first_nibble == 0xF000:
            if nn == 0x07:  # FX07: Set VX to value of delay timer
                self.V[x] = self.delay_timer
                self.pc += 2
            elif nn == 0x0A:  # FX0A: Wait for key press, store key value in VX
                key_pressed = False
                for i in range(16):
                    if self.keypad[i]:
                        self.V[x] = i
                        key_pressed = True
                        break
                if not key_pressed:
                    return  # Try again next cycle
                self.pc += 2
            elif nn == 0x15:  # FX15: Set delay timer to VX
                self.delay_timer = self.V[x]
                self.pc += 2
            elif nn == 0x18:  # FX18: Set sound timer to VX
                self.sound_timer = self.V[x]
                self.pc += 2
            elif nn == 0x1E:  # FX1E: Add VX to I
                self.I = (self.I + self.V[x]) & 0xFFF
                self.pc += 2
            elif nn == 0x29:  # FX29: Set I to location of sprite for character in VX
                self.I = self.FONTSET_START_ADDRESS + (self.V[x] * 5)
                self.pc += 2
            elif nn == 0x33:  # FX33: Store BCD representation of VX in memory locations I, I+1, and I+2
                self.memory[self.I] = self.V[x] // 100
                self.memory[self.I + 1] = (self.V[x] // 10) % 10
                self.memory[self.I + 2] = self.V[x] % 10
                self.pc += 2
            elif nn == 0x55:  # FX55: Store registers V0 through VX in memory starting at I
                for i in range(x + 1):
                    self.memory[self.I + i] = self.V[i]
                self.pc += 2
            elif nn == 0x65:  # FX65: Read registers V0 through VX from memory starting at I
                for i in range(x + 1):
                    self.V[i] = self.memory[self.I + i]
                self.pc += 2

    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key in self.keymap:
                    self.keypad[self.keymap[event.key]] = 1
            elif event.type == pygame.KEYUP:
                if event.key in self.keymap:
                    self.keypad[self.keymap[event.key]] = 0
        return True