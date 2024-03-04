from imageFunctions import resizeMaskLikeImage, applyMaskToImage, fixOrientation, copyAndRenameImage, getPieceOfImage, \
    cutPieceFromImage, insertImagePiece, compressImage, decompressImage, convert_to_jpg
from invokeAICommunication import uploadImage, createSession, invokeSession, downloadResult
from segmentation import anyCarsLeft, createCarMask

def main(inputImage, sample=False):
    anyCarsLeftCounter = 0
    while True:
        fixOrientation(inputImage=inputImage)
        createCarMask(inputImage=inputImage, expansionPixels=25)
        resizeMaskLikeImage(inputImage=inputImage)
        start_x, start_y, width, height = getPieceOfImage(inputImage=inputImage, paddingSize=10)
        cutPieceFromImage(start_x, start_y, width, height, inputImage=inputImage, output_path='images/temp/imagePiece.jpg')
        cutPieceFromImage(start_x, start_y, width, height, inputImage='images/temp/mask.jpg', output_path='images/temp/maskPiece.jpg')
        compressImage(inputImage='images/temp/imagePiece.jpg')
        compressImage(inputImage='images/temp/maskPiece.jpg')
        applyMaskToImage(inputImage='images/temp/imagePiece.jpg')


        imageId = uploadImage(image='images/temp/transparent.png', name='Image')
        maskId = uploadImage(image='images/temp/convertedMask.png', name='Mask')
        sessionId = createSession(imageId=imageId, maskId=maskId)
        invokeSession(sessionId=sessionId)
        downloadResult(numberOfLatents2ImageNodes=2)

        decompressImage(width, height, imagePiece='images/outputImages/resultPiece.png')
        insertImagePiece(inputImage=inputImage, start_x=start_x, start_y=start_y)

        if sample:
            copyAndRenameImage()

        if not anyCarsLeft(inputImage='images/outputImages/result.png'):
            convert_to_jpg(input_path='images/outputImages/result.png', output_path='images/outputImages/result.jpg')
            break

        anyCarsLeftCounter += 1
        if anyCarsLeftCounter > 1:
            convert_to_jpg(input_path='images/outputImages/result.png', output_path='images/outputImages/result.jpg')
            break

