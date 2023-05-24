import numpy as np
import os
from PIL import Image

out_dir = ""
for image in os.listdir(out_dir)[0:5]:
    im = Image.open(f"{out_dir}/"+image)
    imarray = np.array(im)
    print(imarray.shape)
    im = im.convert('RGB')
    im.show()