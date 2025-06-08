from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

DEFAULT_THRESHOLD = 128  # Threshold for edge detection
NUM_BITS = 8  # Bit depth for each pixel channel

class EdgeDetectStego:
    def __init__(self, threshold=DEFAULT_THRESHOLD, edge_bits=4, non_edge_bits=1, block_width=3, block_height=3):
        self.threshold = threshold
        self.edge_bits = edge_bits
        self.non_edge_bits = non_edge_bits
        self.block_width = block_width
        self.block_height = block_height

    def embed_message(self, image_path, message):
        """
        Embeds a message into an RGB image based on edge detection.

        :param image_path: Path to the input image
        :param message: String message to embed
        :return: PIL Image object with embedded message
        """
        # Convert the message to a bit string
        message_bits = ''.join(f'{ord(c):08b}' for c in message)
        img = Image.open(image_path).convert("RGB")  # Load and convert to RGB
        pixels = np.array(img)

        width, height = img.size
        bit_index = 0

        for y in range(0, height, self.block_height):
            for x in range(0, width, self.block_width):
                num_bits = self.edge_bits if self.is_edge_block(pixels, x, y) else self.non_edge_bits

                for dy in range(self.block_height):
                    for dx in range(self.block_width):
                        # Ensure that we do not go out of bounds
                        if (x + dx < width) and (y + dy < height):
                            if bit_index < len(message_bits) and num_bits > 0:  # Only embed bits if there are bits to embed
                                for channel in range(3):  # Loop over R, G, B channels
                                    if bit_index < len(message_bits):
                                        self.embed_bits(pixels, x + dx, y + dy, message_bits[bit_index:bit_index + num_bits], channel)
                                        bit_index += num_bits

        encrypted_image = Image.fromarray(pixels)
        return encrypted_image

    def extract_message(self, image_path, message_length):
        """
        Extracts an embedded message from an RGB image.

        :param image_path: Path to the encrypted image
        :param message_length: Expected length of the original message in characters
        :return: Extracted message as a string
        """
        img = Image.open(image_path).convert("RGB")
        pixels = np.array(img)

        width, height = img.size
        message_bits = ""
        bit_index = 0
        total_bits = message_length * 8

        for y in range(0, height, self.block_height):
            for x in range(0, width, self.block_width):
                num_bits = self.edge_bits if self.is_edge_block(pixels, x, y) else self.non_edge_bits

                for dy in range(self.block_height):
                    for dx in range(self.block_width):
                        # Ensure that we do not go out of bounds
                        if (x + dx < width) and (y + dy < height):
                            if bit_index < total_bits:
                                for channel in range(3):  # Loop over R, G, B channels
                                    if bit_index < total_bits:
                                        bits = self.extract_bits(pixels, x + dx, y + dy, num_bits, channel)
                                        message_bits += bits
                                        bit_index += num_bits

        message = ''.join(chr(int(message_bits[i:i+8], 2)) for i in range(0, total_bits, 8))
        return message

    def is_edge_block(self, pixels, x, y):
        # Ensure we do not go out of bounds
        if x + self.block_width + 1 > pixels.shape[1] or y + self.block_height + 1 > pixels.shape[0]:
            return False  # Treat blocks at the edges as non-edge blocks

        # Calculate gradient magnitude for edge detection on the R channel
        gx = pixels[y:y + self.block_height, x + 1:x + self.block_width + 1, 0] - pixels[y:y + self.block_height, x:x + self.block_width, 0]
        gy = pixels[y + 1:y + self.block_height + 1, x:x + self.block_width, 0] - pixels[y:y + self.block_height, x:x + self.block_width, 0]
        gradient_magnitude = np.sqrt(gx**2 + gy**2)

        return np.any(gradient_magnitude > self.threshold)

    def embed_bits(self, pixels, x, y, bits, channel):
        current_value = pixels[y, x, channel]
        bits_value = int(bits, 2)
        mask = (1 << len(bits)) - 1
        new_value = (current_value & ~mask) | bits_value
        pixels[y, x, channel] = new_value

    def extract_bits(self, pixels, x, y, num_bits, channel):
        value = pixels[y, x, channel] & ((1 << num_bits) - 1)
        return f"{value:0{num_bits}b}"

def plot_histograms(original_image_path, encrypted_image_path):
    original_image = Image.open(original_image_path).convert("L")
    encrypted_image = Image.open(encrypted_image_path).convert("L")

    original_pixels = np.array(original_image).flatten()
    encrypted_pixels = np.array(encrypted_image).flatten()

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.hist(original_pixels, bins=256, range=(0, 255), color='blue', alpha=0.7)
    plt.title("Histogram of Original Image (Grayscale)")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")

    # Histogram of the encrypted image
    plt.subplot(1, 2, 2)
    plt.hist(encrypted_pixels, bins=256, range=(0, 255), color='blue', alpha=0.7)
    plt.title("Histogram of Encrypted Image (Grayscale)")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")

    plt.tight_layout()
    plt.show()

def main():
    image_path = '/content/new-small.png'  # Path to your input RGB image
    message = '''ome differences may sdlffildsjfd kslsdnfldsnvdklv dsflksdfjkldsjfds sdlkfjsdkfj in the histograms, an effective steganographic technique ensures that these changes remain subtle, preserving the image's appearance while effectively hiding the message.'''

    stego = EdgeDetectStego()

    print("Embedding message...")
    encrypted_image = stego.embed_message(image_path, message)
    encrypted_image_path = 'encrypted_image.png'
    encrypted_image.save(encrypted_image_path)
    print("Message embedded and saved as 'encrypted_image.png'")

    print("Extracting message...")
    extracted_message = stego.extract_message(encrypted_image_path, len(message))
    print("Extracted message:", extracted_message)
    print("\n")
    plot_histograms(image_path, encrypted_image_path)

if __name__ == "__main__":
    main()

