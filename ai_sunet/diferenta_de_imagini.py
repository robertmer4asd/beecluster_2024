'''import os
import cv2

def compare_images(reference_image_path, folder_path):
    # Load the reference image
    reference_image = cv2.imread(reference_image_path)
    reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

    # Initialize variables to store sum of differences and count of images
    sum_of_differences = 0
    num_images = 0

    # Iterate through each image in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.jpg') or filename.endswith('.png'):  # Adjust file extensions as needed
            # Load the current image from the folder
            current_image_path = os.path.join(folder_path, filename)
            current_image = cv2.imread(current_image_path)
            current_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)

            # Compute the absolute difference between the reference image and current image
            diff = cv2.absdiff(reference_image, current_image)

            # Sum up the pixel-wise differences
            sum_of_differences += diff.sum()

            # Increment the count of images
            num_images += 1

    # Compute the average1 difference per image
    average_difference = sum_of_differences / num_images if num_images > 0 else 0

    return average_difference, num_images

# Example usage:
reference_image_path = 'toot.png'
folder_path = 'spectrograms/roire'
total_sum_of_differences, num_images_compared = compare_images(reference_image_path, folder_path)
average = total_sum_of_differences / num_images_compared
print(average)'''
import cv2
import numpy as np

# load the input images
img1 = cv2.imread('toot.png')
img2 = cv2.imread('spectrograms/roire/segment_1.png')

# convert the images to grayscale
img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# define the function to compute MSE between two images
def mse(img1, img2):
   h, w = img1.shape
   diff = cv2.subtract(img1, img2)
   err = np.sum(diff**2)
   mse = err/(float(h*w))
   return mse, diff

error, diff = mse(img1, img2)
print("Image matching Error between the two images:",error)

cv2.imshow("difference", diff)
cv2.waitKey(0)
cv2.destroyAllWindows()