import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os
import sys
import pygame
import time

class MemoryGame:
    def __init__(self, master, images, rows, cols):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.images = images * 2
        self.x = 0
        random.shuffle(self.images)

        self.buttons = []
        self.matches = 0
        self.prev_button = None
        self.prev_index = None

        self.default_image = Image.new('RGB', (200, 200), color='white') 
        self.default_photo = ImageTk.PhotoImage(self.default_image)

        self.image_objects = [Image.open(image).resize((200, 200)) for image in self.images]
        self.photo_objects = [ImageTk.PhotoImage(img) for img in self.image_objects]

        self.create_widgets()

        pygame.init()

    def create_widgets(self):
        for i in range(self.rows):
            for j in range(self.cols):
                button = tk.Button(self.master, width=200, height=200, image=self.default_photo, command=lambda row=i, col=j: self.flip(row, col))
                button.grid(row=i, column=j)
                self.buttons.append(button)

    def flip(self, row, col):
        index = row * self.cols + col
        if self.buttons[index]["state"] == tk.DISABLED or self.prev_button == self.buttons[index]:
            return

        self.buttons[index].config(image=self.photo_objects[index])
        self.buttons[index].config(state=tk.DISABLED)

        if self.prev_button:
            self.x += 1
            if self.images[index] == self.images[self.prev_index]:
                self.matches += 1
                if self.matches == len(self.images) // 2:
                    messagebox.showinfo("Memory Game", "Congratulations! You won!")
                    print(f"Tentatives : {self.x}")
                    self.master.destroy()
                else:
                    self.correctMatch(self.prev_index, index)
            else:
                self.master.after(500, self.hide, index, self.prev_index)
            self.prev_button = None
            self.prev_index = None
        else:
            self.prev_button = self.buttons[index]
            self.prev_index = index

    def correctMatch(self, index1, index2):
        self.buttons[index1].config(highlightbackground="green", highlightthickness=2)
        self.buttons[index2].config(highlightbackground="green", highlightthickness=2)

    def hide(self, index1, index2):
        self.buttons[index1].config(image=self.default_photo)
        self.buttons[index1].config(state=tk.NORMAL)
        self.buttons[index2].config(image=self.default_photo)
        self.buttons[index2].config(state=tk.NORMAL)
    
    def music_player():
        time.sleep(2)
        pygame.mixer.music.load("relaxing-145038.mp3")
        pygame.mixer.music.play()

        start_time = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start_time < 10000:  # 10 seconds in milliseconds
            pygame.time.Clock().tick(30)  # Limit frame rate to 30 FPS

        pygame.mixer.music.stop()
    
        pygame.quit()


def main(input):
    # List of image file names
    image_folder = input  # Folder containing images
    images = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(".jpeg") or file.endswith(".avif") or file.endswith(".png")]

    root = tk.Tk()
    root.title("Memory Game")

    game = MemoryGame(root, images, len(images) // 2, len(images) // 2)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        main()
    else:
        root = tk.Tk()
        root.title("Memory Game")

        # List of image file names
        image_folder = "images"  # Folder containing images
        images = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(".jpeg") or file.endswith(".avif")]

        game = MemoryGame(root, images)
        root.mainloop()
