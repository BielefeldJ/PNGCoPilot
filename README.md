# PNGCoPilot

PNGCoPilot is a PNGTuber-like overlay designed for use with EDCoPilot, providing a visual representation of speech activity during gameplay.

## Features

- Displays an animated PNG avatar that reacts to speech detected in EDCoPilot.
- Supports idle and talking states with configurable images.
- Drag-and-drop repositioning and scaling support.
- Persistent settings storage.
- Animated shake effect when speaking.
- Keyboard shortcuts for lock, close, and scaling.

## Installation

### 1. Download the Latest Release
Go to the [Releases](https://github.com/BielefeldJ/PNGCoPilot/releases) section of the repository and download the latest `.exe` file.

### 2. Place PNG Files
Ensure that `idle.png` and `talk.png` are placed in the same folder as the `.exe` file.

### 3. First Run
On the first run, a default config file is generated. You don't need to change anything if:
  - the 2 PNGs are in the same folder as the exe
  - the 2 PNGs are named `talk.png` and `idle.png`
  - EDCoPilot is installed at `C:\EDCoPilot`

## Usage

### 1. Start PNGCoPilot
Double-click the downloaded `.exe` file to start the overlay.

### 2. Keyboard Shortcuts
- `L` - Lock/unlock the overlay position.
- `Q` - Close the overlay.
- `S` - Mirrows the overlay.
- `+` - Scale the overlay up.
- `-` - Scale the overlay down.

### 3. Drag-and-Drop Support
- Click and drag to move the overlay when unlocked.

## Configuration

PNGCoPilot uses a `config.ini` file for customizable settings. If the file does not exist, it will be created with default values upon first run. The following options can be configured manually:

### OverlaySettings
- `idle_image_path`: Path to the idle state PNG image. *(Default: `idle.png`)*
- `talking_image_path`: Path to the talking state PNG image. *(Default: `talk.png`)*
- `scaling_factor`: Scale adjustment factor when resizing. *(Default: `1.1`)*
- `shake_intensity`: Strength of the shake effect when talking. *(Default: `2`)*
- `talking_start_offset`: Delay (seconds) before switching to the talking image. *(Default: `0.3`)*
- `talking_stop_offset`: Delay (seconds) before switching back to idle. *(Default: `0.3`)*

### EDCoPilotSettings
- `edcopilot_dir`: Path to the EDCoPilot installation directory. *(Default: `C:\EDCoPilot`)*
- `character`: The name of the character that should trigger the talking animation. *(Default: `<EDCoPilot>`)*

## Integration with EDCoPilot

The overlay listens for speech events from EDCoPilot. Ensure that:
- EDCoPilot is installed and running.
- The `edcopilot_dir` is correctly set in the configuration.

## License
This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for details.

