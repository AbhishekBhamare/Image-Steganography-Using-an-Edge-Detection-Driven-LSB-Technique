from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
from text_steganography import EdgeDetectStego


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


class TextSteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Steganography")
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

        Label(frame, text="Encode Message into Image", font=("Helvetica", 24, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=20)

        self.encode_file_label = Label(frame, text="No file selected", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 14))
        self.encode_file_label.pack(pady=10)

        RoundedButton(frame, text="Select Image", command=self.select_encode_file).pack(pady=10)

        Label(frame, text="Enter Message:", font=("Helvetica", 14), bg="#34495e", fg="#ecf0f1").pack(pady=10)
        self.encode_message_entry = Entry(frame, width=60, font=("Helvetica", 14))
        self.encode_message_entry.pack(pady=10)

        self.encode_status_label = Label(frame, text="", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 14))
        self.encode_status_label.pack(pady=10)

        RoundedButton(frame, text="ENCODE", command=self.start_encoding, bg="#2ecc71").pack(pady=20)

    def create_decode_tab(self):
        frame = Frame(self.decode_tab, bg="#34495e")
        frame.pack(expand=True)

        Label(frame, text="Decode Message from Image", font=("Helvetica", 24, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=20)

        self.decode_file_label = Label(frame, text="No file selected", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 14))
        self.decode_file_label.pack(pady=10)

        RoundedButton(frame, text="Select Image", command=self.select_decode_file, bg="#e74c3c").pack(pady=10)

        Label(frame, text="Expected Message Length:", font=("Helvetica", 14), bg="#34495e", fg="#ecf0f1").pack(pady=10)
        self.decode_length_entry = Entry(frame, width=10, font=("Helvetica", 14))
        self.decode_length_entry.pack(pady=10)

        self.decode_status_label = Label(frame, text="", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 14))
        self.decode_status_label.pack(pady=10)

        RoundedButton(frame, text="DECODE", command=self.start_decoding, bg="#2ecc71").pack(pady=10)

    def select_encode_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.encode_file_path = file_path
            self.encode_file_label.config(text=f"Selected: {os.path.basename(file_path)}")
        else:
            self.encode_file_label.config(text="No file selected")

    def select_decode_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.decode_file_path = file_path
            self.decode_file_label.config(text=f"Selected: {os.path.basename(file_path)}")
        else:
            self.decode_file_label.config(text="No file selected")

    def start_encoding(self):
        if not hasattr(self, 'encode_file_path'):
            messagebox.showerror("Error", "No image file selected for encoding!")
            return

        message = self.encode_message_entry.get().strip()
        if not message:
            messagebox.showerror("Error", "Message cannot be empty!")
            return

        self.encode_status_label.config(text="Encoding in progress...")
        threading.Thread(target=self.encode_message, args=(self.encode_file_path, message)).start()

    def encode_message(self, file_path, message):
        try:
            save_folder = "assets"
            os.makedirs(save_folder, exist_ok=True)
            save_path = os.path.join(save_folder, "encrypted_image.png")

            encrypted_image =   self.stego.embed_message(file_path, message)
            encrypted_image.save(save_path)

            self.encode_status_label.config(text=f"Encoding successful! Saved to: {save_path}")
        except Exception as e:
            self.encode_status_label.config(text=f"Error: {e}")

    def start_decoding(self):
        if not hasattr(self, 'decode_file_path'):
            messagebox.showerror("Error", "No image file selected for decoding!")
            return

        length = self.decode_length_entry.get().strip()
        if not length.isdigit():
            messagebox.showerror("Error", "Invalid message length!")
            return

        self.decode_status_label.config(text="Decoding in progress...")
        threading.Thread(target=self.decode_message, args=(self.decode_file_path, int(length))).start()

    def decode_message(self, file_path, length):
        try:
            message = self.stego.extract_message(file_path, length)
            self.decode_status_label.config(text=f"Decoded Message: {message}")
        except Exception as e:
            self.decode_status_label.config(text=f"Error: {e}")


if __name__ == "__main__":
    root = Tk()
    app = TextSteganographyGUI(root)
    root.mainloop()
