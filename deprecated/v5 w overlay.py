import os
from tkinter import Tk, Frame, Label, Button, Canvas, ttk
from tkinter.font import Font
from PIL import Image, ImageTk, ImageSequence

class PictureGridApp:
    def __init__(self, root, image_dir, banner_path, back_button_path, selections_dir, 
                 file_names, labels, scaling_factor=1.0, loading_gif_path=None, 
                 overlay_gif_path=None, overlay_x=0, overlay_y=0, overlay_scale_factor=1.0):
        # Add new overlay_scale_factor parameter
        self.overlay_scale_factor = overlay_scale_factor
        self.root = root
        self.image_dir = image_dir
        self.banner_path = banner_path
        self.back_button_path = back_button_path
        self.selections_dir = selections_dir
        self.file_names = file_names
        self.labels = labels
        self.scaling_factor = scaling_factor
        self.loading_gif_path = loading_gif_path
        self.overlay_gif_path = overlay_gif_path
        self.overlay_x = int(overlay_x * scaling_factor)  # Apply scaling
        self.overlay_y = int(overlay_y * scaling_factor)

        # Existing validation and setup...
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
        banner_frame = Frame(self.root, height=self.banner_height)
        banner_frame.pack(fill="x", padx=self.grid_x_spacing, pady=self.grid_y_spacing)

        banner_canvas = Canvas(banner_frame, height=self.banner_height)
        banner_canvas.pack(fill="x")

        # Load and resize the banner image
        banner_image = Image.open(self.banner_path)
        banner_image = banner_image.resize((round(1000 * self.scaling_factor), self.banner_height))
        banner_photo = ImageTk.PhotoImage(banner_image)

        banner_canvas.create_image(0, 0, anchor="nw", image=banner_photo)
        banner_canvas.image = banner_photo  # Keep a reference to prevent garbage collection

    def display_image_grid(self):
        images_frame = Frame(self.root)
        images_frame.pack(fill="both", expand=True, padx=self.grid_x_spacing, pady=self.grid_y_spacing)

        row = 0
        col = 0

        for idx, image_file in enumerate(self.file_names):
            # Check if the file exists in the image directory
            image_path = os.path.join(self.image_dir, image_file)
            if not os.path.exists(image_path):
                print(f"Warning: File {image_file} not found in {self.image_dir}. Skipping.")
                continue

            # Create a fixed-size container frame for each image and label
            container_frame = Frame(images_frame, width=self.image_size[0], height=self.image_size[1] + 20)
            container_frame.grid(row=row, column=col, padx=self.grid_x_spacing, pady=self.grid_y_spacing)
            container_frame.pack_propagate(False)  # Prevent the frame from resizing to fit its contents

            # Load and resize the image (use cached version if available)
            if image_file not in self.image_cache:
                img = Image.open(image_path)
                img = img.resize(self.image_size)
                self.image_cache[image_file] = ImageTk.PhotoImage(img)

            photo = self.image_cache[image_file]

            # Display the image inside the container frame
            img_label = Label(container_frame, image=photo)
            img_label.image = photo  # Keep a reference to prevent garbage collection
            img_label.pack()

            # Display the label under the image
            font = Font(family="Helvetica", size=self.font_size)
            text_label = Label(container_frame, text=self.labels[idx], font=font, fg=self.font_color)
            text_label.pack()

            # Bind click event to the image label
            img_label.bind("<Button-1>", lambda e, file=image_file, frame=container_frame: self.on_image_click(file, frame))

            # Update grid position
            col += 1
            if col >= 5:  # Move to next row after 5 columns
                col = 0
                row += 1

    def clear_window(self):
        """Destroy all widgets in the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_loading_screen(self):
        """Display a loading GIF over the entire window size for a specified time."""
        self.clear_window()

        if not self.loading_gif_path or not os.path.exists(self.loading_gif_path):
            print(f"Warning: Loading GIF not found at {self.loading_gif_path}.")
            self.show_selection_screen()  # Skip loading screen if GIF is missing
            return

        # Load the GIF
        self.loading_gif = Image.open(self.loading_gif_path)

        # Resize each frame of the GIF to match the window size
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        self.loading_frames = [
            ImageTk.PhotoImage(frame.resize((window_width, window_height), Image.Resampling.LANCZOS))
            for frame in ImageSequence.Iterator(self.loading_gif)
        ]

        # Create a label to display the GIF
        self.loading_label = Label(self.root)
        self.loading_label.pack(fill="both", expand=True)

        # Start playing the GIF
        self.current_frame = 0
        self.play_gif()

        # Schedule the transition to the selection screen after a delay (e.g., 3 seconds)
        self.root.after(self.loading_time, self.stop_gif_and_show_selection_screen)

    def play_gif(self):
        """Update the GIF frame to create animation."""
        if hasattr(self, "loading_label") and self.loading_label.winfo_exists():
            self.loading_label.config(image=self.loading_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.loading_frames)
            self.root.after(100, self.play_gif)  # Update every 100ms

    def stop_gif_and_show_selection_screen(self):
        """Stop the GIF animation and show the selection screen."""
        if hasattr(self, "loading_label"):
            self.loading_label.destroy()  # Destroy the loading label
        self.show_selection_screen()

    def show_selection_screen(self):
        """Display the selection screen with an optional animated overlay."""
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

            # Create canvas for background and overlay
            self.selection_canvas = Canvas(self.root)
            self.selection_canvas.pack(fill="both", expand=True)
            self.selection_canvas.create_image(0, 0, anchor="nw", image=new_photo)
            self.selection_canvas.image = new_photo

        if self.overlay_gif_path and os.path.exists(self.overlay_gif_path):
            self.overlay_gif = Image.open(self.overlay_gif_path)
            self.overlay_frames = []
            
            for frame in ImageSequence.Iterator(self.overlay_gif):
                # Convert to RGBA and scale
                frame = frame.convert("RGBA")
                original_width, original_height = frame.size
                new_size = (
                    int(original_width * self.overlay_scale_factor * self.scaling_factor),
                    int(original_height * self.overlay_scale_factor * self.scaling_factor)
                )
                frame = frame.resize(new_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(frame)
                self.overlay_frames.append(photo)

            # Position calculation with main scaling factor
            scaled_x = int(self.overlay_x * self.scaling_factor)
            scaled_y = int(self.overlay_y * self.scaling_factor)
            
            self.overlay_image_id = self.selection_canvas.create_image(
                scaled_x, scaled_y, anchor="nw", image=self.overlay_frames[0]
            )

            # Back button setup
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

    def animate_overlay_gif(self):
        """Cycle through overlay GIF frames."""
        if hasattr(self, 'overlay_image_id') and self.selection_canvas.winfo_exists():
            self.current_overlay_frame = (self.current_overlay_frame + 1) % len(self.overlay_frames)
            self.selection_canvas.itemconfig(self.overlay_image_id, image=self.overlay_frames[self.current_overlay_frame])
            self.root.after(100, self.animate_overlay_gif)  # Adjust frame rate as needed

    def reset_selection(self):
        """Reset the selection and return to the image grid."""
        self.clicked_images = []
        self.selected_frames = {}  # Clear selected frames
        self.clear_window()
        self.display_banner()
        self.display_image_grid()

    def on_image_click(self, image_file, frame):
        """Handle image click and store the clicked image file name."""
        if image_file in self.clicked_images:
            # Deselect the image if it's already selected
            self.clicked_images.remove(image_file)
            frame.config(borderwidth=0)  # Remove border
            del self.selected_frames[image_file]
        else:
            # Select the image if it's not already selected
            if len(self.clicked_images) < 2:
                self.clicked_images.append(image_file)
                frame.config(borderwidth=2, relief="solid")  # Add border
                self.selected_frames[image_file] = frame

        # If two images are selected, show the loading screen
        if len(self.clicked_images) == 2:
            self.show_loading_screen()

if __name__ == "__main__":
    # Configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_DIR = os.path.join(BASE_DIR, "Images", "Grid")
    BANNER_PATH = os.path.join(BASE_DIR, "Images", "Other", "banner.png")
    BACK_BUTTON_PATH = os.path.join(BASE_DIR, "Images", "Other", "backbutton.png")
    SELECTIONS_DIR = os.path.join(BASE_DIR, "Images", "Selections")
    LOADING_GIF_PATH = os.path.join(BASE_DIR, "Images", "Other", "loading.gif")
    OVERLAY_GIF_PATH = os.path.join(BASE_DIR, "Images", "Other", "overlay.gif")
    OVERLAY_X = 100  # Desired X position (before scaling)
    OVERLAY_Y = 200  # Desired Y position (before scaling)

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
        scaling_factor=1.1,
        loading_gif_path=LOADING_GIF_PATH,
        overlay_gif_path=OVERLAY_GIF_PATH,
        overlay_x=OVERLAY_X,
        overlay_y=OVERLAY_Y
    )
    root.mainloop()