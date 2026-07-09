import customtkinter as ctk
from PIL import Image
import pygame

class PygameViewport(ctk.CTkLabel):
    def __init__(self, master, width=400, height=400, **kwargs):
        super().__init__(master, text="", width=width, height=height, **kwargs)
        self.width = width
        self.height = height
        
        # Initialize an empty image
        self.empty_image = Image.new("RGB", (width, height), (30, 30, 30))
        self.ctk_image = ctk.CTkImage(light_image=self.empty_image, dark_image=self.empty_image, size=(width, height))
        self.configure(image=self.ctk_image)

    def draw_surface(self, surface: pygame.Surface, overlay_text=None):
        if surface is None:
            return
            
        # Convert Pygame surface to PIL Image
        # pygame.image.tostring returns a string buffer of RGB pixels
        raw_str = pygame.image.tostring(surface, "RGB", False)
        image = Image.frombytes("RGB", surface.get_size(), raw_str)
        
        # If sizes differ, resize to fit this widget
        if surface.get_size() != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

        if overlay_text:
            # We can use ImageDraw to add text, but for simplicity, 
            # we can just set the label's text attribute on top of the image
            self.configure(text=overlay_text, text_color="red", font=("Arial", 24, "bold"), compound="center")
        else:
            self.configure(text="")

        self.ctk_image.configure(light_image=image, dark_image=image, size=(self.width, self.height))
        self.configure(image=self.ctk_image)

    def draw_empty(self, text="WAITING..."):
        self.ctk_image.configure(light_image=self.empty_image, dark_image=self.empty_image, size=(self.width, self.height))
        self.configure(image=self.ctk_image, text=text, font=("Arial", 20, "bold"), text_color="gray", compound="center")
