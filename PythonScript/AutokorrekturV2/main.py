from imageFunctions import resizeImage, applyMaskToImage, fixOrientation, copyAndRenameImage, getPieceOfImage
from invokeAICommunication import uploadImage, createSession, invokeSession, downloadResult
from segmentation import anyCarsLeft, createCarMask

def main(inputImage, sample=False):
    fixOrientation(inputImage=inputImage)

    #resizeImage(imageSize=(768, 768), inputImage=inputImage)
    createCarMask(inputImage=inputImage, expansionPixels=10)  # was, wenn keine Autos auf dem Bild sind
    #applyMaskToImage()

    getPieceOfImage()
    #applyMaskToPiece()


    imageId = uploadImage(image='images/temp/transparent.png', name='Image')
    maskId = uploadImage(image='images/temp/convertedMask.png', name='Mask')

    sessionId = createSession(imageId=imageId, maskId=maskId)
    invokeSession(sessionId=sessionId)

    downloadResult(numberOfLatents2ImageNodes=2)
    print("Any cars left?", anyCarsLeft())

    if sample:
        print(copyAndRenameImage())


