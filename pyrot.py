import asyncio
import datetime
import logging
import os
from pathlib import Path
from dataclasses import dataclass
import random
import time
import tkinter as tk
from ctypes import windll

import customtkinter
import keyboard
from PIL import ImageGrab, Image
import numpy.typing as npt
import numpy as np
from skimage.metrics import structural_similarity, normalized_root_mse, mean_squared_error

from config.Configuration import get_config, Configuration, write_config
from icons import get_klass_spell_icons, load_spell_icons_by_spec
from specs import SpecKeybind, get_klasses_and_specs, get_spec

windll.shcore.SetProcessDpiAwareness(1)
customtkinter.set_default_color_theme("dark-blue")
cfg_path = Path("config.yaml")

cfg = get_config(cfg_path)

klass_list = get_klasses_and_specs(cfg.specs_path)
spec_with_icons = None
if cfg.klass:
    if cfg.klass not in os.listdir(cfg.icons_path):
        # progressbar.grid(row=2, padx=10, sticky="ew")
        # progressbar.start()
        asyncio.run(get_klass_spell_icons(cfg.klass, cfg.icons_path))
        # progressbar.grid_forget()

if cfg.klass and cfg.spec:
    current_spec = klass_list[cfg.klass][cfg.spec]
    try:
        spec_with_icons = load_spell_icons_by_spec(cfg.icons_path, cfg.klass, current_spec)
    except ValueError as e:
        for sk in current_spec:
            asyncio.run(get_klass_spell_icons(cfg.klass, cfg.icons_path, sk.spell))
            if sk.icon_name:
                asyncio.run(get_klass_spell_icons(cfg.klass, cfg.icons_path, sk.icon_name))
        spec_with_icons = load_spell_icons_by_spec(cfg.icons_path, cfg.klass, current_spec)

play = False


def toggle():
    global play
    play = not play


keyboard.add_hotkey(cfg.toggle_keybind, toggle)

app = customtkinter.CTk()

app.title("pyrot")
app.geometry("500x400")
app.grid_columnconfigure((0), weight=1)

canvas_toplevel = customtkinter.CTkToplevel()
canvas_toplevel.withdraw()
canvas_toplevel.bind("<Any-FocusIn>", lambda x: app.lift())
snip_canvas = tk.Canvas(canvas_toplevel, cursor="cross", bg="grey11")
snip_canvas.pack(fill=tk.BOTH, expand=tk.YES)

canvas_toplevel.attributes("-fullscreen", True)
canvas_toplevel.attributes("-alpha", 0.4)
canvas_toplevel.attributes("-transparent", "maroon3")

snip_canvas.create_rectangle(
    cfg.looker_x,
    cfg.looker_y,
    cfg.looker_x + cfg.looker_size,
    cfg.looker_y + cfg.looker_size,
    outline="red",
    width=3,
    fill="maroon3",
)


def activate_looker():
    canvas_toplevel.deiconify()


def tab_selected():
    if tabview.get() == "Looker":
        canvas_toplevel.deiconify()
        app.lift()
    else:
        canvas_toplevel.withdraw()


tabview = customtkinter.CTkTabview(app, command=tab_selected)
tabview.grid(sticky="nsew")

tab_general = tabview.add("General")
tab_looker = tabview.add("Looker")


# tabview.set("General")
selected_size = tk.StringVar(value=f"{cfg.looker_size} px")
selected_x = tk.StringVar(value=f"{cfg.looker_x} px")
selected_y = tk.StringVar(value=f"{cfg.looker_y} px")


def set_slider_size(size: float):
    size = int(size)
    cfg.looker_size = size
    snip_canvas.coords(1, cfg.looker_x, cfg.looker_y, cfg.looker_x + cfg.looker_size, cfg.looker_y + cfg.looker_size)
    selected_size.set(f"{size} px")
    slider_size.set(size)


def set_slider_x(x: float):
    x = int(x)
    cfg.looker_x = x
    snip_canvas.coords(1, cfg.looker_x, cfg.looker_y, cfg.looker_x + cfg.looker_size, cfg.looker_y + cfg.looker_size)
    selected_x.set(f"{x} px")
    slider_x.set(x)


def set_slider_y(y: float):
    y = int(y)
    cfg.looker_y = y
    snip_canvas.coords(1, cfg.looker_x, cfg.looker_y, cfg.looker_x + cfg.looker_size, cfg.looker_y + cfg.looker_size)
    selected_y.set(f"{y} px")
    slider_y.set(y)


size_label = customtkinter.CTkLabel(tab_looker, text="Looker size")
size_label.grid(row=0, column=0)
slider_size = customtkinter.CTkSlider(tab_looker, from_=30, to=100, number_of_steps=90, command=set_slider_size)
slider_size.grid(row=0, column=1)
slider_size.set(cfg.looker_size)
selected_size_label = customtkinter.CTkLabel(tab_looker, textvariable=selected_size)
selected_size_label.grid(row=0, column=2)
size_plus_button = customtkinter.CTkButton(
    tab_looker, text="+", width=20, command=lambda: set_slider_size(cfg.looker_size + 1)
)
size_plus_button.grid(row=0, column=3)
size_minus_button = customtkinter.CTkButton(
    tab_looker, text="-", width=20, command=lambda: set_slider_size(cfg.looker_size - 1)
)
size_minus_button.grid(row=0, column=4)


slider_x_label = customtkinter.CTkLabel(tab_looker, text="Looker x position")
slider_x_label.grid(row=1, column=0)
slider_x = customtkinter.CTkSlider(
    tab_looker, from_=0, to=app.winfo_screenwidth(), number_of_steps=app.winfo_screenwidth(), command=set_slider_x
)
slider_x.grid(row=1, column=1)
slider_x.set(cfg.looker_x)
selected_x_label = customtkinter.CTkLabel(tab_looker, textvariable=selected_x)
selected_x_label.grid(row=1, column=2)
x_minus_button = customtkinter.CTkButton(tab_looker, text="-", width=20, command=lambda: set_slider_x(cfg.looker_x - 1))
x_minus_button.grid(row=1, column=3)
x_plus_button = customtkinter.CTkButton(tab_looker, text="+", width=20, command=lambda: set_slider_x(cfg.looker_x + 1))
x_plus_button.grid(row=1, column=4)

slider_y_label = customtkinter.CTkLabel(tab_looker, text="Looker y position")
slider_y_label.grid(row=2, column=0)
slider_y = customtkinter.CTkSlider(
    tab_looker, from_=0, to=app.winfo_screenheight(), number_of_steps=app.winfo_screenheight(), command=set_slider_y
)
slider_y.grid(row=2, column=1)
slider_y.set(cfg.looker_x)
selected_y_label = customtkinter.CTkLabel(tab_looker, textvariable=selected_y)
selected_y_label.grid(row=2, column=2)
y_minus_button = customtkinter.CTkButton(tab_looker, text="-", width=20, command=lambda: set_slider_y(cfg.looker_y - 1))
y_minus_button.grid(row=2, column=3)
y_plus_button = customtkinter.CTkButton(tab_looker, text="+", width=20, command=lambda: set_slider_y(cfg.looker_y + 1))
y_plus_button.grid(row=2, column=4)


def save_looker():
    write_config(cfg, cfg_path)


looker_save_button = customtkinter.CTkButton(tab_looker, text="Save to config", command=save_looker)
looker_save_button.grid(row=3, sticky="ew")
looker_image_label = customtkinter.CTkLabel(tab_looker, text="")
looker_image_label.grid(row=3, column=1)


def klass_menu_cb(choice: str):
    global current_spec
    cfg.klass = choice
    write_config(cfg, cfg_path)

    if cfg.klass not in os.listdir(cfg.icons_path):
        # progressbar.grid(row=2, padx=10, sticky="ew")
        # progressbar.start()
        asyncio.run(get_klass_spell_icons(cfg.klass, cfg.icons_path))
        # progressbar.grid_forget()
        if current_spec:
            for sk in current_spec:
                asyncio.run(get_klass_spell_icons(cfg.klass, cfg.icons_path, sk.spell))
                if sk.icon_name:
                    asyncio.run(get_klass_spell_icons(cfg.klass, cfg.icons_path, sk.icon_name))

    spec_menu.configure(values=list(klass_list[cfg.klass].keys()), require_redraw=True)
    spec_menu.set(cfg.spec)


def spec_menu_cb(spec: str):
    global spec_with_icons
    cfg.spec = spec
    write_config(cfg, cfg_path)

    current_spec = klass_list[cfg.klass][cfg.spec]
    spec_with_icons = load_spell_icons_by_spec(cfg.icons_path, cfg.klass, current_spec)


klass_menu = customtkinter.CTkOptionMenu(tab_general, values=list(klass_list.keys()), command=klass_menu_cb)
klass_menu.grid(row=0, column=0, padx=10)
klass_menu.set(cfg.klass)

spec_menu = customtkinter.CTkOptionMenu(
    tab_general, values=list(klass_list[cfg.klass].keys()) if cfg.klass else [], command=spec_menu_cb
)
spec_menu.set(cfg.spec)
spec_menu.grid(row=0, column=1, padx=10)


def download_icons():
    global current_spec
    if current_spec:
        for sk in current_spec:
            asyncio.run(get_klass_spell_icons(cfg.klass, cfg.icons_path, sk.spell))
            if sk.icon_name:
                asyncio.run(get_klass_spell_icons(cfg.klass, cfg.icons_path, sk.icon_name))


# download_icon_button = customtkinter.CTkButton(tab_general, text="Download Icons", command=download_icons)
# download_icon_button.grid(row=0, column=2)


image_label = customtkinter.CTkLabel(tab_general, text="")
image_label.grid(row=1, column=0)
detected_image_label = customtkinter.CTkLabel(tab_general, text="")
detected_image_label.grid(row=1, column=1)

detected_spell_label = customtkinter.CTkLabel(tab_general, text="Spell: .")
detected_spell_label.grid(row=2, column=1)
detected_keybind_label = customtkinter.CTkLabel(tab_general, text="Keybind: .")
detected_keybind_label.grid(row=3, column=1)


toggle_keybind_label = customtkinter.CTkLabel(tab_general, text=f"Toggle bot: '{cfg.toggle_keybind}'")
toggle_keybind_label.grid(row=2, column=0)

bot_running_label = customtkinter.CTkLabel(tab_general, text=f"Bot running: {play}")
bot_running_label.grid(row=3, column=0)

bot_textbox = customtkinter.CTkTextbox(tab_general, state="disabled")
bot_textbox.grid(row=4, columnspan=3, sticky="nsew")


def mse(imageA: npt.NDArray, imageB: npt.NDArray) -> float:
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err = float(err) / float(imageA.shape[0] * imageA.shape[1])
    return err


def detect(
    img: Image.Image, spec_with_icons: list[tuple[SpecKeybind, Image.Image]]
) -> tuple[float, SpecKeybind, Image.Image]:
    mses = [
        (float(mean_squared_error(np.array(img), np.array(cmp))), spec_keybind, cmp)
        for spec_keybind, cmp in spec_with_icons
    ]
    min_mse = min(mses, key=lambda x: x[0])
    return min_mse


while True:
    try:
        img = ImageGrab.grab(
            (cfg.looker_x, cfg.looker_y, cfg.looker_x + cfg.looker_size, cfg.looker_y + cfg.looker_size)
        ).resize((56, 56), Image.Resampling.LANCZOS)
        looker_img = customtkinter.CTkImage(light_image=img, size=(56, 56))
        if tabview.get() == "Looker":
            looker_image_label.configure(image=looker_img)
        else:
            image_label.configure(image=looker_img)

        if spec_with_icons:
            mse_val, spec_keybind, cmp = detect(img, spec_with_icons)
            detected_image_label.configure(image=customtkinter.CTkImage(light_image=cmp, size=(56, 56)))
            detected_spell_label.configure(text=f"Spell: {spec_keybind.spell}")
            detected_keybind_label.configure(text=f"Keybind: {spec_keybind.keybind}")
            bot_running_label.configure(text=f"Bot running: {play}")

            # if spec_keybind.spell == "tipthescales":
            #     img.save("dbg/img.png")
            #     cmp.save("dbg/cmp.png")
            #     for sk, i in spec_with_icons:
            #         i.save(f"dbg/{sk.spell}.png")

            #     exit()

            bot_textbox.configure(state="disabled")
            if play:
                keyboard.press_and_release(spec_keybind.keybind)
                bot_textbox.configure(state="normal")
                bot_textbox.insert(
                    "0.0",
                    f"{datetime.datetime.now().strftime('%H:%M:%S')}:'{spec_keybind.keybind}'->'{spec_keybind.spell}'\n",
                )

                sleep_time = (random.randint(10, 250) / 1000) + 0.2
                time.sleep(sleep_time)

        # app.update_idletasks()
        app.update()

    except RuntimeError as e:
        exit()
    except AttributeError:
        exit()
