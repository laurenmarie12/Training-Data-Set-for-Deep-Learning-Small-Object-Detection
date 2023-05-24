import os
from PIL import Image
import json
import matplotlib.pyplot as plt

with open('Annotations/iSAID_train.json') as f:
    train = json.load(f)
annotations = train['annotations']

def show_annotation(image_id):
    for ann in annotations:
        if ann['image_id'] == image_id:
            seg = ann['segmentation']
            box = ann['bbox']
            name = ann['category_name']
            print(f"Cropping bbox {box} out of image {image_id}")
            img = Image.open(f'instance_masks/images/P{str(image_id).zfill(4)}_instance_id_RGB.png')
            left = box[0]
            top = box[1]
            right = box[0]+box[2]
            bottom = box[1]+box[3]
            cropped = img.crop((left, top, right, bottom))
            plt.imshow(cropped)
            plt.title(f"A {name} in image {image_id}")
            plt.show()
            return
    print(f"No annotation found for image {image_id}")
  
# Ask the user for an image ID and display the corresponding annotation
while True:
    image_id_str = input("Enter an image ID (or 'q' to quit): ")
    if image_id_str == 'q':
        break
    try:
        image_id = int(image_id_str)
        show_annotation(image_id)
    except ValueError:
        print("Invalid input. Please enter a number or 'q' to quit.")