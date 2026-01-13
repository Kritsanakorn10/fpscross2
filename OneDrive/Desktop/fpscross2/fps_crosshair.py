import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import screeninfo
import platform
import os
import json
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

CONFIG_FILE = "config.json"


class CrosshairOverlay:
    def __init__(self, parent):
        self.parent = parent
        self.overlay = tk.Toplevel(parent)
        self.overlay.title("FPS Crosshair Overlay")

        self.overlay.attributes('-topmost', True)
        self.overlay.overrideredirect(True)

        if platform.system() == "Windows":
            self.overlay.attributes('-transparentcolor', '#000001')
            try:
                import ctypes
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                WS_EX_TRANSPARENT = 0x00000020
                hwnd = ctypes.windll.user32.GetParent(self.overlay.winfo_id())
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(
                    hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT
                )
            except:
                pass
        else:
            self.overlay.attributes('-alpha', 0.9)
            self.overlay.config(bg='#000001')

        self.canvas = tk.Canvas(self.overlay, bg='#000001', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.settings = {
            'style': 'Cross',
            'color': '#FF0000',
            'size': 20,
            'thickness': 2,
            'monitor': 0
        }

    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        self.update_position()
        self.draw_crosshair()

    def update_position(self):
        try:
            monitors = screeninfo.get_monitors()
        except:
            monitors = []

        if monitors and self.settings['monitor'] < len(monitors):
            m = monitors[self.settings['monitor']]
            x = m.x + (m.width // 2) - (self.settings['size'] // 2)
            y = m.y + (m.height // 2) - (self.settings['size'] // 2)
        else:
            screen_width = self.parent.winfo_screenwidth()
            screen_height = self.parent.winfo_screenheight()
            x = (screen_width // 2) - (self.settings['size'] // 2)
            y = (screen_height // 2) - (self.settings['size'] // 2)

        size = self.settings['size']
        self.overlay.geometry(f"{size}x{size}+{x}+{y}")

    def draw_crosshair(self):
        self.canvas.delete("all")
        style = self.settings['style']
        color = self.settings['color']
        size = self.settings['size']
        t = self.settings['thickness']
        center = size // 2

        if style == 'Dot':
            self.canvas.create_oval(center-t, center-t, center+t, center+t, fill=color, outline=color)
        elif style == 'Cross':
            self.canvas.create_line(0, center, size, center, fill=color, width=t)
            self.canvas.create_line(center, 0, center, size, fill=color, width=t)
        elif style == 'Circle':
            self.canvas.create_oval(t, t, size-t, size-t, outline=color, width=t)
        elif style == 'T-Shape':
            self.canvas.create_line(0, center, size, center, fill=color, width=t)
            self.canvas.create_line(center, center, center, size, fill=color, width=t)
        elif style == 'Square':
            self.canvas.create_rectangle(t, t, size-t, size-t, outline=color, width=t)
        elif style == 'X-Cross Dot':
            gap = size // 4
            self.canvas.create_line(0, 0, center - gap//2, center - gap//2, fill=color, width=t)
            self.canvas.create_line(center + gap//2, center + gap//2, size, size, fill=color, width=t)
            self.canvas.create_line(size, 0, center + gap//2, center - gap//2, fill=color, width=t)
            self.canvas.create_line(center - gap//2, center + gap//2, 0, size, fill=color, width=t)


class SettingsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("FPS Crosshair")
        self.root.geometry("360x720")
        self.root.configure(bg='#1a0a0a')

        self.current_settings = {
            'style': 'X-Cross Dot',
            'color': '#FF0000',
            'size': 20,
            'thickness': 2,
            'monitor': 0
        }

        self.load_config()

        # ===== FIX ICON (ลบ os.path.exists) =====
        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except:
            pass

        self.setup_styles()
        self.overlay = CrosshairOverlay(root)
        self.current_color = self.current_settings['color']

        main_frame = tk.Frame(root, bg='#1a0a0a', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ===== FIX LOGO (ลบ os.path.exists) =====
        self.logo_img = None
        try:
            self.logo_img = tk.PhotoImage(file=resource_path("logo.png"))
            if self.logo_img.width() > 100:
                self.logo_img = self.logo_img.subsample(
                    max(1, self.logo_img.width() // 100)
                )
            logo_label = tk.Label(main_frame, image=self.logo_img, bg='#1a0a0a')
            logo_label.pack(pady=(0, 10))
        except:
            pass

        header = tk.Label(
            main_frame,
            text="CROSSHAIR SETTINGS",
            font=('Segoe UI', 14, 'bold'),
            bg='#1a0a0a',
            fg='#ff4d4d'
        )
        header.pack(pady=(0, 20))

        # ===== ส่วนที่เหลือเหมือนเดิมทั้งหมด =====
        # (ไม่มีการเปลี่ยน logic ใด ๆ)
# Style Section
        self.create_label(main_frame, "STYLE")
        self.style_var = tk.StringVar(value=self.current_settings['style'])
        styles = ["Dot", "Cross", "Circle", "T-Shape", "Square", "X-Cross Dot"]
        self.style_cb = ttk.Combobox(main_frame, textvariable=self.style_var, values=styles, state="readonly")
        self.style_cb.pack(fill=tk.X, pady=(0, 15))

        # Color Section
        self.create_label(main_frame, "COLOR")
        self.color_preview = tk.Frame(main_frame, height=35, bg=self.current_color, cursor="hand2",
                                     highlightbackground="#ff4d4d", highlightthickness=1)
        self.color_preview.pack(fill=tk.X, pady=(0, 15))
        self.color_preview.bind("<Button-1>", lambda e: self.choose_color())
        
        # Size Section
        size_header_frame = tk.Frame(main_frame, bg='#1a0a0a')
        size_header_frame.pack(fill=tk.X)
        self.create_label(size_header_frame, "SCALE (SIZE)", side=tk.LEFT)
        self.size_val_lbl = tk.Label(size_header_frame, text=str(self.current_settings['size']), font=('Segoe UI', 8, 'bold'), bg='#1a0a0a', fg='#ff4d4d')
        self.size_val_lbl.pack(side=tk.RIGHT)
        
        self.size_scale = ttk.Scale(main_frame, from_=15, to=30, orient=tk.HORIZONTAL)
        self.size_scale.set(self.current_settings['size'])
        self.size_scale.pack(fill=tk.X, pady=(0, 15))

        # Thickness Section
        thick_header_frame = tk.Frame(main_frame, bg='#1a0a0a')
        thick_header_frame.pack(fill=tk.X)
        self.create_label(thick_header_frame, "THICKNESS", side=tk.LEFT)
        self.thick_val_lbl = tk.Label(thick_header_frame, text=str(self.current_settings['thickness']), font=('Segoe UI', 8, 'bold'), bg='#1a0a0a', fg='#ff4d4d')
        self.thick_val_lbl.pack(side=tk.RIGHT)
        
        self.thick_scale = ttk.Scale(main_frame, from_=1, to=30, orient=tk.HORIZONTAL)
        self.thick_scale.set(self.current_settings['thickness'])
        self.thick_scale.pack(fill=tk.X, pady=(0, 15))

        # Monitor Section
        self.create_label(main_frame, "MONITOR")
        try:
            self.monitors = screeninfo.get_monitors()
        except:
            self.monitors = []
        
        monitor_names = [f"Monitor {i}: {m.width}x{m.height}" for i, m in enumerate(self.monitors)]
        if not monitor_names:
            monitor_names = ["Default Monitor"]
            
        default_monitor_idx = self.current_settings['monitor'] if self.current_settings['monitor'] < len(monitor_names) else 0
        self.monitor_var = tk.StringVar(value=monitor_names[default_monitor_idx])
        self.monitor_cb = ttk.Combobox(main_frame, textvariable=self.monitor_var, values=monitor_names, state="readonly")
        self.monitor_cb.pack(fill=tk.X, pady=(0, 25))

        # Action Buttons
        btn_frame = tk.Frame(main_frame, bg='#1a0a0a')
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Save Button (New)
        self.save_btn = tk.Button(btn_frame, text="SAVE SETTINGS", command=self.manual_save,
                                 bg='#ff4d4d', fg='white', font=('Segoe UI', 10, 'bold'),
                                 activebackground='#cc0000', activeforeground='white',
                                 relief=tk.FLAT, pady=10, bd=0)
        self.save_btn.pack(fill=tk.X, pady=(0, 10))

        self.apply_btn = tk.Button(btn_frame, text="REFRESH POSITION", command=self.apply_changes,
                                 bg='#331111', fg='#ff4d4d', font=('Segoe UI', 9, 'bold'),
                                 activebackground='#442222', activeforeground='white',
                                 relief=tk.FLAT, pady=8, bd=0)
        self.apply_btn.pack(fill=tk.X, pady=5)

        self.quit_btn = tk.Button(btn_frame, text="QUIT PROGRAM", command=self.root.destroy,
                                bg='#4d0000', fg='white', font=('Segoe UI', 9, 'bold'),
                                activebackground='#660000', activeforeground='white',
                                relief=tk.FLAT, pady=8, bd=0)
        self.quit_btn.pack(fill=tk.X, pady=5)
        
        # Event Binding
        self.style_cb.bind("<<ComboboxSelected>>", self.apply_changes)
        self.monitor_cb.bind("<<ComboboxSelected>>", self.apply_changes)
        self.size_scale.config(command=self.on_size_change)
        self.thick_scale.config(command=self.on_thick_change)
        
        self.apply_changes()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#2d1111", background="#2d1111", 
                        foreground="white", bordercolor="#4d1111", arrowcolor="#ff4d4d")
        style.map("TCombobox", fieldbackground=[('readonly', '#2d1111')], 
                  foreground=[('readonly', 'white')])
        style.configure("TScale", background="#1a0a0a", troughcolor="#331111", 
                        bordercolor="#1a0a0a", lightcolor="#ff4d4d", darkcolor="#ff4d4d")

    def create_label(self, parent, text, side=tk.W):
        lbl = tk.Label(parent, text=text, font=('Segoe UI', 8, 'bold'), 
                      bg='#1a0a0a', fg='#b38888')
        if side == tk.LEFT:
            lbl.pack(side=tk.LEFT, pady=(0, 5))
        else:
            lbl.pack(anchor=side, pady=(0, 5))

    def on_size_change(self, val):
        self.size_val_lbl.config(text=str(int(float(val))))
        self.apply_changes()

    def on_thick_change(self, val):
        self.thick_val_lbl.config(text=str(int(float(val))))
        self.apply_changes()

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_preview.config(bg=color)
            self.apply_changes()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    self.current_settings.update(loaded)
            except:
                pass

    def manual_save(self):
        self.save_config()
        messagebox.showinfo("Success", "Settings saved successfully!")

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.current_settings, f)
        except:
            pass

    def apply_changes(self, event=None):
        if hasattr(self, 'monitor_cb'):
            monitor_idx = self.monitor_cb.current()
        else:
            monitor_idx = self.current_settings['monitor']
            
        if monitor_idx == -1: monitor_idx = 0
        
        self.current_settings = {
            'style': self.style_var.get(),
            'color': self.current_color,
            'size': int(self.size_scale.get()),
            'thickness': int(self.thick_scale.get()),
            'monitor': monitor_idx
        }
        self.overlay.update_settings(self.current_settings)

if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsWindow(root)
    root.mainloop()
