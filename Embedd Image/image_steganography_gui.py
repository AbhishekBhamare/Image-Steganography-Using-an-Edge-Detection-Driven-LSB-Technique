from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
from image_steganography import EdgeDetectStego  # Assuming you saved the image steganography code in this file


class RoundedButton(Canvas):
    def __init__(self, parent, text, command, bg="#3498db", fg="#fff", font=("Helvetica", 14), width=200, height=50, padx=20, pady=10):
        super().__init__(parent, width=width + 2 * padx, height=height + 2 * pady, bg=bg, highlightthickness=0)
        self.command = command
        self.bg = bg
        self.fg = fg
        self.font = font

        self.rounded_rectangle(padx, pady, width + padx, height + pady, radius=25, fill=bg)
        self.text_id = self.create_text((width + 2 * padx) / 2, (height + 2 * pady) / 2, text=text, font=font, fill=fg)

        self.bind("<Button-1>", self.on_click)
        self.tag_bind(self.text_id, "<Button-1>", self.on_click)

    def rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_click(self, event=None):
        self.command()


class ImageSteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography")
        self.root.geometry("900x600")
        self.root.configure(bg="#2c3e50")
        self.stego = EdgeDetectStego()

        self.style_tabs()
        self.create_widgets()

    def style_tabs(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("CustomNotebook.TNotebook", background="#2c3e50", tabmargins=[5, 5, 5, 5])
        style.configure(
            "CustomNotebook.TNotebook.Tab",
            font=("Helvetica", 14, "bold"),
            padding=[10, 5],
            foreground="#fff",
            background="#3498db",
        )
        style.map(
            "CustomNotebook.TNotebook.Tab",
            background=[("selected", "#2ecc71")],
            foreground=[("selected", "#fff")],
        )

    def create_widgets(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root, style="CustomNotebook.TNotebook")
        self.notebook.pack(fill=BOTH, expand=True, pady=20)

        # Tabs
        self.encode_tab = Frame(self.notebook, bg="#34495e")
        self.decode_tab = Frame(self.notebook, bg="#34495e")
        self.notebook.add(self.encode_tab, text="Encode")
        self.notebook.add(self.decode_tab, text="Decode")

        # Encode Tab
        self.create_encode_tab()

        # Decode Tab
        self.create_decode_tab()

    def create_encode_tab(self):
        frame = Frame(self.encode_tab, bg="#34495e")
        frame.pack(expand=True)

        Label(frame, text="Encode Image into Another Image", font=("Helvetica", 24, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=20)

        self.encode_cover_label = Label(frame, text="No cover image selected", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 14))
        self.encode_cover_label.pack(pady=10)

        RoundedButton(frame, text="Select Cover Image",width=400, command=self.select_cover_image).pack(pady=10)

        self.encode_hidden_label = Label(frame, text="No hidden image selected", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 14))
        self.encode_hidden_label.pack(pady=10)

        RoundedButton(frame, text="Select Hidden Image",width=400, command=self.select_hidden_image).pack(pady=10)

        self.encode_status_label = Label(frame, text="", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 14))
        self.encode_status_label.pack(pady=10)

        RoundedButton(frame, text="ENCODE", command=self.start_encoding, bg="#2ecc71").pack(pady=20)

    def create_decode_tab(self):
        frame = Frame(self.decode_tab, bg="#34495e")
        frame.pack(expand=True)

        Label(frame, text="Decode Image from Another Image", font=("Helvetica", 24, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=20)

        self.decode_file_label = Label(frame, text="No image selected", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 14))
        self.decode_file_label.pack(pady=10)

        RoundedButton(frame, text="Select Encrypted Image", width=400, command=self.select_decode_file, bg="#e74c3c").pack(pady=10)

        Label(frame, text="Hidden Image Size (Width x Height):", font=("Helvetica", 14), bg="#34495e", fg="#ecf0f1").pack(pady=10)
        self.decode_size_entry = Entry(frame, width=20, font=("Helvetica", 14))
        self.decode_size_entry.pack(pady=10)

        self.decode_status_label = Label(frame, text="", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 14))
        self.decode_status_label.pack(pady=10)

        RoundedButton(frame, text="DECODE", command=self.start_decoding, bg="#2ecc71").pack(pady=10)

    def select_cover_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.cover_image_path = file_path
            self.encode_cover_label.config(text=f"Selected: {os.path.basename(file_path)}")
        else:
            self.encode_cover_label.config(text="No cover image selected")

    def select_hidden_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.hidden_image_path = file_path
            self.encode_hidden_label.config(text=f"Selected: {os.path.basename(file_path)}")
        else:
            self.encode_hidden_label.config(text="No hidden image selected")

    def select_decode_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.encrypted_image_path = file_path
            self.decode_file_label.config(text=f"Selected: {os.path.basename(file_path)}")
        else:
            self.decode_file_label.config(text="No image selected")

    def start_encoding(self):
        if not hasattr(self, 'cover_image_path') or not hasattr(self, 'hidden_image_path'):
            messagebox.showerror("Error", "Cover image or hidden image is not selected!")
            return

        self.encode_status_label.config(text="Encoding in progress...")
        threading.Thread(target=self.encode_image).start()

    def encode_image(self):
        try:
            save_folder = "assets"
            os.makedirs(save_folder, exist_ok=True)
            save_path = os.path.join(save_folder, "encrypted_image.png")

            encrypted_image = self.stego.embed_image(self.cover_image_path, self.hidden_image_path)
            encrypted_image.save(save_path)

            self.encode_status_label.config(text=f"Encoding successful! Saved to: {save_path}")
        except Exception as e:
            self.encode_status_label.config(text=f"Error: {e}")

    def start_decoding(self):
        if not hasattr(self, 'encrypted_image_path'):
            messagebox.showerror("Error", "No image selected for decoding!")
            return

        size = self.decode_size_entry.get().strip()
        try:
            width, height = map(int, size.split('x'))
        except ValueError:
            messagebox.showerror("Error", "Invalid image size! Format: Width x Height")
            return

        self.decode_status_label.config(text="Decoding in progress...")
        threading.Thread(target=self.decode_image, args=((width, height),)).start()

    def decode_image(self, hidden_size):
        try:
            hidden_image = self.stego.extract_image(self.encrypted_image_path, hidden_size)
            save_folder = "assets"
            os.makedirs(save_folder, exist_ok=True)
            save_path = os.path.join(save_folder, "extracted_image.png")
            hidden_image.save(save_path)

            self.decode_status_label.config(text=f"Decoding successful! Saved to: {save_path}")
        except Exception as e:
            self.decode_status_label.config(text=f"Error: {e}")


if __name__ == "__main__":
    root = Tk()
    app = ImageSteganographyGUI(root)
    root.mainloop()
