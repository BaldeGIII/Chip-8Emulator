import time
import random

class Chip8:
    def __init__(self):
        # Chip-8 has 4096 bytes of memory
        self.memory = [0] * 4096

        # 16 registers V0 to VF
        self.V = [0] * 16

        # Index register and program counter
        self.I = 0
        self.pc = 0x200 # Program counter starts at 0x200

        # Stack and stack pointer
        self.stack = []
        self.sp = 0

        # Timers
        self.delay_timer = 0
        self.sound_timer = 0

        # Display (64x32 pixels)
        self.display = [0] * 64 * 32

        # Keyboard (16 keys)
        self.keypad = [0] * 16

        # Load fontset into memory
        self.load_fontset()


    def load_fontset(self):
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
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        for i in range(len(fontset)):
            self.memory[i] = fontset[i]

    def emulate_cycle(self):

        # Fetch the next opcode
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]

        # Decode and execute the opcode
        self.execute_opcode(opcode)

        # Update timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def execute_opcode(self, opcode):
        print(f'PC: {self.pc:03X} Opcode: {opcode:04X}')  # Debugging line
        # Extract the first 4 bits of the opcode
        first_nibble = opcode & 0xF000

        if first_nibble == 0x0000:
            if opcode == 0x00E0:
                # 00E0: Clear the display
                self.display = [0] * 64 * 32
            elif opcode == 0x00EE:
                # 00EE: Return from a subroutine
                self.pc = self.stack.pop()
            else:
                print(f'Unknown opcode: {opcode:04X}')
        elif first_nibble == 0x1000:
            # 1NNN: Jump to address NNN
            self.pc = opcode & 0x0FFF
        elif first_nibble == 0x2000:
            # 2NNN: Call subroutine at NNN
            self.stack.append(self.pc)
            self.pc = opcode & 0x0FFF
        elif first_nibble == 0x3000:
            # 3XNN: Skip the next instruction if VX == NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            if self.V[x] == nn:
                self.pc += 2
        elif first_nibble == 0x4000:
            # 4XNN: Skipp the next instruction if VX != NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            if self.V[x] != nn:
                self.pc += 2
        elif first_nibble == 0x5000:
            # 5XY0: Skip the next instruction if VX == VY
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif first_nibble == 0x6000:
            # 6XNN: Set VX to NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.V[x] = nn
        elif first_nibble == 0x7000:
            # 7XNN: Add NN to VX
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.V[x] = (self.V[x] + nn) % 0x0FF
        elif first_nibble == 0x8000:
            # 8XY0: Set VX to the value of VY
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            last_nibble = opcode & 0x000F
            if last_nibble == 0x00:
                # 8XY0: Set VX to the value of VY
                self.V[x] = self.V[y]
            elif last_nibble == 0x1:
                # 8XY1: Set VX to VX | VY
                self.V[x] = self.V[x] | self.V[y]
            elif last_nibble == 0x2:
                # 8XY2: Set VX to VX & VY
                self.V[x] = self.V[x] & self.V[y]
            elif last_nibble == 0x3:
                # 8XY3: Set VX to VX ^ VY
                self.V[x] = self.V[x] ^ self.V[y]
            elif last_nibble == 0x4:
                # 8XY4: Add VY to VX. Set VF to 1 if there's a carry, 0 otherwise if there isn't
                sum = self.V[x] + self.V[y]
                self.V[0xF] = 1 if sum > 0xFF else 0
                self.V[x] = sum % 0xFF
            elif last_nibble == 0x5:
                # 8XY5: Subtract VY from VX. Set VF to 0 if there's a borrow, 1 otherwise if there isn't
                self.V[0xF] = 1 if self.V[x] > self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
            elif last_nibble == 0x6:
                # 8XY6: Shift VX right by one. Set VF to the value of the least significant bit of VX before the shift
                self.V[0xF] = self.V[x] & 0x1
                self.V[x] = self.V[x] >> 1
            elif last_nibble == 0x7:
                # 8XY7: Set VX to VY - VX. Set VF to 0 if there's a borrow, 1 otherwise if there isn't
                self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif last_nibble == 0xE:
                # 8XYE: Shift VX left by one. Set VF to the value of the most significant bit of VX before the shift
                self.V[0xF] = (self.V[x] & 0x80) >> 7
                self.V[x] = (self.V[x] << 1) & 0xFF
        elif first_nibble == 0x9000:
            # 9XY0: Skip the next instruction if VX != VY
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif first_nibble == 0xA000:
            # ANNN: Set I to the address NNN
            self.I = opcode & 0x0FFF
        elif first_nibble == 0xB000:
            # BNNN: Jump to the address NNN + V0
            self.pc = (opcode & 0x0FFF) + self.V[0]
        elif first_nibble == 0xC000:
            # CXNN: Set VX to a random number and NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.V[x] = random.randint(0, 255) & nn
        elif first_nibble == 0xD000:
            # DXYN: Draw a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels
            x = self.V[(opcode & 0x0F00) >> 8]
            y = self.V[(opcode & 0x00F0) >> 4]
            height = opcode & 0x000F
            self.V[0xF] = 0
            for row in range(height):
                sprite = self.memory[self.I + row]
                for col in range(8):
                    if sprite & (0x80 >> col) != 0:
                        if self.display[(x + col + ((y + row) * 64))% len(self.display)] == 1:
                            self.V[0xF] = 1
                        self.display[(x + col + ((y + row)) * 64) % len(self.display)] ^= 1
        elif first_nibble == 0xE000:
            x = (opcode & 0x0F00) >> 8
            if (opcode & 0x00FF) == 0x009E:
                # EX9E: Skip the next instruction if the key stored in VX is pressed
                if self.keypad[self.V[x]] != 0:
                    self.pc += 2
            elif (opcode & 0x00FF) == 0x00A1:
                # EXA1: Skip the next instruction if the key stored in VX isn't pressed
                if self.keypad[self.V[x]] == 0:
                    self.pc += 2
        elif first_nibble == 0xF000:
            x = (opcode & 0x0F00) >> 8
            if (opcode & 0x00FF) == 0x0007:
                # FX07: Set VX to the value of the delay timer
                self.V[x] = self.delay_timer
            elif (opcode & 0x00FF) == 0x000A:
                # FX0A: Wait for a key press, store the value of the key in VX
                key_pressed = False
                for i in range(len(self.keypad)):
                    if self.keypad[i] != 0:
                        self.V[x] = i
                        key_pressed = True
                        break
                if not key_pressed:
                    return
            elif (opcode & 0x00FF) == 0x0015:
                # FX15: Set the delay timer to VX
                self.delay_timer = self.V[x]
            elif (opcode & 0x00FF) == 0x0018:
                # FX18: Set the sound timer to VX
                self.sound_timer = self.V[x]
            elif (opcode & 0x00FF) == 0x001E:
                # FX1E: Add VX to I
                self.I = (self.I + self.V[x]) % 0xFFF
            elif (opcode & 0x00FF) == 0x0029:
                # FX29: Set I to the location of the sprite for the character in VX
                self.I = self.V[x] * 5
            elif (opcode & 0x00FF) == 0x0033:
                # FX33: Store the binary-coded decimal representation of VX at the addresses I, I+1, and I+2
                self.memory[self.I] = self.V[x] // 100
                self.memory[self.I + 1] = (self.V[x] // 10) % 10
                self.memory[self.I + 2] = self.V[x] % 10
            elif (opcode & 0x00FF) == 0x0055:
                # FX55: Store registers V0 to VX in memory starting at address I
                for i in range(x + 1):
                    self.memory[self.I + i] = self.V[i]
            elif (opcode & 0x00FF) == 0x0065:
                # FX65: Read registers V0 to VX from memory starting at address I
                for i in range(x + 1):
                    self.V[i] = self.memory[self.I + i]
        else:
            print(f'Unknown opcode: {opcode:04X}')

        if first_nibble != 0x1000 and opcode != 0x00EE:
            self.pc += 2

    def load_rom(self, rom_file):
        with open(rom_file, 'rb') as f:
            rom_data = f.read()
            for i in range(len(rom_data)):
                self.memory[0x200 + i] = rom_data[i]

chip8 = Chip8()
chip8.load_rom('Roms/Space Invaders [David Winter].ch8')
while True:
    chip8.emulate_cycle()
    time.sleep(1/60)