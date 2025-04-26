from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit
from prompt_toolkit.widgets import TextArea, RadioList, Button, Label
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
import subprocess
from config_manager import load_config
from visual_helper import generate_jump_diagram

import os
import tkinter as tk
from tkinter import filedialog


# 風格設定
style = Style.from_dict({
    "textarea": "#ffffff",
    "label": "bold fg:ansiwhite bg:ansiblue",
    "output": "fg:ansiyellow bg:black bold",
    "button": "#ffffff",
})


# 控制元件
mode_radio = RadioList(values=[
    ("test", "測試連線"),
    ("upload", "上傳"),
    ("download", "下載")
],
    default="test")


force_radio = RadioList(values=[
    ("yes", "強制覆蓋檔案"),
    ("no", "不覆蓋")
], default="no")

path1 = TextArea(height=1, prompt="本地(上傳)/ 遠端路徑: ", multiline=False)
path2 = TextArea(height=1, prompt="遠端/ 本地(下載)路徑: ", multiline=False)
config_path = TextArea(height=1, prompt="AUTH 檔案: ", text="config.yaml", multiline=False)
output = TextArea(style="class:output", height=8, focusable=True, scrollbar=True, wrap_lines=False)

btn_choose_path1 = Button("選擇檔案", handler=lambda: choose_local_path(path1,'file'))   
btn_choose_path2 = Button("選擇目錄", handler=lambda: choose_local_path(path2,'dir'))
btn_choose_config = Button("選擇檔案", handler=lambda: choose_local_path(config_path,'file'))     

def choose_local_path(path_field,act):
    root = tk.Tk()
    root.withdraw()
    current_dir = os.getcwd()  

    if act == 'file':
        selected = filedialog.askopenfilename(title="選擇檔案", initialdir=current_dir)  
    else:
        selected = filedialog.askdirectory(title="選擇目錄") 

    if selected:
        path_field.text = selected 

    root.destroy()


def do_run():
    diagram = generate_jump_diagram(config_path.text.strip())
    output.text = " （・Ａ・） 預覽 Jump Server 連線邏輯\n\n" + diagram  + "\n\n執行中，請查看新終端機視窗..."
    app.invalidate()

    try:
        validate_inputs()
        cmd = build_command()
        launch_command_in_terminal(cmd)
    except ValueError as e:
        output.text = " （・Ａ・） 預覽 Jump Server 連線邏輯\n\n" + diagram  + f"\n錯誤：{e}"
    except Exception as e:
        output.text = " （・Ａ・） 預覽 Jump Server 連線邏輯\n\n" + diagram  + f"\n啟動失敗：{e}"


def validate_inputs():
    if not mode_radio.current_value:
        raise ValueError("請選擇模式")

    if mode_radio.current_value != "test":
        if not path1.text.strip() or not path2.text.strip():
            raise ValueError("請輸入完整的路徑")


def build_command():
    mode = mode_radio.current_value
    cmd = f'sftp_tool_cli.exe {mode}'

    if mode != "test":
        p1 = path1.text.strip().replace('"', r'\"')
        p2 = path2.text.strip().replace('"', r'\"')
        cmd += f' "{p1}" "{p2}"'

    if force_radio.current_value == "yes":
        cmd += " --force"

    config = config_path.text.strip().replace('"', r'\"')
    cmd += f' --config "{config}"'
    return cmd


def launch_command_in_terminal(cmd):
    # Windows 專用：新開終端機 + 保持顯示
    full_cmd = f'start cmd.exe /K "{cmd} & pause & exit"'
    output.text += f"\n 執行指令：{cmd}"
    subprocess.Popen(full_cmd, shell=True)

def do_clear():
    path1.text = ""
    path2.text = ""
    output.text = ""

def do_exit():
    app.exit()

# 按鈕
btn_run = Button("執行", handler=do_run)
btn_clear = Button("清除", handler=do_clear)
btn_exit = Button("離開", handler=do_exit)
# btn_choose_path = Button("瀏覽檔案", handler=choose_local_path)

# 鍵盤綁定
kb = KeyBindings()


@kb.add("down")
@kb.add("tab")
def _(event):
    event.app.layout.focus_next()
    diagram = generate_jump_diagram(config_path.text.strip())
    output.text =  " （・Ａ・） 預覽 Jump Server 連線邏輯\n\n" + diagram 

@kb.add("up")
@kb.add("s-tab")  
def _(event):
    event.app.layout.focus_previous()



@kb.add("q")
@kb.add('c-q')
@kb.add("escape")
def _(event):
    do_exit()


def center_text(text, width=150):

    padding = max((width - len(text)) // 2, 0)
    return ' ' * padding + text

# Layout
root_container = HSplit([
    Label(text=center_text("Multiple Jump Server -  SFTP TUI 工具 PowerBy HowHow - v2.0"), style="class:label"),
    VSplit([
        mode_radio,
    ], padding=1,
    ),

    VSplit([path1, btn_choose_path1], padding=1),  # 上傳模式：選擇檔案
    VSplit([path2, btn_choose_path2], padding=1),  # 下載模式：選擇目錄
    VSplit([config_path, btn_choose_config], padding=1),  # 新增這行：選擇 AUTH 檔案
    force_radio,
    output,
    VSplit([btn_run, btn_clear, btn_exit], padding=3),
    Label(text=(
        "✨Tips: \n"
        "  ▶ Tab/Shift+Tab 切換區域 | Up/Down 切換模式 ｜ Q/ESC/Ctrl-Q 離開\n"
        "  ▶ 系統會自動判斷是【檔案】還是【目錄】\n"
        "  ▶ 可上傳整包或下載整個目錄\n"
        "  ▶ 如 local/remote 已存在檔案，請選擇【強制覆蓋】\n"
        "  ▶ 使用「選擇檔案/目錄」快速帶入本地路徑，需選擇【上傳】/【下載】模式\n"
    ), style="class:label"),
], padding=1)


layout = Layout(root_container)
app = Application(layout=layout, key_bindings=kb, style=style, full_screen=True)
output.text =  " （・Ａ・） 預覽 Jump Server 連線邏輯\n\n\n等待載入..." 

if __name__ == "__main__":
    app.run()
