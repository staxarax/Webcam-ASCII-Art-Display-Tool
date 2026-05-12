## 利用用途

PowerShellまたはコマンドプロンプト上で Webカメラ映像を ASCIIアートとして表示するツールです。

配信やその他利用は各自の責任で行ってください。

＝＝＝＝＝＝＝＝＝＝＝＝＝＝

## 当該プログラムに関して

# Webカメラ ASCII アート表示ツール

本プログラムは、Webカメラ映像をコマンドライン上で ASCII アートとして表示するツールです。

## 必要環境

- OS: Windows 10 以降  
- Python: 3.5 以降  
- Webカメラ: 一般的なUSBカメラ  
- CPU/GPU: 特別な要求なし  
- 言語環境: 日本語  

＝＝＝＝＝＝＝＝＝＝＝＝＝＝
## 導入について

1. Python をインストールしてください。
2. 必要ライブラリをインストールしてください。
opencv
numpy
を導入して下さい。
pipを用いる場合
pip install opencv-python
pip install numpy
で導入できます。

＝＝＝＝＝＝＝＝＝＝＝＝＝＝
## 利用方法について

コマンドプロンプトまたは PowerShell を開きます。

プログラム (main.py) があるディレクトリで以下を実行します。
> python main.py 

プログラムを終了するには Ctrl + C または Pause/Break キーを押してください。

＝＝＝＝＝＝＝＝＝＝＝＝＝＝
## 注意点について

引数を指定しない場合、カメラデバイスを自動で参照できません。
使用するデバイスは 0 から順に試してください。制作者環境では5まで上げました。

＝＝＝＝＝＝＝＝＝＝＝＝＝＝
引数一覧
＝＝＝＝＝＝＝＝＝＝＝＝＝＝

--device			使用するカメラインデックス
--width			ASCIIアートの横幅。
--invert			白黒反転モードを有効にする。
--ascii			使用するASCII文字列。
--fps			出力フレームレートの上限（デフォルト 30.0）")
--color			通常の表示色
--diff-color		差分の表示色
--diff-threshold	閾値の値
--canny-low   		Cannyエッジ検出の閾値を変更
--canny-high		Cannyエッジ検出の閾値を変更
--skip-frames		処理が重いときに古いフレームを捨てて最新を表示


＝＝＝＝＝＝＝＝＝＝＝＝＝＝

利用方法

powershell　コマンドプロンプトを利用してwebカメラからの映像をCLIで表示させる物です。
それ以上でも以下もありません。

配信をするにあたって署名性を求めながら配信を可能にするなど。
利用方法は各自で探して下さい。

＝＝＝＝＝＝＝＝＝＝＝＝＝＝
実行例   実行例コマンド例　

# デフォルト例
python main.py --device 5 --fps 60 --width 300

# 白黒反転＋カスタムASCII文字列
python main.py --device 5 --fps 60 --width 300 --invert --ascii "@MW#8B%$&WM8ZO0QLCJUYXcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\^`'. "

フルパス実行例:
C:\Users\username\PycharmProjects\webcam_AA>python main.py --device 4 --fps 60 --color  white --width 300 --invert --skip-frames  --ascii "@MW#8B%$&WM8ZO0QLCJUYXcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\^`'. "

＝＝＝＝＝＝＝＝＝＝＝＝＝＝
免責
＝＝＝＝＝＝＝＝＝＝＝＝＝＝
本プログラムは「現状のまま」で提供されます。

プログラム使用によるいかなる損害（データ損失、機器損傷、その他）について、作者は一切責任を負いません

利用者自身の責任で使用してください。

商用利用や配信での使用についても、使用者自身の責任で行ってください。


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
