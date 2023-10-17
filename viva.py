import keyboard
import time
import os
import random

import cv2
import numpy as np
import numpy.typing as npt

from PIL import ImageGrab, Image

global running
running = False


def toggle_running():
    global running
    running = not running


keyboard.add_hotkey("ctrl+alt+m", toggle_running, args=())


def mse(imageA: npt.NDArray, imageB: npt.NDArray) -> float:
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err = float(err) / float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def to_frame(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# img_files = os.listdir("augmentation")
profile = "devastation"
img_files = os.listdir(profile)
imgs = {}
for img_file in img_files:
    imgs[img_file.split(".")[0]] = np.array(Image.open(f"{profile}/{img_file}"))

while True:
    img = np.array(ImageGrab.grab((1782, 1015, 1827, 1060)))

    mses = [(mse(img, cmp), name) for name, cmp in imgs.items()]
    min_mse = min(mses, key=lambda x: x[0])
    key = min_mse[1]

    cv2.imshow("screen", to_frame(img))
    cv2.imshow("cmp", to_frame(imgs[key]))

    if running:
        key_converted = key.replace("s", "shift+").replace("c", "ctrl+")
        print(key_converted)
        keyboard.press_and_release(key_converted)

    if (cv2.waitKey(1) & 0xFF) == ord("k"):
        cv2.destroyAllWindows()
        break

    sleep_time = (random.randint(10, 250) / 1000) + 0.2
    time.sleep(sleep_time)
