import datetime
import os
import geopandas as gpd
import rasterio
import rasterio.mask
from shapely.geometry import box
import json

out_dir = f"out_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.mkdir(out_dir)

metadata = { # highest level structure of COCO JSON record
    'info': {},
    'licenses': ["??? not yet public, no license"],
    'images': [],
    'categories': [],
    'annotations': []
}

metadata['info'] = {
  "description": "Satellite imagery clipped to center on water tanks, cooling towers, and solar panels.",
  "url": "??? not yet public, no url",
  "version": "1.0",
  "year": 2023,
  "contributor": "Lauren Mangla ",
  "date_created": datetime.datetime.now().strftime("%Y-%m-%d")
}

# load geometries from geodatabase
geom_path = 'watertowers.gdb'
layers = gpd.read_file(geom_path, driver='OpenFileGDB')

# record all categories and subcategories
categories = list(set(layers['FEATURE_CODE']))
subcategories = list(set(layers['SUB_FEATURE_CODE']))
for category in categories:
    matched = 0
    for i, subcategory in enumerate(subcategories):
        if str(subcategory).startswith(str(category)): # categories seem to be named with integers, with subcategories containing their supercategories as prefixes
            metadata['categories'].append({
                "id": i,
                "name": str(subcategory),
                "supercategory": str(category)
            })

# index geometries by bounding box
geoms_by_bounds = {}
geometries = layers['geometry']
for geometry in geometries:
    geoms_by_bounds[geometry.bounds] = geometry
print(f"geom_boxes:{len(geoms_by_bounds)}")

# load images from directory and index by bounding box (to speed up matching)
image_paths = [path for path in os.listdir("orthos") if path[-4:]=='.tif']
print(f"paths:{len(image_paths)}")
images_by_bounds = {}
for i, path in enumerate(image_paths):
    with rasterio.open('orthos/'+path) as src:
        images_by_bounds[src.bounds] = path
        metadata['images'].append({
            "id": i,
            "license": 1,
            "file_name": path,
            "height": src.bounds.top - src.bounds.bottom,
            "width": src.bounds.right - src.bounds.left,
            "date_captured": "null"
        })

# main loop
crop_padding_meters = 10
image_size_pixels = 1024
match_counts = []
for i, geom_bounds in enumerate(geoms_by_bounds):
    matched = False
    match_counts.append(0)
    for j, image_bounds in enumerate(images_by_bounds):
        geom_left, geom_bottom, geom_right, geom_top = geom_bounds # pad the shape by crop_padding_meters on all sides, to include context
        geom_left -= crop_padding_meters
        geom_bottom -= crop_padding_meters
        geom_right += crop_padding_meters
        geom_top += crop_padding_meters
        if (geom_left >= image_bounds.left and geom_bottom >= image_bounds.bottom and geom_right <= image_bounds.right and geom_top <= image_bounds.top): # check if image contains geometry
            match_counts[-1] += 1
            with rasterio.open("orthos/"+images_by_bounds[image_bounds]) as src:
                out_image, out_transform = rasterio.mask.mask(dataset = src, shapes = [box(minx = geom_left, miny = geom_bottom, maxx = geom_right, maxy = geom_top)], crop=True) # convert bbox coords to a shape for cropping
                out_meta = src.meta
                out_meta.update({"driver": "GTiff", # tell rasterio to scale raster to a image_size_pixels square when writing image to file
                 "height": image_size_pixels,
                 "width": image_size_pixels,
                 "transform": out_transform})
                with rasterio.open(f"{out_dir}/{str(i)}_out.tif", 'w', **out_meta) as dst:
                    dst.write(out_image) 
                    metadata['annotations'].append({ # record metadata
                        "id": i,
                        "image_id": j,
                        "category_id": subcategories.index(layers['SUB_FEATURE_CODE'][i]), # this line is clunky but it's fine for the watertowers dataset specifically
                        "bbox": list(geom_bounds),
                        "segmentation": str(geoms_by_bounds[geom_bounds]),
                        "area": layers['Shape_Area'][i], # this line is clunky but it's fine for the watertowers dataset specifically
                        "iscrowd": 0
                    })

mismatches = [x for x in match_counts if x != 1]
print(f"Failed to crop {len(mismatches)} goemetries with {crop_padding_meters} meters of padding:")
print("\n".join([f"Geometry {i} was fully contained within {x} images" for i, x in enumerate(match_counts) if x != 1]))

with open(out_dir+"/metadata.json", "w") as out_file:
    json.dump(metadata, out_file)