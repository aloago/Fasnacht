import os
from tkinter import Tk, Frame, Label, Canvas, Button
from tkinter.font import Font
from PIL import Image, ImageTk, ImageSequence

class PictureGridApp:
    def __init__(self, root, image_dir, banner_path, back_button_path, selections_dir, file_names, labels, priority_list, scaling_factor=1.0, loading_gif_path=None, background_path=None):
        self.root = root
        self.image_dir = image_dir
        self.banner_path = banner_path
        self.back_button_path = back_button_path
        self.selections_dir = selections_dir
        self.file_names = file_names
        self.labels = labels
        self.priority_list = priority_list
        self.scaling_factor = scaling_factor
        self.loading_gif_path = loading_gif_path
        self.background_path = background_path

        self.grid_bg_color = "#4387ba"

        if len(self.file_names) != len(self.labels) or len(self.file_names) != len(self.priority_list):
            raise ValueError("Mismatched lengths for file_names, labels, and priority_list.")

        self.root.attributes("-fullscreen", True)
        self.root.protocol("WM_DELETE_WINDOW", self.do_nothing)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.square_size = min(self.screen_width, self.screen_height)
        self.square_x = 0
        self.square_y = (self.screen_height - self.square_size) // 10

        self.background_canvas = Canvas(self.root, width=self.screen_width, height=self.screen_height, bg="black", highlightthickness=0)
        self.background_canvas.pack(fill="both", expand=True)

        self.square_frame = Frame(self.root, width=self.square_size, height=self.square_size, bg="black", highlightthickness=0)
        self.square_frame.place(x=self.square_x, y=self.square_y)

        # Main and Selection Frames
        self.main_frame = Frame(self.square_frame, bg="black", highlightthickness=0)
        self.selection_frame = Frame(self.square_frame, bg="black", highlightthickness=0)
        self.main_frame.pack(fill='both', expand=True)
        self.selection_frame.pack_forget()

        self.setup_background()

        self.grid_y_spacing = int(9 * self.scaling_factor)
        self.grid_x_spacing = int(13 * self.scaling_factor)
        self.image_size = (int(150 * self.scaling_factor), int(150 * self.scaling_factor))
        self.banner_height = int(100 * self.scaling_factor)
        self.font_color = "black"
        self.font_size = int(14 * self.scaling_factor)

        self.title_top_spacing = int(20 * self.scaling_factor)
        self.title_grid_spacing = int(10 * self.scaling_factor)

        self.loading_time = 3000
        self.back_button_width = 200
        self.back_button_height = 50
        self.back_button_x_offset = 1
        self.back_button_y_offset = 1

        self.clicked_images = []
        self.image_labels = []  # To track image labels for highlight reset
        self.image_cache = {}

        self.root.title("Kombiniere zwei Masken")

        # Pre-render images and setup loading screen
        self.pre_render_images()
        self.setup_loading_screen()

        # Setup UI components
        self.display_banner()
        self.display_image_grid()
        self.setup_selection_frame()

    def setup_background(self):
        if self.background_path and os.path.exists(self.background_path):
            self.background_image = Image.open(self.background_path)
            self.background_image = self.background_image.resize((self.square_size, self.square_size), Image.Resampling.LANCZOS)
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.background_label = Label(self.square_frame, image=self.background_photo, bg="black")
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.background_label = None

    def pre_render_images(self):
        self.image_cache = {}
        for image_file in self.file_names:
            image_path = os.path.join(self.image_dir, image_file)
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img = img.resize(self.image_size, Image.Resampling.LANCZOS)
                self.image_cache[image_file] = ImageTk.PhotoImage(img)
            else:
                print(f"Warning: {image_file} not found.")

    def setup_loading_screen(self):
        if not self.loading_gif_path or not os.path.exists(self.loading_gif_path):
            self.loading_label = Label(self.square_frame, text="Loading...", font=("Helvetica", 24), fg="white", bg="black")
        else:
            self.loading_gif = Image.open(self.loading_gif_path)
            self.loading_frames = [
                ImageTk.PhotoImage(frame.resize((self.square_size, self.square_size), Image.Resampling.LANCZOS))
                for frame in ImageSequence.Iterator(self.loading_gif)
            ]
            self.loading_label = Label(self.square_frame, bg="black")
            self.current_frame = 0
        self.loading_label.pack_forget()

    def display_banner(self):
        banner_frame = Frame(self.main_frame, height=self.banner_height, bg="lightgray")
        banner_frame.pack(fill="x", padx=self.grid_x_spacing, pady=(self.title_top_spacing, self.title_grid_spacing))
        Label(banner_frame, text="Randomisiere zwei Mottos - Randomize two Themes", 
              font=("Helvetica", 24), fg="black", bg="yellow").pack(fill="both", expand=True)

    def display_image_grid(self):
        images_frame = Frame(self.main_frame, bg=self.grid_bg_color)
        images_frame.pack(fill="both", expand=True)

        self.image_labels = []
        for idx, image_file in enumerate(self.file_names):
            container_frame = Frame(images_frame, width=self.image_size[0], height=self.image_size[1] + 40, 
                                  bg=self.grid_bg_color, highlightthickness=0)
            container_frame.grid(row=idx // 5, column=idx % 5, padx=self.grid_x_spacing, pady=self.grid_y_spacing)
            container_frame.pack_propagate(False)

            photo = self.image_cache[image_file]
            img_label = Label(container_frame, image=photo, bg=self.grid_bg_color, highlightthickness=0)
            img_label.image = photo
            img_label.pack()
            self.image_labels.append(img_label)

            Label(container_frame, text=self.labels[idx], font=("Helvetica", self.font_size), 
                 fg="white", bg=self.grid_bg_color).pack(pady=(5, 10))
            img_label.bind("<Button-1>", lambda e, f=image_file, l=img_label: self.on_image_click(f, l))

    def setup_selection_frame(self):
        # Combined image label
        self.combined_image_label = Label(self.selection_frame, bg="black", highlightthickness=0)
        self.combined_image_label.pack(fill="both", expand=True)

        # Back Button
        Button(self.selection_frame, text="← Back", bg="yellow", fg="black",
              font=("Helvetica", 16), relief="flat", command=self.reset_selection).place(
              relx=1.0, rely=1.0, anchor="se", width=200, height=50)

    def on_image_click(self, image_file, img_label):
        if image_file in self.clicked_images:
            self.clicked_images.remove(image_file)
            img_label.config(highlightthickness=0)
        else:
            if len(self.clicked_images) < 2:
                self.clicked_images.append(image_file)
                img_label.config(highlightthickness=4, highlightbackground="yellow")
        if len(self.clicked_images) == 2:
            self.show_loading_screen()

    def show_loading_screen(self):
        self.main_frame.pack_forget()
        self.loading_label.pack(fill="both", expand=True)
        if hasattr(self, "loading_frames"):
            self.play_gif()
        self.root.after(self.loading_time, self.stop_gif_and_show_selection_screen)

    def play_gif(self):
        if self.loading_label.winfo_exists():
            self.loading_label.config(image=self.loading_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.loading_frames)
            self.root.after(100, self.play_gif)

    def stop_gif_and_show_selection_screen(self):
        self.loading_label.pack_forget()
        self.show_selection_screen()

    def show_selection_screen(self):
        self.main_frame.pack_forget()
        self.selection_frame.pack(fill="both", expand=True)

        if len(self.clicked_images) == 2:
            try:
                sorted_clicked = sorted(self.clicked_images, key=lambda x: self.priority_list[self.file_names.index(x)])
                new_image_name = f"{os.path.splitext(sorted_clicked[0])[0]}-{os.path.splitext(sorted_clicked[1])[0]}.jpg"
                new_image_path = os.path.join(self.selections_dir, new_image_name)

                if os.path.exists(new_image_path):
                    new_image = Image.open(new_image_path).resize((self.square_size, self.square_size), Image.Resampling.LANCZOS)
                    new_photo = ImageTk.PhotoImage(new_image)
                    self.combined_image_label.config(image=new_photo)
                    self.combined_image_label.image = new_photo
            except Exception as e:
                print(f"Error loading image: {e}")

    def reset_selection(self):
        self.clicked_images = []
        for label in self.image_labels:
            label.config(highlightthickness=0)
        self.selection_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)

    def do_nothing(self):
        pass

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_DIR = os.path.join(BASE_DIR, "Images", "Grid")
    SELECTIONS_DIR = os.path.join(BASE_DIR, "Images", "Selections")
    LOADING_GIF_PATH = os.path.join(BASE_DIR, "Images", "Other", "loading.gif")
    BACKGROUND_PATH = os.path.join(BASE_DIR, "Images", "Other", "background_2.jpg")

    FILE_NAMES = ["fritschi.jpg", "hexe.jpg", "spoerri.jpg", "basler.jpg", "fisch.jpg", "affe.jpg", "sau.jpg", "krieger.jpg", "clown.jpg", "hase.jpg", "einhorn.png", "grinch.jpg", "alien.jpg", "teufel.jpg", "guy.jpg", "ueli.jpg", "steampunk.jpg", "pippi.jpg", "wonderwoman.jpg", "federer.jpg"]
    LABELS = ["zünftig", "rüüdig", "kult-urig", "appropriated", "laborig", "huereaffig", "sauglatt", "kriegerisch", "creepy", "cute", "magisch", "cringe", "extraterrestrisch", "teuflisch", "random", "schwurblig", "boomerig", "feministisch", "superstark", "bönzlig"]
    PRIORITY_LIST = [1, 2, 3, 4, 13, 6, 7, 8, 9, 10, 11, 17, 5, 14, 15, 16, 12, 18, 19, 20]

    root = Tk()
    app = PictureGridApp(root, IMAGE_DIR, None, None, SELECTIONS_DIR, FILE_NAMES, LABELS, PRIORITY_LIST, 
                        scaling_factor=1.37, loading_gif_path=LOADING_GIF_PATH, background_path=BACKGROUND_PATH)
    root.mainloop()