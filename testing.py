import os
import pygame
from pygame.locals import *
from PIL import Image, ImageSequence

class PictureGridApp:
    def __init__(self, image_dir, banner_path, back_button_path, selections_dir, file_names, labels, priority_list, scaling_factor=1.0, loading_gif_path=None, background_path=None):
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

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        # Set up colors
        self.grid_bg_color = (67, 135, 186)  # Blue color
        self.font_color = (255, 255, 255)  # White color

        # Set up fonts
        self.font = pygame.font.Font(None, int(24 * self.scaling_factor))

        # Set up images
        self.image_cache = {}
        self.pre_render_images()

        # Set up loading screen
        self.loading_frames = []
        self.setup_loading_screen()

        # Set up background
        self.background_image = None
        self.setup_background()

        # Set up grid
        self.grid_x_spacing = int(13 * self.scaling_factor)
        self.grid_y_spacing = int(9 * self.scaling_factor)
        self.image_size = (int(150 * self.scaling_factor), int(150 * self.scaling_factor))
        self.banner_height = int(100 * self.scaling_factor)

        # Set up state
        self.clicked_images = []
        self.selected_frames = {}

        # Start the main loop
        self.running = True
        self.main_loop()

    def setup_background(self):
        """Set up the background image."""
        if self.background_path and os.path.exists(self.background_path):
            self.background_image = pygame.image.load(self.background_path)
            self.background_image = pygame.transform.scale(self.background_image, (self.screen_width, self.screen_height))

    def pre_render_images(self):
        """Pre-render all images to the correct size and cache them."""
        for image_file in self.file_names:
            image_path = os.path.join(self.image_dir, image_file)
            if os.path.exists(image_path):
                img = pygame.image.load(image_path)
                img = pygame.transform.scale(img, self.image_size)
                self.image_cache[image_file] = img
            else:
                print(f"Warning: File {image_file} not found in {self.image_dir}. Skipping.")

    def setup_loading_screen(self):
        """Set up the loading screen with a GIF or static text."""
        if self.loading_gif_path and os.path.exists(self.loading_gif_path):
            self.loading_gif = Image.open(self.loading_gif_path)
            self.loading_frames = [
                pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                for frame in ImageSequence.Iterator(self.loading_gif)
            ]
            self.loading_frames = [pygame.transform.scale(frame, (self.screen_width, self.screen_height)) for frame in self.loading_frames]
            self.current_frame = 0

    def display_banner(self):
        """Display the banner at the top of the screen."""
        banner_text = "Randomisiere zwei Mottos - Randomize two Themes"
        banner_surface = self.font.render(banner_text, True, (0, 0, 0))  # Black text
        banner_rect = banner_surface.get_rect(center=(self.screen_width // 2, self.banner_height // 2))
        self.screen.blit(banner_surface, banner_rect)

    def display_image_grid(self):
        """Display the grid of images."""
        for idx, image_file in enumerate(self.file_names):
            row = idx // 5
            col = idx % 5
            x = col * (self.image_size[0] + self.grid_x_spacing) + self.grid_x_spacing
            y = row * (self.image_size[1] + self.grid_y_spacing) + self.banner_height + self.grid_y_spacing

            # Draw the image
            img = self.image_cache[image_file]
            self.screen.blit(img, (x, y))

            # Draw the label
            label_surface = self.font.render(self.labels[idx], True, self.font_color)
            label_rect = label_surface.get_rect(center=(x + self.image_size[0] // 2, y + self.image_size[1] + 20))
            self.screen.blit(label_surface, label_rect)

    def on_image_click(self, image_file):
        """Handle image click events."""
        if image_file in self.clicked_images:
            self.clicked_images.remove(image_file)
        else:
            if len(self.clicked_images) < 2:
                self.clicked_images.append(image_file)

        if len(self.clicked_images) == 2:
            self.show_loading_screen()

    def show_loading_screen(self):
        """Show the loading screen."""
        self.screen.fill((0, 0, 0))  # Clear the screen
        if self.loading_frames:
            self.play_gif()
        pygame.time.delay(3000)  # Simulate loading time
        self.show_selection_screen()

    def play_gif(self):
        """Play the loading GIF animation."""
        for frame in self.loading_frames:
            self.screen.blit(frame, (0, 0))
            pygame.display.flip()
            pygame.time.delay(100)

    def show_selection_screen(self):
        """Show the selection screen with the combined image."""
        self.screen.fill((0, 0, 0))  # Clear the screen

        if len(self.clicked_images) == 2:
            sorted_clicked_images = sorted(
                self.clicked_images,
                key=lambda x: self.priority_list[self.file_names.index(x)]
            )
            new_image_name = f"{os.path.splitext(sorted_clicked_images[0])[0]}-{os.path.splitext(sorted_clicked_images[1])[0]}.jpg"
            new_image_path = os.path.join(self.selections_dir, new_image_name)

            if os.path.exists(new_image_path):
                new_image = pygame.image.load(new_image_path)
                new_image = pygame.transform.scale(new_image, (self.screen_width, self.screen_height))
                self.screen.blit(new_image, (0, 0))

                # Draw the back button
                back_button_rect = pygame.Rect(self.screen_width - 210, self.screen_height - 60, 200, 50)
                pygame.draw.rect(self.screen, (255, 255, 0), back_button_rect)  # Yellow button
                back_button_text = self.font.render("← Back", True, (0, 0, 0))  # Black text
                back_button_text_rect = back_button_text.get_rect(center=back_button_rect.center)
                self.screen.blit(back_button_text, back_button_text_rect)

                pygame.display.flip()

                # Wait for back button click
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
        """Reset the selection and return to the image grid."""
        self.clicked_images = []
        self.selected_frames = {}
        self.main_loop()

    def main_loop(self):
        """Main loop to handle events and update the screen."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle image clicks
                    for idx, image_file in enumerate(self.file_names):
                        row = idx // 5
                        col = idx % 5
                        x = col * (self.image_size[0] + self.grid_x_spacing) + self.grid_x_spacing
                        y = row * (self.image_size[1] + self.grid_y_spacing) + self.banner_height + self.grid_y_spacing
                        rect = pygame.Rect(x, y, self.image_size[0], self.image_size[1])
                        if rect.collidepoint(event.pos):
                            self.on_image_click(image_file)

            self.screen.fill((0, 0, 0))  # Clear the screen
            if self.background_image:
                self.screen.blit(self.background_image, (0, 0))
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

    FILE_NAMES = ["fritschi.jpg", "hexe.jpg", "spoerri.jpg", "basler.jpg", "fisch.jpg", "affe.jpg", "sau.jpg", "krieger.jpg", "clown.jpg", "hase.jpg", "einhorn.png", "grinch.jpg", "alien.jpg", "teufel.jpg", "guy.jpg", "ueli.jpg", "steampunk.jpg", "pippi.jpg", "wonderwoman.jpg", "federer.jpg"]
    LABELS = ["zünftig", "rüüdig", "kult-urig", "appropriated", "laborig", "huereaffig", "sauglatt", "kriegerisch", "creepy", "cute", "magisch", "cringe", "extraterrestrisch", "teuflisch", "random", "schwurblig", "boomerig", "feministisch", "superstark", "bönzlig"]
    PRIORITY_LIST = [1, 2, 3, 4, 13, 6, 7, 8, 9, 10, 11, 17, 5, 14, 15, 16, 12, 18, 19, 20]  # Example priority list

    app = PictureGridApp(IMAGE_DIR, BANNER_PATH, BACK_BUTTON_PATH, SELECTIONS_DIR, FILE_NAMES, LABELS, PRIORITY_LIST, scaling_factor=1.37, loading_gif_path=LOADING_GIF_PATH, background_path=BACKGROUND_PATH)