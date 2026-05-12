"""
Webcam ASCII Art Display Tool
案A+C: 差分行描画 + 同期出力モード（\033[?2026h）によるちらつき防止
"""

import cv2
import numpy as np
import shutil
import os
import time
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple, List

# ============================================================
# デフォルト設定
# ============================================================
DEFAULTS = {
    "device": 0,
    "width": 100,
    "invert": False,
    "fps": 30.0,
    "ascii_chars": "@%#W$9876543210?!abc;:+=-,. ",
    "color": "white",
    "diff_color": "green",
    "diff_threshold": 255,
    "canny_low": 50,
    "canny_high": 150,
    "skip_frames": False,
}

# ============================================================
# ANSIエスケープ定数
# ============================================================
ANSI_RESET        = "\033[0m"
ANSI_CURSOR_HOME  = "\033[H"
ANSI_CURSOR_HIDE  = "\033[?25l"
ANSI_CURSOR_SHOW  = "\033[?25h"
ANSI_SYNC_START   = "\033[?2026h"   # 同期出力モード開始（描画完了まで画面更新を保留）
ANSI_SYNC_END     = "\033[?2026l"   # 同期出力モード終了（ここで一括反映）
ANSI_ERASE_LINE   = "\033[2K"       # 行全体を消去
ANSI_CURSOR_COL1  = "\033[1G"       # カーソルを列1に移動

# プリセットカラー
PRESET_COLORS = {
    "white":   ("\033[37m",  "\033[97m"),
    "green":   ("\033[32m",  "\033[92m"),
    "cyan":    ("\033[36m",  "\033[96m"),
    "yellow":  ("\033[33m",  "\033[93m"),
    "red":     ("\033[31m",  "\033[91m"),
    "blue":    ("\033[34m",  "\033[94m"),
    "magenta": ("\033[35m",  "\033[95m"),
}



# ============================================================
# Windows VT有効化
# ============================================================
def enable_windows_vt():
    """WindowsコンソールでANSIエスケープを有効化する。"""
    if os.name != "nt":
        return
    try:
        import ctypes
        import ctypes.wintypes as wt
        k32 = ctypes.windll.kernel32
        handle = k32.GetStdHandle(wt.DWORD(-11))
        mode = wt.DWORD()
        if k32.GetConsoleMode(handle, ctypes.byref(mode)):
            k32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


# ============================================================
# カラー文字列解析
# ============================================================
def parse_color(color_str: str) -> Tuple[str, str]:
    """(通常ANSIコード, 明るいANSIコード) を返す。"""
    s = color_str.strip().lower()
    if s in PRESET_COLORS:
        return PRESET_COLORS[s]
    parts = s.split(",")
    if len(parts) == 3:
        try:
            r, g, b = [max(0, min(255, int(p.strip()))) for p in parts]
            rb, gb, bb = min(255, r+60), min(255, g+60), min(255, b+60)
            return (
                "\033[38;2;{};{};{}m".format(r, g, b),
                "\033[38;2;{};{};{}m".format(rb, gb, bb),
            )
        except ValueError:
            pass
    sys.stderr.write("[警告] カラー '{}' を解釈できません。white を使用します。\n".format(color_str))
    return PRESET_COLORS["white"]


# ============================================================
# 設定ファイル（JSONC対応）
# ============================================================
def _strip_jsonc(text: str) -> str:
    """// コメント・/* */コメント・末尾カンマを除去して純粋なJSONにする。"""
    PATTERN = re.compile(
        r'"(?:[^"\\]|\\.)*"'   # 文字列リテラル（優先）
        r'|(/\*.*?\*/)'         # /* */ ブロックコメント
        r'|(//[^\n]*)',         # // 行コメント
        re.DOTALL,
    )
    def replacer(m):
        if m.group(0).startswith('"'):
            return m.group(0)   # 文字列リテラルはそのまま
        return ""               # コメントは除去
    result = PATTERN.sub(replacer, text)
    result = re.sub(r',(\s*[}\]])', r'\1', result)  # 末尾カンマ除去
    return result


def load_config(config_path: Path) -> dict:
    """JSONC形式の設定ファイルを読み込む。存在しなければ空dictを返す。"""
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = f.read()
        clean = _strip_jsonc(raw)
        data  = json.loads(clean)
        sys.stdout.write("[情報] 設定ファイルを読み込みました: {}\n".format(config_path))
        sys.stdout.flush()
        return data
    except json.JSONDecodeError as e:
        # パース失敗時は問題箇所前後を表示してデバッグを助ける
        try:
            pos     = e.pos
            snippet = clean[max(0, pos-40): pos+40]
            sys.stderr.write("[警告] config.json パース失敗: {}\n".format(e))
            sys.stderr.write("       問題箇所前後: {}\n".format(repr(snippet)))
        except Exception:
            sys.stderr.write("[警告] config.json パース失敗: {}\n".format(e))
        sys.stderr.write("       デフォルト設定で続行します。\n")
        return {}
    except Exception as e:
        sys.stderr.write("[警告] config.json 読み込み失敗: {}\n".format(e))
        return {}


def build_config(file_config: dict, args) -> dict:
    """優先順位: コマンドライン引数 > config.json > DEFAULTS"""
    cfg = dict(DEFAULTS)
    for k, v in file_config.items():
        if k in cfg:
            cfg[k] = v
    if args.device         is not None: cfg["device"]         = args.device
    if args.width          is not None: cfg["width"]          = args.width
    if args.fps            is not None: cfg["fps"]            = args.fps
    if args.ascii          is not None: cfg["ascii_chars"]    = args.ascii
    if args.color          is not None: cfg["color"]          = args.color
    if args.diff_color     is not None: cfg["diff_color"]     = args.diff_color
    if args.diff_threshold is not None: cfg["diff_threshold"] = args.diff_threshold
    if args.canny_low      is not None: cfg["canny_low"]      = args.canny_low
    if args.canny_high     is not None: cfg["canny_high"]     = args.canny_high
    if args.invert:      cfg["invert"]      = True
    if args.skip_frames: cfg["skip_frames"] = True
    return cfg


# ============================================================
# ターミナルサイズ（短めのキャッシュ）
# ============================================================
_cached_term_size    = None
_term_size_cache_time = 0.0
TERM_SIZE_CACHE_SEC  = 0.2   # 0.2秒ごとに再取得（リサイズを素早く検出）


def get_terminal_size_cached() -> Tuple[int, int]:
    global _cached_term_size, _term_size_cache_time
    now = time.time()
    if _cached_term_size is None or now - _term_size_cache_time > TERM_SIZE_CACHE_SEC:
        _cached_term_size    = shutil.get_terminal_size((80, 24))
        _term_size_cache_time = now
    return (_cached_term_size.columns, _cached_term_size.lines)


# ============================================================
# 画像 → ASCII 文字配列
# ============================================================
def image_to_ascii_array(
    image: np.ndarray,
    width: int,
    invert: bool,
    ascii_chars: str,
) -> np.ndarray:
    """グレースケール画像をASCII文字の2D配列 (dtype '<U1') に変換。"""
    if invert:
        image = cv2.bitwise_not(image)
    h, w = image.shape
    if w == 0:
        return np.array([[" "]], dtype="<U1")
    new_height = max(1, int((h / w) * width * 0.55))
    resized    = cv2.resize(image, (width, new_height), interpolation=cv2.INTER_AREA)
    n          = len(ascii_chars)
    indices    = np.clip(
        np.floor(resized.astype(np.float32) * (n - 1) / 255.0).astype(np.int32),
        0, n - 1,
    )
    return np.array(list(ascii_chars))[indices]


# ============================================================
# フレーム描画（案A: 差分行のみ更新 ＋ 案C: 同期出力モード）
# ============================================================
def build_lines(
    char_array: np.ndarray,
    diff_mask: Optional[np.ndarray],
    base_color: str,
    diff_color: str,
) -> List[str]:
    """
    char_array から ANSI カラー付き行リストを生成する。
    - 差分なし → base_color
    - 差分あり → diff_color
    - 色が変わるときだけ前景色 ANSI コードを挿入
    """
    height, width = char_array.shape
    lines = []

    for row_idx in range(height):
        row_chars  = char_array[row_idx]
        row_diff   = diff_mask[row_idx] if diff_mask is not None else None
        parts      = []
        cur_color  = None

        for col_idx in range(width):
            ch    = row_chars[col_idx]
            color = diff_color if (row_diff is not None and row_diff[col_idx]) else base_color
            if color != cur_color:
                parts.append(color)
                cur_color = color
            parts.append(ch)

        parts.append(ANSI_RESET)
        lines.append("".join(parts))

    return lines


def render_diff(
    prev_lines: Optional[List[str]],
    curr_lines: List[str],
) -> str:
    """
    案A: 前フレームと異なる行だけカーソル移動して上書きする。
    同期出力モード（案C）で囲んで一括反映する。
    prev_lines が None（初回）のときは全行を書き出す。
    """
    out    = []
    n_curr = len(curr_lines)
    n_prev = len(prev_lines) if prev_lines is not None else 0

    # 同期出力モード開始
    out.append(ANSI_SYNC_START)

    if prev_lines is None:
        out.append(ANSI_CURSOR_HOME)
        out.append("\n".join(curr_lines))
    else:
        for i, line in enumerate(curr_lines):
            if i < n_prev and line == prev_lines[i]:
                continue  # 変化なし → スキップ
            out.append("\033[{};1H".format(i + 1))
            out.append(ANSI_ERASE_LINE)
            out.append(line)

        for i in range(n_curr, n_prev):
            out.append("\033[{};1H".format(i + 1))
            out.append(ANSI_ERASE_LINE)

    # 同期出力モード終了
    out.append(ANSI_SYNC_END)

    return "".join(out)


# ============================================================
# メイン
# ============================================================
def main():
    enable_windows_vt()

    parser = argparse.ArgumentParser(
        description="Webカメラ映像をASCIIアートでリアルタイム表示するツール"
    )
    parser.add_argument("--device",         type=int,   default=None)
    parser.add_argument("--width",          type=int,   default=None,
                        help="ASCIIアートの横幅（デフォルト: 100）")
    parser.add_argument("--invert",         action="store_true")
    parser.add_argument("--ascii",          type=str,   default=None)
    parser.add_argument("--fps",            type=float, default=None)
    parser.add_argument("--color",          type=str,   default=None,
                        help="基本表示色 white/green/cyan/yellow/red/blue/magenta または '255,100,0'")
    parser.add_argument("--diff-color",     type=str,   default=None,
                        help="差分ハイライト色（デフォルト: green）")
    parser.add_argument("--diff-threshold", type=int,   default=None,
                        help="差分閾値（デフォルト: 255）")
    parser.add_argument("--canny-low",      type=int,   default=None)
    parser.add_argument("--canny-high",     type=int,   default=None)
    parser.add_argument("--skip-frames",    action="store_true")
    parser.add_argument("--config",         type=str,   default=None,
                        help="設定ファイルパス（デフォルト: ./config.json）")
    args = parser.parse_args()

    # 設定読み込み
    config_path = Path(args.config) if args.config else Path(__file__).parent / "config.json"
    cfg = build_config(load_config(config_path), args)

    # カラー解析
    base_color, _  = parse_color(cfg["color"])
    _, diff_color  = parse_color(cfg["diff_color"])

    # カメラ初期化
    backend = cv2.CAP_DSHOW if os.name == "nt" else 0
    cap     = cv2.VideoCapture(cfg["device"], backend)
    if not cap.isOpened():
        sys.stdout.write("カメラデバイス {} を開けませんでした。\n".format(cfg["device"]))
        sys.stdout.write("  1. カメラが他のアプリで使用中でないか確認 (Zoom/OBS/Teams等)\n")
        sys.stdout.write("  2. デバイス番号を変更して試す (--device 1 など)\n")
        sys.stdout.write("  3. 別のUSBポートに接続 or 再起動\n")
        sys.stdout.write("  4. OpenCVを更新: pip install -U opencv-python\n")
        return

    frame_interval = 1.0 / max(1.0, cfg["fps"])
    prev_edges     = None
    prev_lines     = None   # 前フレームの行リスト（差分描画用）

    # カーソル非表示・画面クリア
    sys.stdout.write(ANSI_CURSOR_HIDE)
    sys.stdout.write("\033[2J")   # 画面全消去（初回のみ）
    sys.stdout.write(ANSI_CURSOR_HOME)
    sys.stdout.flush()

    try:
        last_time = 0.0
        while True:
            now     = time.time()
            elapsed = now - last_time

            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)
                if cfg["skip_frames"]:
                    cap.grab()
                last_time = time.time()
            else:
                last_time = now

            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.1)
                continue

            # 画像処理
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, cfg["canny_low"], cfg["canny_high"])

            # ターミナルサイズ（リサイズを素早く検出するため0.2秒キャッシュ）
            term_cols, term_rows = get_terminal_size_cached()
            width = min(cfg["width"], term_cols, 200)

            # ウィンドウリサイズ検出: サイズが変わったら前フレームをリセット
            if prev_lines is not None and len(prev_lines) > 0:
                # 行幅が変わっていたらリセット
                prev_width = len(prev_lines[0].replace(ANSI_RESET, "")) if prev_lines else 0
                if abs(prev_width - width) > 2:
                    prev_lines = None
                    sys.stdout.write("\033[2J")
                    sys.stdout.write(ANSI_CURSOR_HOME)
                    sys.stdout.flush()

            # ASCII変換
            char_array = image_to_ascii_array(
                edges,
                width=width,
                invert=cfg["invert"],
                ascii_chars=cfg["ascii_chars"],
            )

            # 差分マスク（エッジ画像ベース）
            diff_mask = None
            if prev_edges is not None:
                h, w = char_array.shape
                prev_r  = cv2.resize(prev_edges, (w, h), interpolation=cv2.INTER_AREA)
                curr_r  = cv2.resize(edges,      (w, h), interpolation=cv2.INTER_AREA)
                absdiff = cv2.absdiff(curr_r, prev_r)
                diff_mask = absdiff >= cfg["diff_threshold"]
            prev_edges = edges.copy()

            # 描画（案A: 差分行のみ更新、案C: 同期出力モードで囲む）
            curr_lines = build_lines(char_array, diff_mask, base_color, diff_color)
            output     = render_diff(prev_lines, curr_lines)
            sys.stdout.write(output)
            sys.stdout.flush()
            prev_lines = curr_lines

    except KeyboardInterrupt:
        pass

    finally:
        cap.release()
        sys.stdout.write(ANSI_SYNC_END)
        sys.stdout.write(ANSI_CURSOR_SHOW)
        sys.stdout.write("\n\n終了しました。\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
