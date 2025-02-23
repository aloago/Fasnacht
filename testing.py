import os
import pygame
from pygame.locals import *
from PIL import Image, ImageSequence

class PictureGridApp:
    def __init__(self, image_dir, banner_path, back_button_path, selections_dir, file_names, labels, priority_list, scaling_factor=1.0, loading_gif_path=None, background_path=None, loading_duration=2000):
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
        self.loading_duration = loading_duration  # Duration in milliseconds

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        # Set up colors
        self.grid_bg_color = (67, 135, 186)  # Blue color
        self.font_color = (255, 255, 255)      # White color
        self.banner_color = (255, 255, 0)      # Yellow for the banner
        self.highlight_color = (255, 255, 0)   # Yellow for highlighting

        # Set up fonts
        self.font = pygame.font.Font(None, int(24 * self.scaling_factor))  # For labels
        self.title_font = pygame.font.SysFont('Arial', int(24 * self.scaling_factor))  # For banner title

        # Set up image size and grid-related attributes
        self.image_size = (int(139 * self.scaling_factor), int(139 * self.scaling_factor))
        self.grid_x_spacing = int(30 * self.scaling_factor)
        self.grid_y_spacing = int(30 * self.scaling_factor)
        self.banner_height = int(100 * self.scaling_factor)

        # Calculate the square block size and position
        self.square_size = min(self.screen_width, self.screen_height)
        self.square_x = (self.screen_width - self.square_size) // 10
        self.square_y = (self.screen_height - self.square_size) // 2

        # Pre-render images and labels to cache surfaces (optimization)
        self.image_cache = {}
        self.pre_render_images()
        self.precompute_grid_positions()  # Pre-calculate image positions (avoids doing it every frame)
        self.pre_render_labels()          # Pre-render label surfaces

        # Set up loading screen
        self.loading_frames = []
        self.setup_loading_screen()

        # Set up background image
        self.background_image = None
        self.setup_background()

        # Set up state variables
        self.clicked_images = set()  # Use a set to track selected images

        # Start the main loop
        self.running = True
        self.main_loop()

    def setup_background(self):
        """Load and scale the background image if provided."""
        if self.background_path and os.path.exists(self.background_path):
            self.background_image = pygame.image.load(self.background_path)
            self.background_image = pygame.transform.scale(self.background_image, (self.square_size, self.square_size))

    def pre_render_images(self):
        """Load, scale, and cache all grid images."""
        for image_file in self.file_names:
            image_path = os.path.join(self.image_dir, image_file)
            if os.path.exists(image_path):
                img = pygame.image.load(image_path)
                img = pygame.transform.scale(img, self.image_size)
                self.image_cache[image_file] = img
            else:
                print(f"Warning: File {image_file} not found in {self.image_dir}. Skipping.")

    def precompute_grid_positions(self):
        """Precompute and store the positions (as Rects) for each image in the grid."""
        self.image_rects = []
        for idx in range(len(self.file_names)):
            row = idx // 5
            col = idx % 5
            x = self.square_x + col * (self.image_size[0] + self.grid_x_spacing) + self.grid_x_spacing
            y = self.square_y + row * (self.image_size[1] + self.grid_y_spacing) + self.banner_height + self.grid_y_spacing
            rect = pygame.Rect(x, y, self.image_size[0], self.image_size[1])
            self.image_rects.append(rect)

    def pre_render_labels(self):
        """Pre-render label text surfaces and store their positions."""
        self.label_surfaces = []
        self.label_rects = []
        for idx, label in enumerate(self.labels):
            label_surface = self.font.render(label, True, self.font_color)
            # Position label below its corresponding image
            rect = self.image_rects[idx]
            label_rect = label_surface.get_rect(center=(rect.x + self.image_size[0] // 2, rect.y + self.image_size[1] + 20))
            self.label_surfaces.append(label_surface)
            self.label_rects.append(label_rect)

    def setup_loading_screen(self):
        """Set up the loading screen using a GIF if available."""
        if self.loading_gif_path and os.path.exists(self.loading_gif_path):
            self.loading_gif = Image.open(self.loading_gif_path)
            self.loading_frames = [
                pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                for frame in ImageSequence.Iterator(self.loading_gif)
            ]
            self.loading_frames = [pygame.transform.scale(frame, (self.square_size, self.square_size)) for frame in self.loading_frames]
            self.current_frame = 0

    def display_banner(self):
        """Display a banner with a rounded yellow rectangle and centered title text."""
        banner_text = "Randomisiere zwei Mottos - Randomize two Themes"
        banner_surface = self.title_font.render(banner_text, True, (0, 0, 0))  # Black text

        banner_rect_width = self.square_size - 2 * self.grid_x_spacing
        banner_rect_height = self.banner_height - 20  # Padding adjustment
        banner_rect_x = self.square_x + self.grid_x_spacing
        banner_rect_y = self.square_y + 10  # Top padding

        pygame.draw.rect(
            self.screen,
            self.banner_color,
            (banner_rect_x, banner_rect_y, banner_rect_width, banner_rect_height),
            border_radius=20
        )

        text_rect = banner_surface.get_rect(center=(banner_rect_x + banner_rect_width // 2, banner_rect_y + banner_rect_height // 2))
        self.screen.blit(banner_surface, text_rect)

    def display_image_grid(self):
        """Display the precomputed grid of images, labels, and highlight borders."""
        for idx, image_file in enumerate(self.file_names):
            rect = self.image_rects[idx]
            self.screen.blit(self.image_cache[image_file], (rect.x, rect.y))

            # If this image is selected, draw a yellow border around it.
            if image_file in self.clicked_images:
                border_rect = pygame.Rect(rect.x - 2, rect.y - 2, self.image_size[0] + 4, self.image_size[1] + 4)
                pygame.draw.rect(self.screen, self.highlight_color, border_rect, width=4)

            # Blit the pre-rendered label.
            self.screen.blit(self.label_surfaces[idx], self.label_rects[idx])

    def on_image_click(self, image_file):
        """Toggle image selection; if two images are selected, show the loading screen."""
        if image_file in self.clicked_images:
            self.clicked_images.remove(image_file)
        else:
            if len(self.clicked_images) < 2:
                self.clicked_images.add(image_file)

        if len(self.clicked_images) == 2:
            self.show_loading_screen()

    def show_loading_screen(self):
        """Display the loading screen for a fixed duration before showing the selection screen."""
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < self.loading_duration:
            if self.loading_frames:
                for frame in self.loading_frames:
                    self.screen.fill((0, 0, 0))
                    self.screen.blit(frame, (self.square_x, self.square_y))
                    pygame.display.flip()
                    pygame.time.delay(100)
                    if pygame.time.get_ticks() - start_time >= self.loading_duration:
                        break
            else:
                pygame.time.delay(100)
        self.show_selection_screen()

    def show_selection_screen(self):
        """Display the selection screen using the combined image and a back button."""
        self.screen.fill((0, 0, 0))
        if len(self.clicked_images) == 2:
            sorted_clicked_images = sorted(
                self.clicked_images,
                key=lambda x: self.priority_list[self.file_names.index(x)]
            )
            new_image_name = f"{os.path.splitext(sorted_clicked_images[0])[0]}-{os.path.splitext(sorted_clicked_images[1])[0]}.jpg"
            new_image_path = os.path.join(self.selections_dir, new_image_name)

            if os.path.exists(new_image_path):
                new_image = pygame.image.load(new_image_path)
                new_image = pygame.transform.scale(new_image, (self.square_size, self.square_size))
                self.screen.blit(new_image, (self.square_x, self.square_y))

                # Draw the back button
                back_button_rect = pygame.Rect(self.square_x + self.square_size - 210, self.square_y + self.square_size - 60, 200, 50)
                pygame.draw.rect(self.screen, (255, 255, 0), back_button_rect, border_radius=10)
                back_button_text = self.font.render("Back", True, (0, 0, 0))
                back_button_text_rect = back_button_text.get_rect(center=back_button_rect.center)
                self.screen.blit(back_button_text, back_button_text_rect)

                pygame.display.flip()

                # Wait for a click on the back button
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                            waiting = False
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if back_button_rect.collidepoint(event.pos):
                                waiting = False
                                self.reset_selection()

    def reset_selection(self):
        """Reset image selections and return to the grid."""
        self.clicked_images = set()
        # Instead of calling main_loop() again (which can nest loops), simply continue running.
        # The main loop below will re-render the grid.
    
    def main_loop(self):
        """Main event loop: handles events and redraws the screen."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Use precomputed rects for hit detection
                    for idx, image_file in enumerate(self.file_names):
                        if self.image_rects[idx].collidepoint(event.pos):
                            self.on_image_click(image_file)

            self.screen.fill((0, 0, 0))  # Clear the entire screen

            # Draw the background within the grid block
            if self.background_image:
                self.screen.blit(self.background_image, (self.square_x, self.square_y))

            self.display_banner()
            self.display_image_grid()

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_DIR = os.path.join(BASE_DIR, "Images", "Grid")
    BANNER_PATH = os.path.join(BASE_DIR, "Images", "Other", "banner.png")
    BACK_BUTTON_PATH = os.path.join(BASE_DIR, "Images", "Other", "backbutton.png")
    SELECTIONS_DIR = os.path.join(BASE_DIR, "Images", "Selections")
    LOADING_GIF_PATH = os.path.join(BASE_DIR, "Images", "Other", "loading.gif")
    BACKGROUND_PATH = os.path.join(BASE_DIR, "Images", "Other", "background_2.jpg")

    FILE_NAMES = ["fritschi.jpg", "hexe.jpg", "spoerri.jpg", "basler.jpg", "fisch.jpg", 
                  "affe.jpg", "sau.jpg", "krieger.jpg", "clown.jpg", "hase.jpg", 
                  "einhorn.png", "grinch.jpg", "alien.jpg", "teufel.jpg", "guy.jpg", 
                  "ueli.jpg", "steampunk.jpg", "pippi.jpg", "wonderwoman.jpg", "federer.jpg"]
    LABELS = ["zünftig", "rüüdig", "kult-urig", "appropriated", "laborig", "huereaffig", 
              "sauglatt", "kriegerisch", "creepy", "cute", "magisch", "cringe", 
              "extraterrestrisch", "teuflisch", "random", "schwurblig", "boomerig", 
              "feministisch", "superstark", "bönzlig"]
    PRIORITY_LIST = [1, 2, 3, 4, 13, 6, 7, 8, 9, 10, 11, 17, 5, 14, 15, 16, 12, 18, 19, 20]

    app = PictureGridApp(IMAGE_DIR, BANNER_PATH, BACK_BUTTON_PATH, SELECTIONS_DIR, FILE_NAMES, LABELS, PRIORITY_LIST,
                         scaling_factor=1.37, loading_gif_path=LOADING_GIF_PATH, background_path=BACKGROUND_PATH, loading_duration=2000)