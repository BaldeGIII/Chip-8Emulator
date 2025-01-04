# Chip-8 Emulator

This is a Chip-8 emulator written in Python using Pygame.

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/Chip8-Emulator.git
    cd Chip8-Emulator
    ```

2. **Create a virtual environment:**

    ```sh
    python -m venv .venv
    ```

3. **Activate the virtual environment:**

    - On Windows:

        ```sh
        .venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```sh
        source .venv/bin/activate
        ```

4. **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

## Running the Emulator

1. **Run the emulator:**

    ```sh
    python main.py
    ```

2. **Load a ROM:**

    - Click on `File` > `Load ROM` to open the file explorer and select a `.ch8` ROM file.

## Creating a Beep Sound

If you don't have a `beep.wav` file, you can create one using Audacity or download one from a free sound website.

### Using Audacity:

1. **Download and Install Audacity**: [Audacity Download](https://www.audacityteam.org/download/)
2. **Generate a Tone**:
    - Open Audacity.
    - Go to `Generate` > `Tone...`.
    - Set the frequency to 440 Hz and duration to 1 second.
    - Click `OK`.
3. **Export the File**:
    - Go to `File` > `Export` > `Export as WAV`.
    - Save the file as `beep.wav` in the project directory.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
