# Webcam ASCII Art Display Tool

This program displays your webcam feed as ASCII art in the command line interface (CLI).

＝＝＝＝＝＝＝＝＝＝＝＝＝＝

## Requirements

- OS: Windows 10 or later  
- Python: 3.x or later  
- Webcam: Any standard USB camera  
- CPU/GPU: No special requirements  

＝＝＝＝＝＝＝＝＝＝＝＝＝＝

## Installation

1. Install Python.
2. Install the required libraries:

pip install opencv-python
pip install numpy

＝＝＝＝＝＝＝＝＝＝＝＝＝＝

Usage

Open Command Prompt or PowerShell

Navigate to the directory containing main.py and run:

python main.py


To stop the program, press Ctrl + C or the Pause/Break key

＝＝＝＝＝＝＝＝＝＝＝＝＝＝

Notes

Without specifying arguments, the program cannot automatically detect the camera device.

Try device indexes starting from 0.

＝＝＝＝＝＝＝＝＝＝＝＝＝＝

Command-line Arguments

| Argument   | Description                              |
| ---------- | ---------------------------------------- |
| `--device` | Camera device index to use               |
| `--width`  | Width of the ASCII art                   |
| `--invert` | Enable inverted black-and-white mode     |
| `--ascii`  | Custom ASCII characters to use           |
| `--fps`    | Maximum output frame rate (default 30.0) |

＝＝＝＝＝＝＝＝＝＝＝＝＝＝

Purpose

Displays your webcam feed as ASCII art in PowerShell or Command Prompt

Streaming or other usage should be done at your own responsibility

＝＝＝＝＝＝＝＝＝＝＝＝＝＝

# Examples

Default example
python main.py --device 5 --fps 60 --width 300

Inverted colors + custom ASCII characters
python main.py --device 5 --fps 60 --width 300 --invert --ascii "@MW#8B%$&WM8ZO0QLCJUYXcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\^`'. "

Full path example:
C:\Users\username\PycharmProjects\webcam_AA>python main.py --device 5 --fps 60 --width 300 --invert --ascii "@MW#8B%$&WM8ZO0QLCJUYXcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\^`'. "

＝＝＝＝＝＝＝＝＝＝＝＝＝＝

Use Case

A simple tool to display webcam feed as ASCII art in CLI (PowerShell or Command Prompt)

Any streaming or other usage is at the user's own responsibility

＝＝＝＝＝＝＝＝＝＝＝＝＝＝
Disclaimer

This program is provided "as-is"

The author is not responsible for any damages caused by the program (data loss, hardware damage, or other issues)

Use at your own risk

Commercial use or streaming is also at the user's own responsibility

## License / ライセンス

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

本プロジェクトは **MITライセンス** のもとで配布されています。  
詳細については [LICENSE](./LICENSE) ファイルをご確認ください。

---

### Third-Party Components / サードパーティーコンポーネント

This software uses the following third-party libraries:

本ソフトウェアでは以下のサードパーティーライブラリを使用しています。

- **OpenCV-Python** — Licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)
- **NumPy** — Licensed under the [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause)

License texts are included in the `third_party/` directory.  
ライセンス文は `third_party/` ディレクトリに同梱しています。

---

### Summary / 概要

You are free to use, modify, and distribute this software for personal or commercial purposes,  
as long as you comply with the terms of the MIT License and the licenses of third-party components used.

本ソフトウェアは、MITライセンスおよび使用しているサードパーティーライブラリのライセンス条件に従う限り、  
個人・商用を問わず、自由に使用・改変・再配布することができます。