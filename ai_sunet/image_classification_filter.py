import os
import cv2

def compare_images(reference_image_path, folder_path):
    reference_image = cv2.imread(reference_image_path)
    reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

    sum_of_differences = 0
    num_images = 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            current_image_path = os.path.join(folder_path, filename)
            current_image = cv2.imread(current_image_path)
            current_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)

            diff = cv2.absdiff(reference_image, current_image)
            sum_of_differences += diff.sum()
            num_images += 1

    average_difference = sum_of_differences / num_images if num_images > 0 else 0

    return average_difference
reference_image_path = 'normal.png'
folder_path1 = 'spectrograms/roire'
folder_path2 = 'spectrograms/normal'
folder_path3 = 'spectrograms/angry'
diff1 = compare_images(reference_image_path, folder_path1)
diff2 = compare_images(reference_image_path, folder_path2)
diff3 = compare_images(reference_image_path, folder_path3)
print(f"First comparation: {diff1}\nSecond comparation: {diff2}\nThird comparation: {diff3}")
if diff1 < diff2 and diff1 < diff3:
    print("roire")
    case = "roire"
elif diff2 < diff1 and diff2 < diff3:
    print("normal")
    case = "normal"
elif diff3 < diff1 and diff3 < diff2:
    print("angry")
    case = "angry"