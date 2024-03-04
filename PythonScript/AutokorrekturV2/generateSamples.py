import os

from main import main

input_images_dir = 'images/inputImages'
image_files = [f for f in os.listdir(input_images_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]

numberPerImage = 1

for image_file in image_files:
    inputImage = os.path.join(input_images_dir, image_file)
    for i in range(numberPerImage):
        main(inputImage=inputImage, sample=True)
