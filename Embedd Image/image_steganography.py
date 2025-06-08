from PIL import Image, ImageFile
import numpy as np
import matplotlib.pyplot as plt

# Allow loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

DEFAULT_THRESHOLD = 128  # Threshold for edge detection
NUM_BITS_EDGE = 4  # Number of bits for edge blocks
NUM_BITS_NON_EDGE = 1  # Number of bits for non-edge blocks
BLOCK_WIDTH = 3  # Width of the block
BLOCK_HEIGHT = 3  # Height of the block

class EdgeDetectStego:
    def __init__(self, threshold=DEFAULT_THRESHOLD, edge_bits=NUM_BITS_EDGE, non_edge_bits=NUM_BITS_NON_EDGE, block_width=BLOCK_WIDTH, block_height=BLOCK_HEIGHT):
        self.threshold = threshold
        self.edge_bits = edge_bits
        self.non_edge_bits = non_edge_bits
        self.block_width = block_width
        self.block_height = block_height

    def embed_image(self, image_path, hidden_image_path):
        """
        Embed a hidden image into the cover image using edge detection and block-based embedding.
        """
        img = Image.open(image_path).convert("RGB")
        hidden_img = Image.open(hidden_image_path).convert("RGB")

        pixels = np.array(img)
        hidden_pixels = np.array(hidden_img)

        width, height = img.size
        hidden_width, hidden_height = hidden_img.size
        bit_index = 0
        hidden_bits = ''.join(f'{pixel:08b}' for pixel in hidden_pixels.flatten())

        for y in range(0, height, self.block_height):
            for x in range(0, width, self.block_width):
                if bit_index >= len(hidden_bits):
                    break

                num_bits = self.edge_bits if self.is_edge_block(pixels, x, y) else self.non_edge_bits

                for dy in range(self.block_height):
                    for dx in range(self.block_width):
                        if (x + dx < width) and (y + dy < height) and (bit_index < len(hidden_bits)):
                            for channel in range(3):  # Process R, G, and B channels separately
                                self.embed_bits(pixels, x + dx, y + dy, hidden_bits[bit_index:bit_index + num_bits], channel)
                                bit_index += num_bits

        encrypted_image = Image.fromarray(pixels)
        return encrypted_image

    def extract_image(self, encrypted_image_path, hidden_image_size):
        """
        Extract the hidden image from the encrypted image.
        """
        img = Image.open(encrypted_image_path).convert("RGB")
        pixels = np.array(img)

        width, height = img.size
        hidden_width, hidden_height = hidden_image_size
        hidden_bits = ""
        bit_index = 0
        total_bits = hidden_width * hidden_height * 8 * 3  # Each pixel has 3 channels (R, G, B)

        for y in range(0, height, self.block_height):
            for x in range(0, width, self.block_width):
                if bit_index >= total_bits:
                    break

                num_bits = self.edge_bits if self.is_edge_block(pixels, x, y) else self.non_edge_bits

                for dy in range(self.block_height):
                    for dx in range(self.block_width):
                        if (x + dx < width) and (y + dy < height) and (bit_index < total_bits):
                            for channel in range(3):  # Process R, G, and B channels separately
                                bits = self.extract_bits(pixels, x + dx, y + dy, num_bits, channel)
                                hidden_bits += bits
                                bit_index += num_bits

        hidden_pixel_values = [int(hidden_bits[i:i+8], 2) for i in range(0, total_bits, 8)]
        hidden_image = np.array(hidden_pixel_values, dtype=np.uint8).reshape((hidden_height, hidden_width, 3))
        return Image.fromarray(hidden_image, "RGB")

    def is_edge_block(self, pixels, x, y):
        """
        Perform edge detection on the block of pixels.
        """
        if x + self.block_width >= pixels.shape[1] or y + self.block_height >= pixels.shape[0]:
            return False

        # Calculate gradients for edge detection within the valid block area
        gx = pixels[y:y + self.block_height, x + 1:x + self.block_width + 1, 0] - pixels[y:y + self.block_height, x:x + self.block_width, 0]
        gy = pixels[y + 1:y + self.block_height + 1, x:x + self.block_width, 0] - pixels[y:y + self.block_height, x:x + self.block_width, 0]
        gradient_magnitude = np.sqrt(gx**2 + gy**2)

        return np.any(gradient_magnitude > self.threshold)

    def embed_bits(self, pixels, x, y, bits, channel):
        """
        Embed bits into the pixel value.
        """
        current_value = pixels[y, x, channel]
        bits_value = int(bits, 2)
        mask = (1 << len(bits)) - 1
        new_value = (current_value & ~mask) | bits_value
        pixels[y, x, channel] = new_value

    def extract_bits(self, pixels, x, y, num_bits, channel):
        """
        Extract bits from the pixel value.
        """
        value = pixels[y, x, channel] & ((1 << num_bits) - 1)
        return f"{value:0{num_bits}b}"

def plot_histograms(original_image_path, encrypted_image_path):
    """
    Plot histograms for the original and encrypted images in grayscale.
    """
    # Load the original and encrypted images and convert them to grayscale
    original_image = Image.open(original_image_path).convert("L")
    encrypted_image = Image.open(encrypted_image_path).convert("L")

    # Convert images to numpy arrays
    original_pixels = np.array(original_image).flatten()
    encrypted_pixels = np.array(encrypted_image).flatten()

    # Plot histograms
    plt.figure(figsize=(12, 6))

    # Histogram of the original image
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
    image_path = '/content/new-large.png'  # Path to your large image file
    hidden_image_path = '/content/new-small.png'  # Path to your small image file

    stego = EdgeDetectStego()

    # Embed the hidden image into the cover image
    print("Embedding hidden image...")
    encrypted_image = stego.embed_image(image_path, hidden_image_path)
    encrypted_image.save('encrypted_image.png')
    print("Hidden image embedded and saved as 'encrypted_image.png'")

    # Extract the hidden image from the encrypted image
    print("Extracting hidden image...")
    extracted_image = stego.extract_image('encrypted_image.png', Image.open(hidden_image_path).size)
    extracted_image.save('extracted_image.png')
    print("Hidden image extracted and saved as 'extracted_image.png'")

    # Plot histograms of the original and encrypted images
    plot_histograms(image_path, 'encrypted_image.png')

if __name__ == "__main__":
    main()
