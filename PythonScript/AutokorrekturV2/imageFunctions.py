import os
import shutil
import time
from PIL import Image

import cv2
import numpy as np
from PIL import Image, ImageOps


def fixOrientation(inputImage):
    try:
        image = Image.open(inputImage)
        image = ImageOps.exif_transpose(image)
        image.save(inputImage)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def resizeImage(imageSize, inputImage):
    original_image = Image.open(inputImage)
    # Resize the image
    resized_image = original_image.resize(imageSize, Image.LANCZOS)
    resized_image.save('images/temp/resizedImage.jpg')

def findExtremeBlackPixels(image_path):
    # Open the image using Pillow
    image = Image.open(image_path)

    # Convert the image to grayscale for easy pixel manipulation
    image = image.convert('L')

    # Get the image dimensions
    width, height = image.size

    leftmost = width
    rightmost = 0
    topmost = height
    bottommost = 0

    # Iterate through each pixel to find the extreme black pixels
    for x in range(width):
        for y in range(height):
            pixel_value = image.getpixel((x, y))
            if pixel_value == 0:  # Check if the pixel is black
                if x < leftmost:
                    leftmost = x
                if x > rightmost:
                    rightmost = x
                if y < topmost:
                    topmost = y
                if y > bottommost:
                    bottommost = y

    return (leftmost, rightmost, topmost, bottommost)



def getPieceOfImage(inputMask='images/temp/mask.jpg'):
    (leftmost, rightmost, topmost, bottommost) =findExtremeBlackPixels(inputMask)

    image = Image.open(inputMask)
    width, height = image.size
    squareLength = min(width, height)

    widthCars = abs(rightmost - leftmost)
    heightCars = abs(topmost - bottommost)
    print(squareLength/64, widthCars, heightCars)




def expandBlackMask(expansionPixels, maskPath='images/temp/mask.jpg', outputMaskPath='images/temp/mask.jpg'):
    # Load the mask image
    mask_image = cv2.imread(maskPath, cv2.IMREAD_GRAYSCALE)

    # Create a kernel for dilation
    kernel = np.ones((expansionPixels, expansionPixels), np.uint8)

    # Create an inverted mask (black area becomes white, and vice versa)
    inverted_mask = cv2.bitwise_not(mask_image)

    # Dilate the inverted mask to expand the black area
    expanded_black_area = cv2.dilate(inverted_mask, kernel, iterations=1)

    # Invert the expanded black area mask to get the expanded black area
    expanded_black_area = cv2.bitwise_not(expanded_black_area)

    # Save the expanded black area mask as an image
    cv2.imwrite(outputMaskPath, expanded_black_area)

    print(f"Expanded black mask saved as {outputMaskPath}")


def applyMaskToImage(inputImage='images/temp/resizedImage.jpg', inputMaks='images/temp/mask.jpg'):
    convertJpgToPng(inputImage, 'images/temp/convertedImage.png')
    convertJpgToPng(inputMaks, 'images/temp/convertedMask.png')

    makeTransparent('images/temp/convertedImage.png', 'images/temp/convertedMask.png', 'images/temp/transparent.png')


def convertJpgToPng(input_path, output_path):
    try:
        # Open the JPG image
        img = Image.open(input_path)

        # Save it as a PNG
        img.save(output_path, "PNG")
        print(f"Image converted and saved as {output_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def makeTransparent(image_path, mask_path, output_path):
    # Open the image and the mask
    image = Image.open(image_path)
    mask = Image.open(mask_path)

    # Ensure both images have the same size
    if image.size != mask.size:
        raise ValueError("Image and mask must have the same dimensions")

    # Convert the mask to grayscale
    mask = mask.convert('L')

    # Create a transparent version of the image
    transparent_image = Image.new('RGBA', image.size)
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.getpixel((x, y))
            alpha = mask.getpixel((x, y))
            r, g, b = pixel[0], pixel[1], pixel[2]
            transparent_pixel = (r, g, b, alpha)
            transparent_image.putpixel((x, y), transparent_pixel)

    transparent_image.save(output_path)
    print(f"Image with applied Mask saved as {output_path}")

def copyAndRenameImage(source_path='images/outputImages/result.png', destination_dir='images/samples'):
    if not os.path.exists(source_path):
        return "Source image not found."

    timestamp = int(time.time())
    new_filename = f'{timestamp}.png'
    destination_path = os.path.join(destination_dir, new_filename)
    print(source_path, destination_path)
    shutil.copy(source_path, destination_path)

    return f'Image copied to {destination_path}'
