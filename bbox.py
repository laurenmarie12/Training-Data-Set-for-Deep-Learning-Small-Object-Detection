import os
from PIL import Image
import json
import matplotlib.pyplot as plt

with open('Annotations/iSAID_train.json') as f:
    train = json.load(f)
annotations = train['annotations']
for ann in annotations:
    image_id = ann['image_id']
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

