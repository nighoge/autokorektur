import math
import os
import shutil
import time
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
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


def resizeMaskLikeImage(inputImage, inputMask='images/temp/mask.jpg', outputImage='images/temp/mask.jpg'):
    image = Image.open(inputImage)
    mask = Image.open(inputMask)

    imageSize = image.size

    resized_image = mask.resize(imageSize, Image.LANCZOS)
    resized_image.save(outputImage)

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
            if pixel_value == 0:
                if x < leftmost:
                    leftmost = x
                if x > rightmost:
                    rightmost = x
                if y < topmost:
                    topmost = y
                if y > bottommost:
                    bottommost = y

    return (leftmost, rightmost, topmost, bottommost)


def moveBox(widthCars, heightCars, leftmost, topmost, inputImage):
    image = Image.open(inputImage)
    width, height = image.size
    xDelta = 0
    yDelta = 0
    if leftmost < 0:
        xDelta = leftmost
    if topmost < 0:
        yDelta = topmost

    if leftmost+widthCars > width:
        xDelta = leftmost+widthCars - width
    if topmost+heightCars > height:
        yDelta = topmost+heightCars - height

    return xDelta, yDelta


def addPaddingToImagePieceIfPossible(leftmost, topmost, widthCars, heightCars, paddingSize, inputImage):
    totalPadding = paddingSize*64

    if widthCars > heightCars:
        widthCarsWithPadding = widthCars + totalPadding
        newLeft = leftmost - totalPadding / 2

        resizeRatio = 768 / widthCarsWithPadding
        heightCarsWithPadding = heightCars + totalPadding
        resizedShortestSide = heightCarsWithPadding * resizeRatio
        correction = (resizedShortestSide % 64) / resizeRatio
        heightCarsWithPadding -= correction
        print(heightCarsWithPadding*resizeRatio, "shortest Side")
        newTop = topmost - math.floor(correction/2)

    else:
        heightCarsWithPadding = heightCars + totalPadding
        newTop = topmost - totalPadding / 2

        resizeRatio = 768 / heightCarsWithPadding
        widthCarsWithPadding = heightCars + totalPadding
        resizedShortestSide = widthCarsWithPadding * resizeRatio
        correction = (resizedShortestSide % 64) / resizeRatio
        widthCarsWithPadding -= correction
        print(widthCarsWithPadding*resizeRatio, "shortest Side")
        newLeft = topmost - math.floor(correction*resizeRatio)

    xDelta, yDelta = moveBox(widthCarsWithPadding, heightCarsWithPadding, newLeft, newTop, inputImage)

    newLeft = newLeft - xDelta
    newTop = newTop - yDelta

    xDelta, yDelta = moveBox(widthCarsWithPadding, heightCarsWithPadding, newLeft, newTop, inputImage)

    if(xDelta == 0 and yDelta == 0):
        print("Padding added to ImagePiece")
        drawBoxOnImage(newLeft, newTop, widthCarsWithPadding, heightCarsWithPadding, inputImage, 'images/temp/boxWithPadding.jpg')
        return newLeft, newTop, widthCarsWithPadding, heightCarsWithPadding

    return int(leftmost), int(topmost), int(widthCars), int(heightCars)


def getPieceOfImage(inputImage, paddingSize=0, inputMask='images/temp/mask.jpg'):
    (leftmost, rightmost, topmost, bottommost) =findExtremeBlackPixels(inputMask)

    widthCars = math.ceil(abs(rightmost - leftmost)/64) * 64
    heightCars = math.ceil(abs(topmost - bottommost)/64) * 64

    drawBoxOnImage(leftmost, topmost, widthCars, heightCars, inputImage, 'images/temp/boximage.jpg')

    xDelta, yDelta = moveBox(widthCars, heightCars, leftmost, topmost, inputImage)
    if (xDelta != 0 or yDelta != 0):
        leftmost = leftmost - xDelta
        topmost = topmost - yDelta
        drawBoxOnImage(leftmost, topmost, widthCars, heightCars, inputImage, 'images/temp/boximageMoved.jpg')

    leftmost, topmost, widthCars, heightCars = makeSquareIfPossible(heightCars, inputImage, leftmost, topmost, widthCars)

    leftmost, topmost, widthCars, heightCars = addPaddingToImagePieceIfPossible(leftmost, topmost, widthCars, heightCars, paddingSize, inputImage)


    print("Bounding-box around the cars is drawn")
    #print(f"width>heigth is {widthCars>heightCars} => {heightCars*768/(widthCars*64)} is Integer")
    #print(f"width<heigth is {widthCars<heightCars} => {widthCars*768/(heightCars*64)} is Integer")
    return int(leftmost), int(topmost), int(widthCars), int(heightCars)


def makeSquareIfPossible(heightCars, inputImage, leftmost, topmost, widthCars):
    if widthCars > heightCars:
        xDeltaSquare, yDeltaSquare = moveBox(widthCars, widthCars, leftmost, topmost, inputImage)
        xDeltaSquare2, yDeltaSquare2 = moveBox(widthCars, widthCars, leftmost - xDeltaSquare, topmost - yDeltaSquare,
                                               inputImage)
        if xDeltaSquare2 == yDeltaSquare2 == 0:
            print("Square is possible")
            drawBoxOnImage(leftmost - xDeltaSquare, topmost - yDeltaSquare, widthCars, widthCars, inputImage,
                           'images/temp/squareBoximage.jpg')
            leftmost = leftmost - xDeltaSquare
            topmost = topmost - yDeltaSquare
            heightCars = widthCars
    else:
        xDeltaSquare, yDeltaSquare = moveBox(heightCars, heightCars, leftmost, topmost, inputImage)
        xDeltaSquare2, yDeltaSquare2 = moveBox(heightCars, heightCars, leftmost - xDeltaSquare, topmost - yDeltaSquare,
                                               inputImage)
        if xDeltaSquare2 == yDeltaSquare2 == 0:
            drawBoxOnImage(leftmost - xDeltaSquare, topmost - yDeltaSquare, widthCars, heightCars, inputImage,
                           'images/temp/squareBoximage.jpg')
            leftmost = leftmost - xDeltaSquare
            topmost = topmost - yDeltaSquare
            widthCars = heightCars
    return leftmost, topmost, widthCars, heightCars


def drawBoxOnImage(left, top, width, height, image_path, output_path):
    img = mpimg.imread(image_path)
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    rect = patches.Rectangle((left,top), width, height, linewidth=2, edgecolor='r', facecolor='none')
    ax.add_patch(rect)

    plt.savefig(output_path)



def expandBlackMask(expansionPixels, maskPath='images/temp/mask.jpg', outputMaskPath='images/temp/mask.jpg'):
    mask_image = cv2.imread(maskPath, cv2.IMREAD_GRAYSCALE)
    kernel = np.ones((expansionPixels, expansionPixels), np.uint8)
    inverted_mask = cv2.bitwise_not(mask_image)
    expanded_black_area = cv2.dilate(inverted_mask, kernel, iterations=1)
    expanded_black_area = cv2.bitwise_not(expanded_black_area)
    cv2.imwrite(outputMaskPath, expanded_black_area)

    print(f"Expanded black mask saved as {outputMaskPath}")


def compressImage(inputImage):
    img = Image.open(inputImage)
    longestSide = 768
    if img.width > img.height:
        new_width = longestSide
        shortSide = longestSide * (img.height / img.width)
        new_height = math.ceil(shortSide/8)*8
    else:
        new_height = longestSide
        shortSide = longestSide * (img.width / img.height)
        new_width = math.ceil(shortSide/8)*8

    resized_img = img.resize((new_width, new_height))
    resized_img.save(inputImage)
    print(f"Compression of {inputImage} successful to {new_width}x{new_height}")


def applyMaskToImage(inputImage, inputMaks='images/temp/maskPiece.jpg'):
    convertJpgToPng(inputImage, 'images/temp/convertedImage.png')
    convertJpgToPng(inputMaks, 'images/temp/convertedMask.png')

    makeTransparent(inputImage, 'images/temp/convertedMask.png', 'images/temp/transparent.png')


def convertJpgToPng(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            img.save(output_path, 'PNG')
        print(f"Conversion successful: {input_path} converted to {output_path}")
    except Exception as e:
        print(f"Conversion to png failed: {e}")

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
            if alpha == 0:
                pixel = (255, 255, 255)
            r, g, b = pixel[0], pixel[1], pixel[2]
            transparent_pixel = (r, g, b, alpha)
            transparent_image.putpixel((x, y), transparent_pixel)

    transparent_image.save(output_path)
    print(f"Image with applied Mask saved as {output_path}")

def cutPieceFromImage(start_x, start_y, width, height, inputImage, output_path):
    image = Image.open(inputImage)
    cropped_image = image.crop((start_x, start_y, start_x + width, start_y + height))
    cropped_image.save(output_path)


def decompressImage(width, height, imagePiece='images/outputImages/resultPiece.png'):
    input_image = Image.open(imagePiece)
    resized_image = input_image.resize((width, height))
    resized_image.save('images/outputImages/resultPieceDecompressed.png')

def insertImagePiece(inputImage, start_x, start_y, imagePiece='images/outputImages/resultPieceDecompressed.png'):
    baseImage = Image.open(inputImage)
    imagePiece = Image.open(imagePiece)

    piece_width, piece_height = imagePiece.size
    base_width, base_height = baseImage.size

    if start_x + piece_width > base_width or start_y + piece_height > base_height:
        print("Error: The piece cannot fit within the base image.")
        return

    baseImage.paste(imagePiece, (start_x, start_y))
    baseImage.save('images/outputImages/result.png')
def copyAndRenameImage(source_path='images/outputImages/result.png', destination_dir='images/samples'):
    if not os.path.exists(source_path):
        return "Source image not found."

    timestamp = int(time.time())
    new_filename = f'{timestamp}.png'
    destination_path = os.path.join(destination_dir, new_filename)
    print(source_path, destination_path)
    shutil.copy(source_path, destination_path)

    print(f'Image copied to {destination_path}')

def convert_to_jpg(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            img.convert('RGB').save(output_path, 'JPEG')
            print(f"Conversion successful. Image saved to: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
