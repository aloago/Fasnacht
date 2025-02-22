import os
from tkinter import *
from tkinter.font import Font
from PIL import Image, ImageTk

class PictureGridApp:
    def __init__(self, root, image_dir, banner_path, scaling_factor=1.0):
        self.root = root
        self.image_dir = image_dir
        self.banner_path = banner_path
        self.scaling_factor = scaling_factor

        # Customization options (scaled)
        self.grid_y_spacing = int(5 * self.scaling_factor)
        self.grid_x_spacing = int(18 * self.scaling_factor)
        self.image_size = (int(150 * self.scaling_factor), int(150 * self.scaling_factor))  # Width, Height
        self.banner_height = int(100 * self.scaling_factor)
        self.font_color = "black"
        self.font_size = int(12 * self.scaling_factor)
        self.clicked_images = []  # List to store clicked images
        self.selected_labels = {}  # Dictionary to track selected images and their labels

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

        # Load image files
        image_files = [f for f in os.listdir(self.image_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
        image_files = image_files[:20]  # Limit to 20 images

        row = 0
        col = 0

        for image_file in image_files:
            # Create a frame for each image and label
            image_frame = Frame(images_frame, padx=self.grid_x_spacing, pady=self.grid_y_spacing)
            image_frame.grid(row=row, column=col)

            # Load and resize the image (use cached version if available)
            if image_file not in self.image_cache:
                image_path = os.path.join(self.image_dir, image_file)
                img = Image.open(image_path)
                img = img.resize(self.image_size)
                self.image_cache[image_file] = ImageTk.PhotoImage(img)

            photo = self.image_cache[image_file]

            # Display the image
            img_label = Label(image_frame, image=photo, borderwidth=0)  # No border initially
            img_label.image = photo  # Keep a reference to prevent garbage collection
            img_label.bind("<Button-1>", lambda e, file=image_file, label=img_label: self.on_image_click(file, label))
            img_label.pack()

            # Display the label under the image
            font = Font(family="Helvetica", size=self.font_size)
            text_label = Label(image_frame, text=image_file, font=font, fg=self.font_color)
            text_label.pack()

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
        """Display the selection screen with the selected images."""
        self.clear_window()

        # Reinitialize the selection frame
        self.selection_frame = Frame(self.root)
        self.selection_frame.pack(fill="both", expand=True)

        selected_text = "Selected images "+str(self.clicked_images)
        label = Label(
            self.selection_frame, text=selected_text, font=("Arial", 12), pady=15
        )
        label.pack()

        # Display the selected images
        for image_file in self.clicked_images:
            image_path = os.path.join(self.image_dir, image_file)
            img = Image.open(image_path)
            img = img.resize((100, 100))  # Resize for display
            photo = ImageTk.PhotoImage(img)

            img_label = Label(self.selection_frame, image=photo)
            img_label.image = photo  # Keep a reference to prevent garbage collection
            img_label.pack()

        back_button = Button(
            self.selection_frame,
            text="Back",
            command=self.reset_selection,
            pady=8,
            padx=15,
            font=("Arial", 10),
        )
        back_button.pack()

    def reset_selection(self):
        """Reset the selection and return to the image grid."""
        self.clicked_images = []
        self.selected_labels = {}  # Clear selected labels
        self.clear_window()
        self.display_banner()
        self.display_image_grid()

    def on_image_click(self, image_file, label):
        """Handle image click and store the clicked image file name."""
        if image_file in self.clicked_images:
            # Deselect the image if it's already selected
            self.clicked_images.remove(image_file)
            label.config(borderwidth=0)  # Remove border
            del self.selected_labels[image_file]
        else:
            # Select the image if it's not already selected
            if len(self.clicked_images) < 2:
                self.clicked_images.append(image_file)
                label.config(borderwidth=2, relief="solid")  # Add border
                self.selected_labels[image_file] = label

        # If two images are selected, show the selection screen
        if len(self.clicked_images) == 2:
            self.show_selection_screen()

if __name__ == "__main__":
    # Configuration
    IMAGE_DIR = "C:\\Users\\remig\\Pictures\\Fasnacht\\Grid"
    BANNER_PATH = "C:\\Users\\remig\\Pictures\\Fasnacht\\Other\\banner.png"

    # Initialize and run the app
    root = Tk()
    app = PictureGridApp(root, IMAGE_DIR, BANNER_PATH, scaling_factor=0.8)  # Adjust scaling_factor as needed
    root.mainloop()