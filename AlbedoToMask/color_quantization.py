import cv2
import numpy as np
import argparse

def quantize_colors(image_path, k=8, output_path=None):

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
    # Convert back to uint8
    centers = np.uint8(centers)


    # Map each pixel to its corresponding center
    quantized_flat = centers[labels.flatten()]
    # Reshape back to the original image shape
    quantized = quantized_flat.reshape(image_rgb.shape)
    # Convert back to BGR for OpenCV
    clustered_preview = cv2.cvtColor(quantized, cv2.COLOR_RGB2BGR)
    
    original_centers = centers #save the original copy

    print(f"Image resolution: {image.shape[1]} x {image.shape[0]}")
    print(f"Clustered values: \n {centers}")
    print(len(labels))
    show_image(original_centers, labels, image_rgb, "clustered", False)

    # First, set centers to all [0,0,0]
    for i, center in enumerate(centers):
        centers[i] = [0, 0, 0]

    # Then, iterate through k, store every 3 in a mask
    i = 0
    j = i

    while i < k:
        if j == 0: 
            centers[i] = [255, 0, 0]
        elif j == 1:
            centers[i] = [0, 255, 0]
        elif j == 2:
            centers[i] = [0, 0, 255]

        i += 1
        j = i % 3

        if j == 0: # time to save a mask
            show_image(centers, labels, image_rgb, f"Mask_{int(i/3 - 1)}", True)
            
            # Reset centers to [0,0,0]
            for index, center in enumerate(centers):
                centers[index] = [0, 0, 0]

    
    # Wait for a key press and then close
    cv2.waitKey(0)
    cv2.destroyAllWindows()



    
    
    return quantized

def show_image(centers, labels, image_rgb, image_name, bSave = False, output_path = "./Output/image.png"):
    # Map each pixel to its corresponding center
    mask_flat = centers[labels.flatten()]
    # Reshape back to the original image shape
    mask = mask_flat.reshape(image_rgb.shape)
    # Convert back to BGR for OpenCV
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_RGB2BGR)

    # Preview RGB Channel Mask
    scaled_img = cv2.resize(mask_bgr, (720, 720))
    cv2.imshow(f"{image_name}", scaled_img)

    if bSave:
        output_path = f"{image_path.rsplit('.', 1)[0]}_quantized_{k}_colors.png"
        cv2.imwrite(output_path, quantized_bgr)
        print(f"Quantized image saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Color quantization using K-means clustering")
    parser.add_argument("image_path", type=str, help="Path to the input PNG image")
    parser.add_argument("-k", "--colors", type=int, default=8, help="Number of colors to quantize to (default: 8)")
    parser.add_argument("-o", "--output", type=str, help="Path to save the output image")
    
    args = parser.parse_args()
    
    quantize_colors(args.image_path, args.colors, args.output)

if __name__ == "__main__":
    main()