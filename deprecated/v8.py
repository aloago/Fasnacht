import os
from tkinter import Tk, Frame, Label, Button, Canvas, ttk
from tkinter.font import Font
from PIL import Image, ImageTk, ImageSequence

class PictureGridApp:
    def __init__(self, root, image_dir, banner_path, back_button_path, selections_dir, file_names, labels, scaling_factor=1.0, loading_gif_path=None, background_path=None):
        self.root = root
        self.image_dir = image_dir
        self.banner_path = banner_path
        self.back_button_path = back_button_path
        self.selections_dir = selections_dir
        self.file_names = file_names
        self.labels = labels
        self.scaling_factor = scaling_factor
        self.loading_gif_path = loading_gif_path
        self.background_path = background_path

        if len(self.file_names) != len(self.labels):
            raise ValueError("The length of file_names and labels must be the same.")

        # Set the root window to full-screen mode
        self.root.attributes("-fullscreen", True)  # Enable full-screen mode

        # Disable the window close button (X button)
        self.root.protocol("WM_DELETE_WINDOW", self.do_nothing)  # Override close button

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Define the square layout dimensions (preserve aspect ratio)
        self.square_size = min(self.screen_width, self.screen_height)  # Size of the square layout
        self.square_x = (self.screen_width - self.square_size) # // 10  # X position to center the square
        self.square_y = (self.screen_height - self.square_size) // 10  # Y position to center the square ---Use this to adjust the position---

        # Create a black background canvas to fill the entire screen
        self.background_canvas = Canvas(self.root, width=self.screen_width, height=self.screen_height, bg="black", highlightthickness=0)
        self.background_canvas.pack(fill="both", expand=True)

        # Create a container frame for the square layout
        self.square_frame = Frame(self.root, width=self.square_size, height=self.square_size, bg="white")
        self.square_frame.place(x=self.square_x, y=self.square_y)

        # Customization options (scaled)
        self.grid_y_spacing = int(13.4 * self.scaling_factor)
        self.grid_x_spacing = int(13 * self.scaling_factor)
        self.image_size = (int(150 * self.scaling_factor), int(150 * self.scaling_factor))
        self.banner_height = int(100 * self.scaling_factor)
        self.font_color = "black"
        self.font_size = int(12 * self.scaling_factor)

        self.loading_time = 3000

        self.back_button_width = 100
        self.back_button_height = 33
        self.back_button_x_offset = 1
        self.back_button_y_offset = 1

        self.clicked_images = []
        self.selected_frames = {}
        self.image_cache = {}

        self.root.title("Picture Grid Viewer")
        self.selection_frame = None

        self.display_banner()
        self.display_image_grid()

    def do_nothing(self):
        """Override the close button to do nothing."""
        pass

    def display_banner(self):
        banner_frame = Frame(self.square_frame, height=self.banner_height, bg="lightgray")
        banner_frame.pack(fill="x", padx=self.grid_x_spacing, pady=self.grid_y_spacing)

        banner_label = Label(banner_frame, text="Picture Grid Viewer", font=("Helvetica", 24), fg="black", bg="lightgray")
        banner_label.pack(fill="both", expand=True)

    def display_image_grid(self):
        images_frame = Frame(self.square_frame)
        images_frame.pack(fill="both", expand=True, padx=self.grid_x_spacing, pady=self.grid_y_spacing)

        row = 0
        col = 0

        for idx, image_file in enumerate(self.file_names):
            image_path = os.path.join(self.image_dir, image_file)
            if not os.path.exists(image_path):
                print(f"Warning: File {image_file} not found in {self.image_dir}. Skipping.")
                continue

            container_frame = Frame(images_frame, width=self.image_size[0], height=self.image_size[1] + 20)
            container_frame.grid(row=row, column=col, padx=self.grid_x_spacing, pady=self.grid_y_spacing)
            container_frame.pack_propagate(False)

            if image_file not in self.image_cache:
                img = Image.open(image_path)
                img = img.resize(self.image_size)
                self.image_cache[image_file] = ImageTk.PhotoImage(img)

            photo = self.image_cache[image_file]

            img_label = Label(container_frame, image=photo)
            img_label.image = photo
            img_label.pack()

            font = Font(family="Helvetica", size=self.font_size)
            text_label = Label(container_frame, text=self.labels[idx], font=font, fg=self.font_color)
            text_label.pack()

            img_label.bind("<Button-1>", lambda e, file=image_file, frame=container_frame: self.on_image_click(file, frame))

            col += 1
            if col >= 5:
                col = 0
                row += 1

    def clear_window(self):
        """Destroy all widgets in the square frame."""
        for widget in self.square_frame.winfo_children():
            widget.destroy()

    def show_loading_screen(self):
        self.clear_window()

        if not self.loading_gif_path or not os.path.exists(self.loading_gif_path):
            print(f"Warning: Loading GIF not found at {self.loading_gif_path}.")
            self.show_selection_screen()
            return

        self.loading_gif = Image.open(self.loading_gif_path)

        # Resize the loading GIF to fit the square frame
        self.loading_frames = [
            ImageTk.PhotoImage(frame.resize((self.square_size, self.square_size), Image.Resampling.LANCZOS))
            for frame in ImageSequence.Iterator(self.loading_gif)
        ]

        self.loading_label = Label(self.square_frame)
        self.loading_label.pack(fill="both", expand=True)

        self.current_frame = 0
        self.play_gif()

        self.root.after(self.loading_time, self.stop_gif_and_show_selection_screen)

    def play_gif(self):
        if hasattr(self, "loading_label") and self.loading_label.winfo_exists():
            self.loading_label.config(image=self.loading_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.loading_frames)
            self.root.after(100, self.play_gif)

    def stop_gif_and_show_selection_screen(self):
        if hasattr(self, "loading_label"):
            self.loading_label.destroy()
        self.show_selection_screen()

    def show_selection_screen(self):
        self.clear_window()

        sorted_clicked_images = sorted(self.clicked_images, key=lambda x: self.file_names.index(x))

        if len(sorted_clicked_images) == 2:
            new_image_name = f"{os.path.splitext(sorted_clicked_images[0])[0]}-{os.path.splitext(sorted_clicked_images[1])[0]}.jpg"
            new_image_path = os.path.join(self.selections_dir, new_image_name)

            if not os.path.exists(new_image_path):
                print(f"Warning: File {new_image_name} not found in {self.selections_dir}.")
                return

            # Resize the new image to fit the square frame
            new_image = Image.open(new_image_path)
            new_image = new_image.resize((self.square_size, self.square_size), Image.Resampling.LANCZOS)
            new_photo = ImageTk.PhotoImage(new_image)

            background_label = Label(self.square_frame, image=new_photo)
            background_label.image = new_photo
            background_label.pack(fill="both", expand=True)

            style = ttk.Style()
            style.configure("Flat.TButton",
                            relief="flat",
                            background=self.root.cget("bg"),
                            foreground="black",
                            borderwidth=0,
                            padding=0)

            back_button = ttk.Button(self.square_frame, text="← Back", style="Flat.TButton", command=self.reset_selection)
            
            back_button.place(
                relx=self.back_button_x_offset,
                rely=self.back_button_y_offset,
                anchor="se",
                width=self.back_button_width,
                height=self.back_button_height
            )

    def reset_selection(self):
        self.clicked_images = []
        self.selected_frames = {}
        self.clear_window()
        self.display_banner()
        self.display_image_grid()

    def on_image_click(self, image_file, frame):
        if image_file in self.clicked_images:
            self.clicked_images.remove(image_file)
            frame.config(borderwidth=0)
            del self.selected_frames[image_file]
        else:
            if len(self.clicked_images) < 2:
                self.clicked_images.append(image_file)
                frame.config(borderwidth=2, relief="solid")
                self.selected_frames[image_file] = frame

        if len(self.clicked_images) == 2:
            self.show_loading_screen()


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_DIR = os.path.join(BASE_DIR, "Images", "Grid")
    BANNER_PATH = os.path.join(BASE_DIR, "Images", "Other", "banner.png")
    BACK_BUTTON_PATH = os.path.join(BASE_DIR, "Images", "Other", "backbutton.png")
    SELECTIONS_DIR = os.path.join(BASE_DIR, "Images", "Selections")
    LOADING_GIF_PATH = os.path.join(BASE_DIR, "Images", "Other", "loading.gif")
    BACKGROUND_PATH = os.path.join(BASE_DIR, "Images", "Other", "background_2.jpg")

    FILE_NAMES = ["fritschi.jpg", "hexe.jpg", "spoerri.jpg", "affe.jpg", "alien.jpg", "basler.jpg", "clown.jpg", "einhorn.png", "federer.jpg", "fisch.jpg", "grinch.jpg", "guy.jpg", "hase.jpg", "krieger.jpg", "pippi.jpg", "sau.jpg", "steampunk.jpg", "teufel.jpg", "ueli.jpg", "wonderwoman.jpg"]
    LABELS = ["Fritschi", "Hexe", "Spoerri", "Affe", "Alien", "Basler", "Clown", "Einhorn", "Federer", "Fisch", "Grinch", "Guy", "Hase", "Krieger", "Pippi", "Sau", "Steampunk", "Teufel", "Ueli", "Wonderwoman"]

    root = Tk()
    app = PictureGridApp(root, IMAGE_DIR, BANNER_PATH, BACK_BUTTON_PATH, SELECTIONS_DIR, FILE_NAMES, LABELS, scaling_factor=0.9, loading_gif_path=LOADING_GIF_PATH, background_path=BACKGROUND_PATH)
    root.mainloop()