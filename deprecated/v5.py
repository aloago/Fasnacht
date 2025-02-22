import os
from tkinter import Tk, Frame, Label, Button, Canvas, ttk
from tkinter.font import Font
from PIL import Image, ImageTk, ImageSequence

class PictureGridApp:
    def __init__(self, root, image_dir, banner_path, back_button_path, selections_dir, 
                 file_names, labels, scaling_factor=1.0, loading_gif_path=None, 
                 background_path=None):
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

        self.grid_y_spacing = int(5 * self.scaling_factor)
        self.grid_x_spacing = int(18 * self.scaling_factor)
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
        self.root.geometry(f"{int(1000 * self.scaling_factor)}x{int(1000 * self.scaling_factor)}")
        self.selection_frame = None

        self.display_banner()
        self.display_image_grid()

    def display_banner(self):
        banner_frame = Frame(self.root, height=self.banner_height, bg="lightgray")
        banner_frame.pack(fill="x", padx=self.grid_x_spacing, pady=self.grid_y_spacing)

        title_label = Label(banner_frame, text="Picture Grid Viewer", font=("Helvetica", 24, "bold"), bg="lightgray", fg="black")
        title_label.pack(expand=True)

    def display_image_grid(self):
        images_frame = Canvas(self.root)
        images_frame.pack(fill="both", expand=True, padx=self.grid_x_spacing, pady=self.grid_y_spacing)

        if self.background_path and os.path.exists(self.background_path):
            try:
                self.bg_image_pil = Image.open(self.background_path)
                self.bg_photo = None

                def resize_background(event):
                    new_width = event.width
                    new_height = event.height
                    resized_bg = self.bg_image_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    self.bg_photo = ImageTk.PhotoImage(resized_bg)
                    images_frame.itemconfig(bg_image_id, image=self.bg_photo)

                images_frame.bind("<Configure>", resize_background)
                bg_image_id = images_frame.create_image(0, 0, anchor="nw", image=None)
                images_frame.event_generate("<Configure>", width=images_frame.winfo_width(), height=images_frame.winfo_height())
            except Exception as e:
                print(f"Error loading background image: {e}")

        row = 0
        col = 0
        max_cols = 5

        for idx, image_file in enumerate(self.file_names):
            image_path = os.path.join(self.image_dir, image_file)
            if not os.path.exists(image_path):
                print(f"Warning: File {image_file} not found in {self.image_dir}. Skipping.")
                continue

            container_frame = Frame(images_frame, width=self.image_size[0], height=self.image_size[1] + 20)
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

            x = col * (self.image_size[0] + 2 * self.grid_x_spacing)
            y = row * (self.image_size[1] + 20 + 2 * self.grid_y_spacing)

            images_frame.create_window(x, y, anchor="nw", window=container_frame)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        images_frame.update_idletasks()
        images_frame.config(scrollregion=images_frame.bbox("all"))

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_loading_screen(self):
        self.clear_window()

        if not self.loading_gif_path or not os.path.exists(self.loading_gif_path):
            print(f"Warning: Loading GIF not found at {self.loading_gif_path}.")
            self.show_selection_screen()
            return

        self.loading_gif = Image.open(self.loading_gif_path)
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        self.loading_frames = [
            ImageTk.PhotoImage(frame.resize((window_width, window_height), Image.Resampling.LANCZOS))
            for frame in ImageSequence.Iterator(self.loading_gif)
        ]

        self.loading_label = Label(self.root)
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

            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            new_image = Image.open(new_image_path)
            new_image = new_image.resize((window_width, window_height), Image.Resampling.LANCZOS)
            new_photo = ImageTk.PhotoImage(new_image)

            self.selection_canvas = Canvas(self.root)
            self.selection_canvas.pack(fill="both", expand=True)
            self.selection_canvas.create_image(0, 0, anchor="nw", image=new_photo)
            self.selection_canvas.image = new_photo

        style = ttk.Style()
        style.configure("Flat.TButton", relief="flat", background=self.root.cget("bg"), borderwidth=0)
        back_button = ttk.Button(self.root, text="← Back", style="Flat.TButton", command=self.reset_selection)
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
    app = PictureGridApp(
        root,
        IMAGE_DIR,
        BANNER_PATH,
        BACK_BUTTON_PATH,
        SELECTIONS_DIR,
        FILE_NAMES,
        LABELS,
        scaling_factor=0.9,
        loading_gif_path=LOADING_GIF_PATH,
        background_path=BACKGROUND_PATH
    )
    root.mainloop()