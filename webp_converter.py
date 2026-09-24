import os
from PIL import Image
import pillow_heif


# Directory containing the images
input_directory = input("Enter the path to the directory containing images: ")
pillow_heif.register_heif_opener()

# Check if the directory exists
if not os.path.exists(input_directory):
    print("Directory not found.")
else:
    # Output directory for converted images
    output_directory = os.path.join(input_directory, "webp_images")

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # List of supported image file extensions
    supported_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".heic")

    for root, _, files in os.walk(input_directory):
        for filename in files:
            # Get the file extension
            file_extension = os.path.splitext(filename)[1].lower()

            # Check if the file is an image with a supported extension
            if file_extension in supported_extensions:
                file_path = os.path.join(root, filename)
                img = Image.open(file_path)
                img = img.convert("RGB")

                # Ensure the output directory structure is preserved
                relative_path = os.path.relpath(file_path, input_directory)
                output_path = os.path.join(output_directory, relative_path)

                # Create the output directory structure if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Save the image in WebP format with the ".webp" extension
                output_path_with_extension = os.path.splitext(output_path)[0] + ".webp"
                img.save(output_path_with_extension, "webp")

                print(f"Converted: {file_path} -> {output_path_with_extension}")

    print("Conversion complete.")