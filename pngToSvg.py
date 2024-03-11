import os
import subprocess

def png_to_svg(input_file, output_file):
    """
    Convert PNG to SVG using potrace library.
    
    Args:
        input_file (str): Path to the input PNG file.
        output_file (str): Path to save the output SVG file.
    """
    # Check if input file exists
    if not os.path.exists(input_file):
        print("Input file not found!")
        return
    
    # Use potrace to convert PNG to SVG
    try:
        subprocess.run([input_file, '-s', '-o', output_file], check=True)
        print("Conversion successful!")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e}")

# Example usage
input_png = "./input.png"
output_svg = "output.svg"
png_to_svg(input_png, output_svg)
