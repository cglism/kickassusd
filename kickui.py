import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import configparser

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.ini")

root = tk.Tk()
root.title("Kick Arnold USD Renderer - Pro")
root.geometry("600x640")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

# ------------------ Theme Colors ------------------
bg_color = "#1e1e1e"
fg_color = "#dddddd"
entry_bg = "#2e2e2e"
entry_fg = "#ffffff"
button_bg = "#3c3f41"
button_fg = "#ffffff"

# ------------------ Variables ------------------
kick_path_var = tk.StringVar()
usd_file_var = tk.StringVar()
output_dir_var = tk.StringVar()
output_name_var = tk.StringVar(value="render")
start_frame_var = tk.StringVar(value="1")
end_frame_var = tk.StringVar(value="10")
filetype_var = tk.StringVar(value="png")
device_var = tk.StringVar(value="CPU")
res_width_var = tk.StringVar(value="1920")
res_height_var = tk.StringVar(value="1080")
aa_preset_var = tk.StringVar(value="Medium (4)")
custom_aa_var = tk.StringVar(value="5")
camera_var = tk.StringVar()
render_mode_var = tk.StringVar(value="Single Frame")

# ------------------ Config Functions ------------------
def save_config():
    config = configparser.ConfigParser()
    config['Settings'] = {k: v.get() for k, v in {
        'kick_path': kick_path_var,
        'usd_file': usd_file_var,
        'output_dir': output_dir_var,
        'output_name': output_name_var,
        'start_frame': start_frame_var,
        'end_frame': end_frame_var,
        'filetype': filetype_var,
        'device': device_var,
        'res_width': res_width_var,
        'res_height': res_height_var,
        'aa_preset': aa_preset_var,
        'custom_aa': custom_aa_var,
        'camera': camera_var,
        'render_mode': render_mode_var
    }.items()}

    with open(CONFIG_FILE, 'w') as f:
        config.write(f)
    messagebox.showinfo("Config Saved", f"Settings saved to config.ini")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'Settings' in config:
        for key in config['Settings']:
            var = globals().get(f"{key}_var")
            if isinstance(var, tk.StringVar):
                var.set(config['Settings'][key])

# ------------------ Utility Functions ------------------
def browse_kick():
    path = filedialog.askopenfilename(filetypes=[("kick.exe", "kick.exe")])
    if path:
        kick_path_var.set(path)

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("USD files", "*.usd;*.usda;*.usdc")])
    if file_path:
        usd_file_var.set(file_path)

def browse_output_dir():
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_dir_var.set(dir_path)

def get_aa_samples(preset):
    return {
        "Low (2)": 2,
        "Medium (4)": 4,
        "High (6)": 6,
        "Ultra (8)": 8,
        "Custom": custom_aa_var.get()
    }.get(preset, 4)

# ------------------ Render Functions ------------------
def render_single_frame():
    try:
        start = int(start_frame_var.get())
        width = int(res_width_var.get())
        height = int(res_height_var.get())
        aa_samples = int(get_aa_samples(aa_preset_var.get()))
    except ValueError:
        messagebox.showerror("Error", "Frame/resolution/AA must be valid numbers.")
        return

    cmd = (
        f'"{kick_path_var.get()}" -frame {start} '
        f'-r {width} {height} '
        f'-set options.AA_samples {aa_samples} '
        f'-set options.bucket_size 16 '
        f'-set options.render_device "{device_var.get()}" '
        f'-set options.imager 1 '
        f'-o "{os.path.join(output_dir_var.get(), f"{output_name_var.get()}_{str(start).zfill(4)}.{filetype_var.get()}")}" '
        f'"{usd_file_var.get()}"'
    )
    subprocess.Popen(cmd, shell=True)
    messagebox.showinfo("Render Started", f"Rendering single frame {start}...")

def render_sequence():
    try:
        start = int(start_frame_var.get())
        end = int(end_frame_var.get())
        width = int(res_width_var.get())
        height = int(res_height_var.get())
        aa_samples = int(get_aa_samples(aa_preset_var.get()))
    except ValueError:
        messagebox.showerror("Error", "Frame/resolution/AA must be valid numbers.")
        return

    if start > end:
        messagebox.showerror("Error", "Start frame must be <= end frame.")
        return

    script_lines = ["@echo off\n"]
    for frame in range(start, end + 1):
        padded = str(frame).zfill(4)
        output_path = os.path.join(output_dir_var.get(), f"{output_name_var.get()}_{padded}.{filetype_var.get()}")
        cmd = (
            f'"{kick_path_var.get()}" -frame {frame} '
            f'-r {width} {height} '
            f'-set options.AA_samples {aa_samples} '
            f'-set options.bucket_size 16 '
            f'-set options.render_device "{device_var.get()}" '
            f'-dw -o "{output_path}" "{usd_file_var.get()}"\n'
        )
        script_lines.append(cmd)

    bat_path = os.path.join(output_dir_var.get(), "render_sequence.bat")
    with open(bat_path, "w") as f:
        f.writelines(script_lines)

    os.startfile(bat_path)
    messagebox.showinfo("Render Started", f"Rendering {start} to {end}\nScript saved at:\n{bat_path}")

# ------------------ UI Update ------------------
def update_render_mode(*args):
    mode = render_mode_var.get()
    if mode == "Single Frame":
        end_frame_entry.config(state="disabled")
    else:
        end_frame_entry.config(state="normal")

# ------------------ UI Layout ------------------
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Save Config", command=save_config)
file_menu.add_command(label="Load Config", command=load_config)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# Render Mode
tk.Label(root, text="Render Mode:", fg=fg_color, bg=bg_color).pack(pady=5)
tk.OptionMenu(root, render_mode_var, "Single Frame", "Render Sequence").pack()
render_mode_var.trace("w", update_render_mode)

# Kick Path
tk.Label(root, text="Path to kick.exe:", fg=fg_color, bg=bg_color).pack(pady=5)
frame_kick = tk.Frame(root, bg=bg_color)
frame_kick.pack()
tk.Entry(frame_kick, textvariable=kick_path_var, width=50, bg=entry_bg, fg=entry_fg).pack(side=tk.LEFT, padx=5)
tk.Button(frame_kick, text="Browse", command=browse_kick, bg=button_bg, fg=button_fg).pack(side=tk.LEFT)

# USD File
tk.Label(root, text="USD File:", fg=fg_color, bg=bg_color).pack(pady=5)
tk.Entry(root, textvariable=usd_file_var, width=60, bg=entry_bg, fg=entry_fg).pack()
tk.Button(root, text="Browse USD File", command=browse_file, bg=button_bg, fg=button_fg).pack(pady=2)

# Output Folder
tk.Label(root, text="Output Folder:", fg=fg_color, bg=bg_color).pack(pady=5)
tk.Entry(root, textvariable=output_dir_var, width=60, bg=entry_bg, fg=entry_fg).pack()
tk.Button(root, text="Browse Output Folder", command=browse_output_dir, bg=button_bg, fg=button_fg).pack(pady=2)

# Base Name, Extension, Device
frame1 = tk.Frame(root, bg=bg_color)
frame1.pack(pady=5)
tk.Label(frame1, text="Base Name:", fg=fg_color, bg=bg_color).grid(row=0, column=0, padx=5)
tk.Entry(frame1, textvariable=output_name_var, width=16, bg=entry_bg, fg=entry_fg).grid(row=0, column=1)
tk.Label(frame1, text="Ext:", fg=fg_color, bg=bg_color).grid(row=0, column=2, padx=5)
tk.OptionMenu(frame1, filetype_var, "png", "exr", "jpg", "tif").grid(row=0, column=3)
tk.Label(frame1, text="Device:", fg=fg_color, bg=bg_color).grid(row=0, column=4, padx=5)
tk.OptionMenu(frame1, device_var, "CPU", "GPU").grid(row=0, column=5)

# Frame Range
frame2 = tk.Frame(root, bg=bg_color)
frame2.pack(pady=5)
tk.Label(frame2, text="Start Frame:", fg=fg_color, bg=bg_color).grid(row=0, column=0, padx=5)
tk.Entry(frame2, textvariable=start_frame_var, width=8, bg=entry_bg, fg=entry_fg).grid(row=0, column=1)
tk.Label(frame2, text="End Frame:", fg=fg_color, bg=bg_color).grid(row=0, column=2, padx=5)
end_frame_entry = tk.Entry(frame2, textvariable=end_frame_var, width=8, bg=entry_bg, fg=entry_fg)
end_frame_entry.grid(row=0, column=3)

# Resolution
frame3 = tk.Frame(root, bg=bg_color)
frame3.pack(pady=5)
tk.Label(frame3, text="Resolution:", fg=fg_color, bg=bg_color).grid(row=0, column=0, padx=5)
tk.Entry(frame3, textvariable=res_width_var, width=6, bg=entry_bg, fg=entry_fg).grid(row=0, column=1)
tk.Label(frame3, text="x", fg=fg_color, bg=bg_color).grid(row=0, column=2)
tk.Entry(frame3, textvariable=res_height_var, width=6, bg=entry_bg, fg=entry_fg).grid(row=0, column=3)

# AA and Custom
frame4 = tk.Frame(root, bg=bg_color)
frame4.pack(pady=5)
tk.Label(frame4, text="AA Samples:", fg=fg_color, bg=bg_color).grid(row=0, column=0, padx=5)
tk.OptionMenu(frame4, aa_preset_var, "Low (2)", "Medium (4)", "High (6)", "Ultra (8)", "Custom").grid(row=0, column=1)
tk.Label(frame4, text="Custom AA:", fg=fg_color, bg=bg_color).grid(row=0, column=2, padx=5)
tk.Entry(frame4, textvariable=custom_aa_var, width=5, bg=entry_bg, fg=entry_fg).grid(row=0, column=3)

# Camera
tk.Label(root, text="Camera Override (optional):", fg=fg_color, bg=bg_color).pack(pady=5)
tk.Entry(root, textvariable=camera_var, width=40, bg=entry_bg, fg=entry_fg).pack()

# Render Button
render_button = tk.Button(root, text="Render", height=2, bg="#007ACC", fg="white", font=("Arial", 14, "bold"))
render_button.pack(fill=tk.X, pady=20, padx=40)

def render_dispatch():
    if render_mode_var.get() == "Single Frame":
        render_single_frame()
    else:
        render_sequence()

render_button.config(command=render_dispatch)

# ------------------ Init ------------------
load_config()
update_render_mode()
root.mainloop()
