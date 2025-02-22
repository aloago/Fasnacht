import os
from tkinter import Tk, Frame, Label, Button, Canvas, ttk
from tkinter.font import Font
from PIL import Image, ImageTk, ImageSequence

class PictureGridApp:
    def __init__(self, root, image_dir, banner_path, back_button_path, selections_dir, file_names, labels, scaling_factor=1.0, loading_gif_path=None):
        self.root = root
        self.image_dir = image_dir
        self.banner_path = banner_path
        self.back_button_path = back_button_path
        self.selections_dir = selections_dir  # Directory for derived images
        self.file_names = file_names  # List of file names to display
        self.labels = labels  # List of labels corresponding to the file names
        self.scaling_factor = scaling_factor
        self.loading_gif_path = loading_gif_path  # New parameter for the loading GIF path

        # Validate that file_names and labels have the same length
        if len(self.file_names) != len(self.labels):
            raise ValueError("The length of file_names and labels must be the same.")

        # Customization options (scaled)
        self.grid_y_spacing = int(5 * self.scaling_factor)
        self.grid_x_spacing = int(18 * self.scaling_factor)
        self.image_size = (int(150 * self.scaling_factor), int(150 * self.scaling_factor))  # Width, Height
        self.banner_height = int(100 * self.scaling_factor)
        self.font_color = "black"
        self.font_size = int(12 * self.scaling_factor)

        self.loading_time = 300  # Duration of the loading screen in milliseconds

        # Variables for the back button (using Option 2 – ttk Button)
        self.back_button_width = 100  # size in pixels (width and height)
        self.back_button_height = 33
        self.back_button_x_offset = 1  # relative x position (0.0 to 1.0)
        self.back_button_y_offset = 1  # relative y position (0.0 to 1.0)

        self.clicked_images = []  # List to store clicked images
        self.selected_frames = {}  # Dictionary to track selected images and their frames

        # Cache for resized images
        self.image_cache = {}

        # Configure the root window
        self.root.title("Picture Grid Viewer")
        self.root.geometry(f"{int(1000 * self.scaling_factor)}x{int(1000 * self.scaling_factor)}")
        self.selection_frame = None  # Initialize as None

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
        """Display a single image derived from the selected images, covering the entire window."""
        self.clear_window()

        # Sort the clicked_images based on their order in the file_names list
        sorted_clicked_images = sorted(self.clicked_images, key=lambda x: self.file_names.index(x))

        if len(sorted_clicked_images) == 2:
            new_image_name = f"{os.path.splitext(sorted_clicked_images[0])[0]}-{os.path.splitext(sorted_clicked_images[1])[0]}.jpg"
            new_image_path = os.path.join(self.selections_dir, new_image_name)

            if not os.path.exists(new_image_path):
                print(f"Warning: File {new_image_name} not found in {self.selections_dir}.")
                return

            # Load and resize the new image to fit the window
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            new_image = Image.open(new_image_path)
            new_image = new_image.resize((window_width, window_height), Image.Resampling.LANCZOS)
            new_photo = ImageTk.PhotoImage(new_image)

            background_label = Label(self.root, image=new_photo)
            background_label.image = new_photo  # Keep a reference
            background_label.pack(fill="both", expand=True)

            # Create a ttk Button styled as a flat button
            style = ttk.Style()
            style.configure("Flat.TButton",
                            relief="flat",
                            background=self.root.cget("bg"),
                            foreground="black",
                            borderwidth=0,
                            padding=0)  # No extra padding

            back_button = ttk.Button(self.root, text="← Back", style="Flat.TButton", command=self.reset_selection)
            
            # Place the button using the variables we defined
            # The width and height options in place() ensure the button has the desired pixel size.
            back_button.place(
                relx=self.back_button_x_offset,
                rely=self.back_button_y_offset,
                anchor="se",
                width=self.back_button_width,
                height=self.back_button_height
            )

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
    IMAGE_DIR = "C:\\Users\\remig\\Pictures\\Fasnacht\\Grid"
    BANNER_PATH = "C:\\Users\\remig\\Pictures\\Fasnacht\\Other\\banner.png"
    BACK_BUTTON_PATH = "C:\\Users\\remig\\Pictures\\Fasnacht\\Other\\backbutton.png"
    SELECTIONS_DIR = "C:\\Users\\remig\\Pictures\\Fasnacht\\Selections"  # Directory for derived images
    LOADING_GIF_PATH = "C:\\Users\\remig\\Pictures\\Fasnacht\\Other\\loading.gif"  # Path to the loading GIF

    # List of file names and corresponding labels
    FILE_NAMES = ["fritschi.jpg", "hexe.jpg", "spoerri.jpg", "affe.jpg", "alien.jpg", "basler.jpg", "clown.jpg", "einhorn.jpg", "federer.jpg", "fisch.jpg", "grinch.jpg", "guy.jpg", "hase.jpg", "krieger.jpg", "pippi.jpg", "sau.jpg", "steampunk.jpg", "teufel.jpg", "ueli.jpg", "wonderwoman.jpg"]
    LABELS = ["Fritschi", "Hexe", "Spoerri", "Affe", "Alien", "Basler", "Clown", "Einhorn", "Federer", "Fisch", "Grinch", "Guy", "Hase", "Krieger", "Pippi", "Sau", "Steampunk", "Teufel", "Ueli", "Wonderwoman"]

    # Initialize and run the app
    root = Tk()
    app = PictureGridApp(root, IMAGE_DIR, BANNER_PATH, BACK_BUTTON_PATH, SELECTIONS_DIR, FILE_NAMES, LABELS, scaling_factor=0.6, loading_gif_path=LOADING_GIF_PATH)  # Adjust scaling_factor as needed
    root.mainloop()