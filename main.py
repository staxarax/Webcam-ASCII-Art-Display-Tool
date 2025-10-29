# main.py
import cv2
import numpy as np
import shutil
import os
import time
import argparse

# ASCII文字セット（暗→明）。必要なら変更してください。
# ASCII_CHARS = "@MW#8B%$&WM8ZO0QLCJUYXcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\^`'. " # length 40+
ASCII_CHARS = "@%#W$9876543210?!abc;:+=-,. "  # length 20
# ASCII_CHARS = "@%#*+=-:. "  # length 10
# ASCII_CHARS = "@#*:-"     # length 5
# ASCII_CHARS = "#=:. "

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def image_to_ascii(image, width=100, invert=False, ascii_chars=ASCII_CHARS):
    """
    image: 2D numpy array (grayscale, dtype uint8)
    width: 出力文字幅
    invert: Trueなら白黒反転
    ascii_chars: 文字列（暗→明）
    """
    if invert:
        image = cv2.bitwise_not(image)

    # 元画像の形状
    h, w = image.shape
    if w == 0:
        return ""

    # アスペクト比考慮して高さ計算（1文字が縦長のため補正係数0.55）
    aspect_ratio = h / w
    new_height = max(1, int(aspect_ratio * width * 0.55))  # 最低1行は確保
    # リサイズ（INTER_AREAは縮小時に良好）
    resized = cv2.resize(image, (width, new_height), interpolation=cv2.INTER_AREA)

    # NumPyで線形マッピング: 0..255 -> 0..(N-1)
    n_chars = len(ascii_chars)
    # floatで計算して範囲内に丸める（端点255が確実に最後の文字に対応）
    indices = np.floor(resized.astype(np.float32) * (n_chars - 1) / 255.0).astype(np.int32)
    # safety clamp
    indices = np.clip(indices, 0, n_chars - 1)

    # 文字配列を作る
    char_array = np.array(list(ascii_chars))
    mapped = char_array[indices]  # shape (new_height, width), dtype '<U1'

    # 各行を結合して1つの文字列にする
    lines = ["".join(row) for row in mapped.tolist()]
    ascii_image = "\n".join(lines)
    return ascii_image

def get_terminal_size():
    return shutil.get_terminal_size((80, 20))

def main():
    parser = argparse.ArgumentParser(description="Webカメラ映像をASCIIアートでリアルタイム表示するツール（Windows対応）")
    parser.add_argument("--device", type=int, default=0,
                        help="使用するカメラインデックス（例: 0, 1, 2 ...）")
    parser.add_argument("--width", type=int, default=100,
                        help="ASCIIアートの横幅（デフォルト: 100）")
    parser.add_argument("--invert", action="store_true",
                        help="白黒反転モードを有効にする")
    parser.add_argument("--ascii", type=str, default=ASCII_CHARS,
                        help="使用するASCII文字列（暗→明）。例: '@%#*+=-:. '")
    parser.add_argument("--fps", type=float, default=30.0,
                        help="出力フレームレートの上限（デフォルト 30.0）")
    args = parser.parse_args()

    # WindowsではCAP_DSHOWを指定して安定化
    # NOTE: os.name == 'nt' でWindows
    backend = cv2.CAP_DSHOW if os.name == 'nt' else 0
    cap = cv2.VideoCapture(args.device, backend)

    if not cap.isOpened():
        print("カメラデバイス {args.device} を開けませんでした。")
        print("  対処法:")
        print("  1. カメラが他のアプリで使用中でないか確認（Zoom/OBS/Teams等）")
        print("  2. デバイス番号を変更して試す（--device 1 など）")
        print("  3. 別のUSBポートに接続 or 再起動")
        print("  4. OpenCVを更新: pip install -U opencv-python")
        return

    frame_interval = 1.0 / max(1.0, args.fps)
    try:
        last_time = 0.0
        while True:
            now = time.time()
            if now - last_time < frame_interval:
                time.sleep(max(0.0, frame_interval - (now - last_time)))
            last_time = time.time()

            ret, frame = cap.read()
            if not ret or frame is None:
                print("フレームを取得できませんでした。カメラ接続を確認してください。")
                # すぐにループを抜けず、少し待って再試行する（短時間の接続ロス対策）
                time.sleep(0.1)
                continue

            # グレースケール化・エッジ検出
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            # ターミナル幅と指定幅を比較して決定
            term_width, _ = get_terminal_size()
            width = min(args.width, term_width, 200)  # 上限を200に制限

            ascii_art = image_to_ascii(edges, width=width, invert=args.invert, ascii_chars=args.ascii)

            clear_terminal()
            print(ascii_art)

    except KeyboardInterrupt:
        print("\n終了します。")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
