import win32gui
import win32con
import win32api  # 追加
from PIL import Image, ImageTk, ImageSequence, ImageFilter
import tkinter as tk

# ウィンドウハンドルを取得
def get_taskbar_handle():
    return win32gui.FindWindow("Shell_TrayWnd", None)

# タスクバーの位置とサイズを取得
def get_taskbar_rect():
    hwnd = get_taskbar_handle()
    rect = win32gui.GetWindowRect(hwnd)
    return rect

# モニターの解像度を取得
def get_screen_width():
    return win32api.GetSystemMetrics(0)

# GIFを読み込む
def load_gif_frames(file_path, scale_factor=1/6):  # scale_factorを1/6に設定
    gif = Image.open(file_path)
    frames = []
    for frame in ImageSequence.Iterator(gif):
        # RGBAモードでのリサイズ
        resized_frame = frame.convert('RGBA').resize(
            (int(frame.width * scale_factor), int(frame.height * scale_factor)),
            Image.Resampling.LANCZOS  # 高品質リサンプリング
        )
        # アウトラインのギザギザを滑らかにするためにスムージングを加える
        resized_frame = resized_frame.filter(ImageFilter.SMOOTH_MORE)  # より高品質なスムージング
        
        frames.append(resized_frame)
    return frames

# タスクバーの上にウィンドウを作成し、GIFを表示
class TaskbarGifApp:
    def __init__(self, gif_path):
        self.frames = load_gif_frames(gif_path)
        self.original_frames = self.frames.copy()  # 元のフレームを保存
        self.current_frame = 0
        self.moving_right = False  # 初期状態で左に動く

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "black")

        self.label = tk.Label(self.root, bg="black")
        self.label.pack()

        self.update_gif()
        self.position_window()
        self.move_gif()

        self.root.mainloop()

    def update_gif(self):
        frame = ImageTk.PhotoImage(self.frames[self.current_frame])
        self.label.config(image=frame)
        self.label.image = frame

        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.root.after(50, self.update_gif)  # 次のフレームを50ミリ秒後に表示

    def position_window(self):
        rect = get_taskbar_rect()
        self.taskbar_y = rect[1] - self.frames[0].height  # タスクバーの上に配置するためにY座標を調整
        self.taskbar_width = rect[2] - rect[0]

        self.screen_width = get_screen_width()  # モニターの幅を取得

        # スタート位置を右端に設定し、サブモニターの右側に映らないようにする
        self.x = self.screen_width - self.frames[0].width  # 右端からスタート
        self.root.geometry(f"+{self.x}+{self.taskbar_y}")

    def move_gif(self):
        if self.moving_right:
            self.x += 2  # 2ピクセル右に移動 (速度を少し遅くした)
            if self.x + self.frames[0].width > self.screen_width:  # 右端に達したら反転
                self.moving_right = False
                # GIFの向きを反転し、現在のフレーム位置をリセット
                self.frames = [frame.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for frame in self.frames]  # 左右反転
        else:
            self.x -= 2  # 2ピクセル左に移動 (速度を少し遅くした)
            if self.x < 0:  # 左端に達したら反転
                self.moving_right = True
                # GIFの向きを元に戻し、現在のフレーム位置をリセット
                self.frames = [frame.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for frame in self.frames]  # 左右反転

        self.root.geometry(f"+{self.x}+{self.taskbar_y}")
        self.root.after(30, self.move_gif)  # 30ミリ秒後に再度移動 (移動速度の遅さを調整)

if __name__ == "__main__":
    TaskbarGifApp(r"ここにあなたのGIFファイルパス")
