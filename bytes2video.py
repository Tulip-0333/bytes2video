import os
import binascii
from PIL import Image
import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import glob
import gc

def process_binary_file(file_path):
    # Read the binary file
    with open(file_path, 'rb') as file:
        binary_data = file.read()

    # Convert to hexadecimal
    hex_data = binascii.hexlify(binary_data).decode('utf-8')

    return hex_data

def hex_to_color(hex_string):
    # Ensure the hex string length is a multiple of 6 by padding with zeros if necessary
    if (len(hex_string) % 6) != 0:
        hex_string += '0' * (6 - len(hex_string) % 6)
    # Convert every 6 characters (3 bytes) to a color code
    return [f'#{hex_string[i:i+6]}' for i in range(0, len(hex_string), 6)]

def create_image_from_colors(colors, size=(32, 32)):
    # Create an image from a list of colors
    img = Image.new('RGB', size)
    pixels = img.load()

    for y in range(size[1]):
        for x in range(size[0]):
            idx = y * size[0] + x
            if idx < len(colors):
                pixels[x, y] = tuple(int(colors[idx][i:i+2], 16) for i in (1, 3, 5))
            else:
                pixels[x, y] = (0, 0, 0)  # Black if no more colors

    return img

def upscale_image(image, new_size=(160, 160)):
    return image.resize(new_size, Image.NEAREST)

def create_video_from_images(images, output_path, fps=1):
    # Convert PIL images to numpy arrays
    frames = [np.array(img) for img in images]

    # Create a video from the frames
    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile(output_path, codec='libx264')

def process_files(file_paths, output_video_path, frame_size=(80, 80), upscale_size=(160, 160), fps=30, batch_size=10):
    all_images = []
    
    for i, file_path in enumerate(file_paths):
        # Step 1: Process the binary file to get hex data
        hex_data = process_binary_file(file_path)

        # Step 2: Convert hex data to color codes
        colors = hex_to_color(hex_data)

        # Step 3: Create images
        total_pixels = frame_size[0] * frame_size[1]
        for j in range(0, len(colors), total_pixels):
            frame_colors = colors[j:j+total_pixels]
            img = create_image_from_colors(frame_colors, frame_size)
            upscaled_img = upscale_image(img, upscale_size)
            all_images.append(upscaled_img)
        
        # Step 4: Batch processing and memory management
        if (i + 1) % batch_size == 0 or i == len(file_paths) - 1:
            create_video_from_images(all_images, f"{output_video_path.rsplit('.', 1)[0]}_part{i//batch_size + 1}.mp4", fps)
            all_images.clear()
            gc.collect()  # Force garbage collection to free memory

def main():
    wildcard_path = input('Enter file pattern (e.g., *.bin): ')
    output_video_path = input('Enter output video file name (e.g., output.mp4): ')
    
    # Use glob to find all files matching the pattern
    file_paths = glob.glob(wildcard_path)

    if not file_paths:
        print("No files found matching the pattern.")
        return
    
    print(f'Found {len(file_paths)} files. Creating video...')
    process_files(file_paths, output_video_path)

if __name__ == '__main__':
    main()
