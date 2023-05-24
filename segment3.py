import os
import rasterio
import geopandas as gpd

# load bounding boxes from geodatabase
boxes = []
file_gdb_path = 'application/water_tank_cooling_tower_samples.gdb'
layers = gpd.read_file(file_gdb_path, driver='OpenFileGDB')
geometries = layers['geometry']
for geometry in geometries:
    boxes.append(geometry.bounds)

# match bounding boxes to photo segments
image_paths = [path for path in os.listdir("application/Orthos") if path[-4:]=='.tif']
print(f"len:{len(image_paths)}")
for i, box in enumerate(boxes[0:15]):
    for path in image_paths:
        if True: # decide if segment is inside this image or not somehow
            with rasterio.open('application/Orthos/'+path) as src:
                transform = src.transform
                xmin, ymin, xmax, ymax = box
                window = rasterio.windows.from_bounds(xmin, ymin, xmax, ymax, transform)

                crop_data = src.read(window=window)

                with rasterio.open('out/'+str(i)+"_out.tif", 'w', **src.profile) as dst:
                    dst.write(crop_data)
    print(i)

from PIL import Image
for image in os.listdir('out'):
    im = Image.open('out/'+image)
    im = im.convert('RGB')
    im.show()