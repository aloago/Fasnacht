import os
import pygame
from pygame.locals import *
from PIL import Image, ImageSequence  # Added missing import

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
        self.loading_duration = loading_duration

        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        self.grid_bg_color = (67, 135, 186)
        self.font_color = (255, 255, 255)
        self.banner_color = (255, 255, 0)
        self.highlight_color = (255, 255, 0)

        self.font = pygame.font.Font(None, int(24 * self.scaling_factor))
        self.title_font = pygame.font.SysFont('Arial', int(24 * self.scaling_factor))

        self.image_size = (int(139 * self.scaling_factor), int(139 * self.scaling_factor))
        self.grid_x_spacing = int(30 * self.scaling_factor)
        self.grid_y_spacing = int(30 * self.scaling_factor)
        self.banner_height = int(100 * self.scaling_factor)

        self.square_size = min(self.screen_width, self.screen_height)
        self.square_x = (self.screen_width - self.square_size) // 10
        self.square_y = (self.screen_height - self.square_size) // 2

        self.image_cache = {}
        self.pre_render_images()

        self.loading_frames = []
        self.setup_loading_screen()

        self.background_image = None
        self.setup_background()

        self.clicked_images = set()
        self.selected_frames = {}

        self.running = True
        self.image_sprites = pygame.sprite.Group()
        self.image_rects = []
        self.image_labels = []
        self.create_image_sprites()

        self.main_loop()

    def setup_background(self):
        if self.background_path and os.path.exists(self.background_path):
            self.background_image = pygame.image.load(self.background_path)
            self.background_image = pygame.transform.scale(self.background_image, (self.square_size, self.square_size))

    def pre_render_images(self):
        for image_file in self.file_names:
            image_path = os.path.join(self.image_dir, image_file)
            if os.path.exists(image_path):
                img = pygame.image.load(image_path)
                img = pygame.transform.scale(img, self.image_size)
                self.image_cache[image_file] = img

    def setup_loading_screen(self):
        if self.loading_gif_path and os.path.exists(self.loading_gif_path):
            self.loading_gif = Image.open(self.loading_gif_path)
            self.loading_frames = [
                pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                for frame in ImageSequence.Iterator(self.loading_gif)
            ]
            self.loading_frames = [pygame.transform.scale(frame, (self.square_size, self.square_size)) for frame in self.loading_frames]
            self.current_frame = 0

    def create_image_sprites(self):
        for idx, image_file in enumerate(self.file_names):
            img = self.image_cache[image_file]
            # Use the Surface's copy method instead of a non-existent pygame.transform.copy()
            img_with_border = img.copy()
            border_rect = pygame.Rect(0, 0, img.get_width(), img.get_height())
            pygame.draw.rect(img_with_border, self.highlight_color, border_rect, 4)
            sprite = pygame.sprite.Sprite()
            sprite.image = img
            sprite.rect = pygame.Rect(self.get_image_position(idx), img.get_size())
            sprite.image_with_border = img_with_border
            self.image_sprites.add(sprite)
            self.image_rects.append(sprite.rect.copy())
            self.image_labels.append(self.labels[idx])

    def get_image_position(self, idx):
        row = idx // 5
        col = idx % 5
        x = self.square_x + col * (self.image_size[0] + self.grid_x_spacing) + self.grid_x_spacing
        y = self.square_y + row * (self.image_size[1] + self.grid_y_spacing) + self.banner_height + self.grid_y_spacing
        return (x, y)

    def display_banner(self):
        banner_text = "Randomisiere zwei Mottos - Randomize two Themes"
        banner_surface = self.title_font.render(banner_text, True, (0, 0, 0))
        banner_rect_width = self.square_size - 2 * self.grid_x_spacing
        banner_rect_height = self.banner_height - 20
        banner_rect_x = self.square_x + self.grid_x_spacing
        banner_rect_y = self.square_y + 10
        pygame.draw.rect(self.screen, self.banner_color, (banner_rect_x, banner_rect_y, banner_rect_width, banner_rect_height), border_radius=20)
        text_rect = banner_surface.get_rect(center=(banner_rect_x + banner_rect_width // 2, banner_rect_y + banner_rect_height // 2))
        self.screen.blit(banner_surface, text_rect)

    def on_image_click(self, image_file):
        if image_file in self.clicked_images:
            self.clicked_images.remove(image_file)
        else:
            if len(self.clicked_images) < 2:
                self.clicked_images.add(image_file)
        if len(self.clicked_images) == 2:
            self.show_loading_screen()

    def show_loading_screen(self):
        start_time = pygame.time.get_ticks()
        frame_duration = 100
        while pygame.time.get_ticks() - start_time < self.loading_duration:
            self.screen.fill((0, 0, 0))
            if self.loading_frames:
                current_frame = (self.current_frame // frame_duration) % len(self.loading_frames)
                self.screen.blit(self.loading_frames[current_frame], (self.square_x, self.square_y))
                self.current_frame += 1
            pygame.display.flip()
            self.clock.tick(60)
        self.show_selection_screen()

    def show_selection_screen(self):
        self.screen.fill((0, 0, 0))
        if len(self.clicked_images) == 2:
            sorted_images = sorted(self.clicked_images, key=lambda x: self.priority_list[self.file_names.index(x)])
            new_image_name = f"{os.path.splitext(sorted_images[0])[0]}-{os.path.splitext(sorted_images[1])[0]}.jpg"
            new_image_path = os.path.join(self.selections_dir, new_image_name)
            if os.path.exists(new_image_path):
                new_image = pygame.image.load(new_image_path)
                new_image = pygame.transform.scale(new_image, (self.square_size, self.square_size))
                self.screen.blit(new_image, (self.square_x, self.square_y))
                back_button_rect = pygame.Rect(self.square_x + self.square_size - 210, self.square_y + self.square_size - 60, 200, 50)
                pygame.draw.rect(self.screen, (255, 255, 0), back_button_rect, border_radius=10)
                back_button_text = self.font.render("Back", True, (0, 0, 0))
                back_button_text_rect = back_button_text.get_rect(center=back_button_rect.center)
                self.screen.blit(back_button_text, back_button_text_rect)
                pygame.display.flip()
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
        self.clicked_images = set()
        # Removed call to self.main_loop() to avoid nested loops.

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for idx, rect in enumerate(self.image_rects):
                        if rect.collidepoint(event.pos):
                            self.on_image_click(self.file_names[idx])

            self.screen.fill((0, 0, 0))
            if self.background_image:
                self.screen.blit(self.background_image, (self.square_x, self.square_y))
            self.display_banner()
            self.image_sprites.draw(self.screen)
            for idx, rect in enumerate(self.image_rects):
                if self.file_names[idx] in self.clicked_images:
                    x, y = rect.topleft
                    border_rect = pygame.Rect(x - 2, y - 2, self.image_size[0] + 4, self.image_size[1] + 4)
                    pygame.draw.rect(self.screen, self.highlight_color, border_rect, 4)
                label_surface = self.font.render(self.labels[idx], True, self.font_color)
                label_rect = label_surface.get_rect(center=(rect.centerx, rect.bottom + 20))
                self.screen.blit(label_surface, label_rect)
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
    PRIORITY_LIST = [1, 2, 3, 4, 13, 6, 7, 8, 9, 10, 11, 17, 5, 14, 15, 16, 12, 18, 19, 20]

    app = PictureGridApp(IMAGE_DIR, BANNER_PATH, BACK_BUTTON_PATH, SELECTIONS_DIR, FILE_NAMES, LABELS, PRIORITY_LIST,
                         scaling_factor=1.37, loading_gif_path=LOADING_GIF_PATH, background_path=BACKGROUND_PATH, loading_duration=2000)
