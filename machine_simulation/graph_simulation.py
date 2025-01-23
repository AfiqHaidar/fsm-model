import tkinter as tk
from tkinter import filedialog
from PIL import Image as PILImage, ImageTk


class GraphSimulation(tk.Tk):
    def __init__(self, graph_path):
        super().__init__()
        self.title("Graph Simulation Viewer")
        self.graph_path = graph_path

        # Load the image using PIL to get its size
        try:
            self.img = PILImage.open(self.graph_path)
            self.img_width, self.img_height = self.img.size
        except Exception as e:
            print(f"Error loading image: {e}")
            return

        # Use the original image width and calculate the corresponding height to maintain the aspect ratio
        aspect_ratio = self.img_height / self.img_width
        new_width = self.img_width  # Dynamic width, based on original image size
        new_height = int(new_width * aspect_ratio)

        # Scale the image to the dynamic width while maintaining the aspect ratio
        self.scaled_img = self.img.resize(
            (new_width, new_height), PILImage.Resampling.LANCZOS)

        # Create canvas and scrollbars
        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.config(scrollregion=(0, 0, new_width, new_height))

        self.x_scrollbar = tk.Scrollbar(
            self, orient="horizontal", command=self.canvas.xview)
        self.x_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.config(xscrollcommand=self.x_scrollbar.set)

        self.y_scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.y_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.config(yscrollcommand=self.y_scrollbar.set)

        # Add the image to the canvas
        self.tk_img = ImageTk.PhotoImage(self.scaled_img)
        self.image_id = self.canvas.create_image(
            0, 0, anchor="nw", image=self.tk_img)

        # Set canvas size based on the scaled image size
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))

        # Save button
        self.save_button = tk.Button(
            self, text="Save Image", command=self.save_image)
        self.save_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Make the canvas expand with the window resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def save_image(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if save_path:
            try:
                # Save the scaled image to the desired location
                self.scaled_img.save(save_path)
                print(f"Image saved to {save_path}")
            except Exception as e:
                print(f"Error saving image: {e}")

    def on_resize(self, event):
        # Update the canvas scroll region when the window is resized (not needed for dynamic width but can be left for flexibility)
        self.canvas.config(scrollregion=(
            0, 0, self.img_width, self.scaled_img.height))
