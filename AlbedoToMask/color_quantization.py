import cv2
import numpy as np
import argparse

def quantize_colors(image_path, k=8, output_path=None):
    """
    Perform color quantization on an image using K-means clustering.
    
    Args:
        image_path (str): Path to the input PNG image
        k (int): Number of colors to quantize to
        output_path (str, optional): Path to save the output image. If None, a default path is used.
    
    Returns:
        numpy.ndarray: The quantized image
    """
    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    # Convert to RGB (OpenCV uses BGR by default)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Reshape the image to a 2D array of pixels
    pixels = image_rgb.reshape(-1, 3).astype(np.float32)
    
    # Define criteria for K-means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    
    # Apply K-means clustering
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    print(centers)
    print(len(labels))

    # Convert back to uint8
    centers = np.uint8(centers)
    
    # Map each pixel to its corresponding center
    quantized_flat = centers[labels.flatten()]
    
    # Reshape back to the original image shape
    quantized = quantized_flat.reshape(image_rgb.shape)
    
    # Convert back to BGR for OpenCV
    quantized_bgr = cv2.cvtColor(quantized, cv2.COLOR_RGB2BGR)
    
    # Save the result if an output path is provided
    if output_path is None:
        output_path = f"{image_path.rsplit('.', 1)[0]}_quantized_{k}_colors.png"
    
    cv2.imwrite(output_path, quantized_bgr)
    print(f"Quantized image saved to {output_path}")
    
    return quantized

def main():
    parser = argparse.ArgumentParser(description="Color quantization using K-means clustering")
    parser.add_argument("image_path", type=str, help="Path to the input PNG image")
    parser.add_argument("-k", "--colors", type=int, default=8, help="Number of colors to quantize to (default: 8)")
    parser.add_argument("-o", "--output", type=str, help="Path to save the output image")
    
    args = parser.parse_args()
    
    quantize_colors(args.image_path, args.colors, args.output)

if __name__ == "__main__":
    main()