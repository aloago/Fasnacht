import os
from tkinter import Tk, Frame, Label, Button, Canvas
from tkinter.font import Font
from PIL import Image, ImageTk

class PictureGridApp:
    def __init__(self, root, image_dir, banner_path, back_button_path, selections_dir, file_names, labels, scaling_factor=1.0):
        self.root = root
        self.image_dir = image_dir
        self.banner_path = banner_path
        self.back_button_path = back_button_path
        self.selections_dir = selections_dir  # Directory for derived images
        self.file_names = file_names  # List of file names to display
        self.labels = labels  # List of labels corresponding to the file names
        self.scaling_factor = scaling_factor

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
        self.clicked_images = []  # List to store clicked images
        self.selected_frames = {}  # Dictionary to track selected images and their frames

        # Configure the root window
        self.root.title("Picture Grid Viewer")
        self.root.geometry(f"{int(1000 * self.scaling_factor)}x{int(1000 * self.scaling_factor)}")
        self.selection_frame = None  # Initialize as None

        # Cache for resized images
        self.image_cache = {}

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

    def show_selection_screen(self):
        """Display a single image derived from the selected images, covering the entire window."""
        self.clear_window()

        # Sort the clicked_images based on their order in the file_names list
        sorted_clicked_images = sorted(self.clicked_images, key=lambda x: self.file_names.index(x))

        # Derive the new image file name from the sorted clicked images
        if len(sorted_clicked_images) == 2:
            new_image_name = f"{os.path.splitext(sorted_clicked_images[0])[0]}-{os.path.splitext(sorted_clicked_images[1])[0]}.jpg"
            new_image_path = os.path.join(self.selections_dir, new_image_name)

            # Check if the new image exists
            if not os.path.exists(new_image_path):
                print(f"Warning: File {new_image_name} not found in {self.selections_dir}.")
                return

            # Load and resize the new image to fit the window
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            new_image = Image.open(new_image_path)
            new_image = new_image.resize((window_width, window_height), Image.Resampling.LANCZOS)
            new_photo = ImageTk.PhotoImage(new_image)

            # Display the new image
            image_label = Label(self.root, image=new_photo)
            image_label.image = new_photo  # Keep a reference to prevent garbage collection
            image_label.pack(fill="both", expand=True)
            
            back_button_path = self.back_button_path

            if not os.path.exists(back_button_path):
                print(f"Warning: Back button image not found at {back_button_path}.")
                return

            back_button_image = Image.open(back_button_path)
            back_button_image = back_button_image.resize((50, 50), Image.Resampling.LANCZOS)  # Resize to 50x50
            back_button_photo = ImageTk.PhotoImage(back_button_image)

            # Create a back button with the image
            back_button = Button(
                self.root,
                image=back_button_photo,
                command=self.reset_selection,
                borderwidth=0,  # Remove border
                highlightthickness=0,  # Remove highlight
            )
            back_button.image = back_button_photo  # Keep a reference to prevent garbage collection
            back_button.place(relx=0.02, rely=0.95, anchor="sw")  # Place in the lower-left corner

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

        # If two images are selected, show the selection screen
        if len(self.clicked_images) == 2:
            self.show_selection_screen()


if __name__ == "__main__":
    # Configuration
    IMAGE_DIR = "C:\\Users\\remig\\Pictures\\Fasnacht\\Grid"
    BANNER_PATH = "C:\\Users\\remig\\Pictures\\Fasnacht\\Other\\banner.png"
    BACK_BUTTON_PATH = "C:\\Users\\remig\\Pictures\\Fasnacht\\Other\\backbutton.png"
    SELECTIONS_DIR = "C:\\Users\\remig\\Pictures\\Fasnacht\\Selections"  # Directory for derived images

    # List of file names and corresponding labels
    FILE_NAMES = ["fritschi.jpg", "hexe.jpg", "spoerri.jpg", "affe.jpg", "alien.jpg", "basler.jpg", "clown.jpg", "einhorn.jpg", "federer.jpg", "fisch.jpg", "grinch.jpg", "guy.jpg", "hase.jpg", "krieger.jpg", "pippi.jpg", "sau.jpg", "steampunk.jpg", "teufel.jpg", "ueli.jpg", "wonderwoman.jpg"]
    LABELS = ["Fritschi", "Hexe", "Spoerri", "Affe", "Alien", "Basler", "Clown", "Einhorn", "Federer", "Fisch", "Grinch", "Guy", "Hase", "Krieger", "Pippi", "Sau", "Steampunk", "Teufel", "Ueli", "Wonderwoman"]

    # Initialize and run the app
    root = Tk()
    app = PictureGridApp(root, IMAGE_DIR, BANNER_PATH, BACK_BUTTON_PATH, SELECTIONS_DIR, FILE_NAMES, LABELS, scaling_factor=0.6)  # Adjust scaling_factor as needed
    root.mainloop()