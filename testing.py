import os
from tkinter import Tk, Frame, Label, Canvas, Button
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
        self.clicked_images = []
        self.image_cache = {}

        # Validate input lengths
        if len(self.file_names) != len(self.labels) or len(self.file_names) != len(self.priority_list):
            raise ValueError("The length of file_names, labels, and priority_list must be the same.")

        # Set up the root window
        self.root.attributes("-fullscreen", True)
        self.root.protocol("WM_DELETE_WINDOW", self.do_nothing)

        # Hide the cursor
        self.root.config(cursor="none")  # This hides the cursor

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Set up the background canvas
        self.background_canvas = Canvas(self.root, width=self.screen_width, height=self.screen_height, bg="black", highlightthickness=0)
        self.background_canvas.pack(fill="both", expand=True)

        # Set up the square frame (main container)
        self.square_frame = Frame(self.root, width=self.screen_width, height=self.screen_height, bg="black", highlightthickness=0)
        self.square_frame.place(x=0, y=0)  # Position at the top-left corner

        # Set up the background
        self.setup_background()

        # Pre-render images and set up loading screen
        self.pre_render_images()
        self.setup_loading_screen()

        # Display the banner and image grid
        self.display_banner()
        self.display_image_grid()

    def setup_background(self):
        """Set up the background image."""
        if self.background_path and os.path.exists(self.background_path):
            self.background_image = Image.open(self.background_path)
            self.background_image = self.background_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.background_label = Label(self.square_frame, image=self.background_photo, bg="black")
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.background_label = None

    def pre_render_images(self):
        """Pre-render all images to the correct size and cache them."""
        self.image_cache = {}
        for image_file in self.file_names:
            image_path = os.path.join(self.image_dir, image_file)
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img = img.resize((int(150 * self.scaling_factor), int(150 * self.scaling_factor)), Image.Resampling.LANCZOS)
                self.image_cache[image_file] = ImageTk.PhotoImage(img)
            else:
                print(f"Warning: File {image_file} not found in {self.image_dir}. Skipping.")

    def setup_loading_screen(self):
        """Set up the loading screen with a GIF or static text."""
        if not self.loading_gif_path or not os.path.exists(self.loading_gif_path):
            print(f"Warning: Loading GIF not found at {self.loading_gif_path}.")
            self.loading_label = Label(self.square_frame, text="Loading...", font=("Helvetica", 24), fg="white", bg="black")
        else:
            self.loading_gif = Image.open(self.loading_gif_path)
            self.loading_frames = [
                ImageTk.PhotoImage(frame.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS))
                for frame in ImageSequence.Iterator(self.loading_gif)
            ]
            self.loading_label = Label(self.square_frame, bg="black", highlightthickness=0)
            self.current_frame = 0

        self.loading_label.pack_forget()  # Hide initially

    def display_banner(self):
        """Display the banner at the top of the screen."""
        banner_frame = Frame(self.square_frame, height=int(100 * self.scaling_factor), bg="lightgray")
        banner_frame.pack(fill="x", padx=int(13 * self.scaling_factor), pady=(int(20 * self.scaling_factor), int(10 * self.scaling_factor)))

        banner_label = Label(banner_frame, text="Randomisiere zwei Mottos - Randomize two Themes", font=("Helvetica", 24), fg="black", bg="yellow")
        banner_label.pack(fill="both", expand=True)

    def display_image_grid(self):
        """Display the grid of images."""
        # Clear any existing widgets in the square_frame
        self.clear_window()

        # Ensure the square_frame uses the full screen dimensions
        self.square_frame.config(width=self.screen_width, height=self.screen_height)
        self.square_frame.place(x=0, y=0)  # Position at the top-left corner

        # Set up the banner
        self.display_banner()

        # Create a frame for the grid of images
        images_frame = Frame(self.square_frame, bg=self.grid_bg_color, highlightthickness=0)
        images_frame.pack(fill="both", expand=True, padx=int(13 * self.scaling_factor), pady=(0, int(1 * self.scaling_factor)))

        # Calculate the number of rows and columns for the grid
        num_columns = 5
        num_rows = (len(self.file_names) + num_columns - 1) // num_columns

        # Calculate the size of each image container
        container_width = int((self.screen_width - (num_columns + 1) * int(13 * self.scaling_factor)) / num_columns)
        container_height = int((self.screen_height - self.banner_height - (num_rows + 1) * int(1 * self.scaling_factor)) / num_rows)

        # Display the images in the grid
        for idx, image_file in enumerate(self.file_names):
            # Create a container frame for each image
            container_frame = Frame(
                images_frame,
                width=container_width,
                height=container_height,
                bg=self.grid_bg_color,
                highlightthickness=0
            )
            container_frame.grid(
                row=idx // num_columns,
                column=idx % num_columns,
                padx=int(13 * self.scaling_factor),
                pady=int(1 * self.scaling_factor)
            )
            container_frame.pack_propagate(False)

            # Display the image
            photo = self.image_cache[image_file]
            img_label = Label(container_frame, image=photo, bg=self.grid_bg_color, highlightthickness=0)
            img_label.image = photo
            img_label.pack()

            # Display the label below the image
            text_label = Label(
                container_frame,
                text=self.labels[idx],
                font=("Helvetica", int(14 * self.scaling_factor)),
                fg="white",
                bg=self.grid_bg_color
            )
            text_label.pack(pady=(5, 10))

            # Bind click event to the image
            img_label.bind("<Button-1>", lambda e, file=image_file, label=img_label: self.on_image_click(file, label))

    def on_image_click(self, image_file, img_label):
        """Handle image click events."""
        if image_file in self.clicked_images:
            # If the image is already selected, deselect it
            self.clicked_images.remove(image_file)
            img_label.config(highlightthickness=0)  # Remove the border
        else:
            if len(self.clicked_images) < 2:
                # If the image is not selected and fewer than 2 images are selected, select it
                self.clicked_images.append(image_file)
                img_label.config(
                    highlightthickness=4,  # Add a border
                    highlightbackground="yellow"  # Set the border color to yellow
                )

        # If two images are selected, show the loading screen
        if len(self.clicked_images) == 2:
            self.show_loading_screen()

    def show_loading_screen(self):
        """Show the loading screen."""
        self.clear_window()
        self.loading_label.pack(fill="both", expand=True)
        if hasattr(self, "loading_frames"):
            self.play_gif()
        self.root.after(3000, self.stop_gif_and_show_selection_screen)

    def play_gif(self):
        """Play the loading GIF animation."""
        if hasattr(self, "loading_label") and self.loading_label.winfo_exists():
            self.loading_label.config(image=self.loading_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.loading_frames)
            self.root.after(100, self.play_gif)

    def stop_gif_and_show_selection_screen(self):
        """Stop the GIF and show the selection screen."""
        if hasattr(self, "loading_label"):
            self.loading_label.pack_forget()  # Hide the loading label
        self.show_selection_screen()

    def show_selection_screen(self):
        """Show the selection screen with the combined image."""
        self.clear_window()

        if len(self.clicked_images) == 2:
            try:
                # Sort based on priority_list
                sorted_clicked_images = sorted(
                    self.clicked_images,
                    key=lambda x: self.priority_list[self.file_names.index(x)]
                )
                # Create the combined file name
                new_image_name = f"{os.path.splitext(sorted_clicked_images[0])[0]}-{os.path.splitext(sorted_clicked_images[1])[0]}.jpg"
                new_image_path = os.path.join(self.selections_dir, new_image_name)

                if os.path.exists(new_image_path):
                    # Load and display the combined image
                    new_image = Image.open(new_image_path)
                    new_image = new_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
                    new_photo = ImageTk.PhotoImage(new_image)
                    Label(self.square_frame, image=new_photo, bg="black", highlightthickness=0).pack(fill="both", expand=True)

                    # Add the back button
                    Button(
                        self.square_frame,
                        text="← Back",
                        bg="yellow",
                        fg="black",
                        font=("Helvetica", 16),
                        relief="flat",
                        command=self.reset_selection
                    ).place(relx=1.0, rely=1.0, anchor="se", width=200, height=50)
            except Exception as e:
                print(f"Error: {e}")

    def reset_selection(self):
        """Reset the selection and return to the image grid."""
        self.clicked_images = []
        self.clear_window()
        self.setup_background()
        self.display_banner()
        self.display_image_grid()

    def clear_window(self):
        """Clear all widgets from the square frame except the background and loading labels."""
        for widget in self.square_frame.winfo_children():
            if widget not in [self.background_label, self.loading_label]:
                widget.destroy()

    def do_nothing(self):
        """Override the close button to do nothing."""
        pass


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_DIR = os.path.join(BASE_DIR, "Images", "Grid")
    BANNER_PATH = os.path.join(BASE_DIR, "Images", "Other", "banner.png")
    BACK_BUTTON_PATH = os.path.join(BASE_DIR, "Images", "Other", "backbutton.png")
    SELECTIONS_DIR = os.path.join(BASE_DIR, "Images", "Selections")
    LOADING_GIF_PATH = os.path.join(BASE_DIR, "Images", "Other", "loading.gif")
    BACKGROUND_PATH = os.path.join(BASE_DIR, "Images", "Other", "background_2.jpg")

    FILE_NAMES = ["fritschi.jpg", "hexe.jpg", "spoerri.jpg", "basler.jpg", "fisch.jpg", "affe.jpg", "sau.jpg", "krieger.jpg", "clown.jpg", "hase.jpg", "einhorn.png", "grinch.jpg", "alien.jpg", "teufel.jpg", "guy.jpg", "ueli.jpg", "steampunk.jpg", "pippi.jpg", "wonderwoman.jpg", "federer.jpg"]
    LABELS = ["zünftig", "rüüdig", "kult-urig", "appropriated", "laborig", "huereaffig", "sauglatt", "kriegerisch", "creepy", "cute", "magisch", "cringe", "extraterrestrisch", "teuflisch", "ramdom", "schwurblig", "boomerig", "feministisch", "superstark", "bönzlig"]
    PRIORITY_LIST = [1, 2, 3, 4, 13, 6, 7, 8, 9, 10, 11, 17, 5, 14, 15, 16, 12, 18, 19, 20]

    root = Tk()
    app = PictureGridApp(root, IMAGE_DIR, BANNER_PATH, BACK_BUTTON_PATH, SELECTIONS_DIR, FILE_NAMES, LABELS, PRIORITY_LIST, scaling_factor=1.4, loading_gif_path=LOADING_GIF_PATH, background_path=BACKGROUND_PATH)
    root.mainloop()