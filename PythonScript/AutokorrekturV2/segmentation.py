from ultralytics import YOLO
import torch
from imageFunctions import expandBlackMask
import cv2
import numpy as np


def createCarMask(inputImage, expansionPixels=0):
    # Load a pretrained YOLOv8n model
    model = YOLO('yolov8n-seg.pt')
    results = model(inputImage)

    for r in results:
        try:
            masks = r.masks.data
            boxes = r.boxes.data #eigentlich ungefährlich

        except AttributeError as e:
            print("An AttributeError occurred:", e)
            return #sollte mehr als das sein

        # extract classes
        clss = boxes[:, 5]
        # get indices of results where class is 2 (car in COCO)
        car_indices = torch.where(clss == 2)
        car_masks = masks[car_indices]
        # scale for visualizing results
        car_mask = torch.any(car_masks, dim=0).int() * 255
        inverted_car_mask = 255 - car_mask
        cv2.imwrite('images/temp/mask.jpg', inverted_car_mask.cpu().numpy())
        expandBlackMask(expansionPixels=expansionPixels)


def anyCarsLeft():
    image = f'images/outputImages/result.png'
    model = YOLO('yolov8n-seg.pt')
    results = model(image)

    for r in results:
        boxes = r.boxes.data
        clss = boxes[:, 5]
        car_indices = torch.where(clss == 2)
        if len(car_indices[0]) > 0:
            return True
        return False
