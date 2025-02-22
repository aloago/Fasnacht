import tkinter as tk
from tkinter import PhotoImage

class ImageSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Selection Grid")

        # Configuration constants
        self.ROWS = 4
        self.COLS = 5
        self.IMAGE_SIZE = 50
        self.BORDER_WIDTH = 1
        self.CELL_PADDING = 1  # Further reduced padding
        self.TEXT_PADDING = 1

        # Dynamic window size
        window_width = (self.COLS * (self.IMAGE_SIZE + 2 * self.CELL_PADDING))
        window_height = (self.ROWS * (self.IMAGE_SIZE + 2 * self.CELL_PADDING + 20))
        self.root.geometry(f"{window_width}x{window_height}")

        self.CELL_SIZE = self.IMAGE_SIZE + 2 * self.CELL_PADDING + 20

        self.labels = []
        self.selected_images = []

        self.grid_frame = tk.Frame(self.root, padx=2, pady=2)
        self.grid_frame.pack(expand=True, fill="both")
        self.selection_frame = tk.Frame(self.root)

        self.create_grid()

    def create_placeholder_image(self, color):
        img = tk.PhotoImage(width=self.IMAGE_SIZE, height=self.IMAGE_SIZE)
        img.put(color, to=(0, 0, self.IMAGE_SIZE, self.IMAGE_SIZE))
        return img

    def on_picture_click(self, index):
        if index not in self.selected_images:
            self.labels[index].config(
                bg="lightblue", relief=tk.SOLID, borderwidth=self.BORDER_WIDTH
            )
            self.selected_images.append(index)

            if len(self.selected_images) == 2:
                self.show_selection_screen()

    def create_grid(self):
        for i in range(self.ROWS):
            for j in range(self.COLS):
                index = i * self.COLS + j
                img = self.create_placeholder_image(
                    f"#{50 + 20 * i:02x}{100 + 10 * j:02x}{150:02x}"
                )

                container_frame = tk.Frame(
                    self.grid_frame, width=self.CELL_SIZE, height=self.CELL_SIZE
                )
                container_frame.grid(row=i, column=j, padx=2, pady=2)
                container_frame.grid_propagate(False)

                frame = tk.Frame(container_frame, bg="white")
                frame.place(relx=0.5, rely=0.5, anchor="center")

                label = tk.Label(
                    frame,
                    image=img,
                    bg="white",
                    width=self.IMAGE_SIZE,
                    height=self.IMAGE_SIZE,
                    borderwidth=0,
                )
                label.image = img
                label.pack(pady=(0, self.TEXT_PADDING))

                text = tk.Label(
                    frame,
                    text=f"Image {index+1}",
                    bg="white",
                    font=("Arial", 7),  # Slightly smaller font
                )
                text.pack()

                label.bind("<Button-1>", lambda event, idx=index: self.on_picture_click(idx))

                self.labels.append(label)

    def show_selection_screen(self):
        self.grid_frame.pack_forget()
        self.selection_frame.pack(expand=True, fill="both")

        for widget in self.selection_frame.winfo_children():
            widget.destroy()

        selected_text = f"Selected Images: {[i+1 for i in self.selected_images]}"
        label = tk.Label(
            self.selection_frame, text=selected_text, font=("Arial", 12), pady=15
        )
        label.pack()

        back_button = tk.Button(
            self.selection_frame,
            text="Back",
            command=self.reset_selection,
            pady=8,
            padx=15,
            font=("Arial", 10),
        )
        back_button.pack()

    def reset_selection(self):
        for index in self.selected_images:
            self.labels[index].config(bg="white", relief=tk.FLAT, borderwidth=0)
        self.selected_images.clear()

        self.selection_frame.pack_forget()
        self.grid_frame.pack(expand=True, fill="both")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageSelector()
    app.run()
