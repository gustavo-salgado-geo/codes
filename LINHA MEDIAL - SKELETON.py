#!/usr/bin/env python
# coding: utf-8

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_ubyte
from tqdm import tqdm
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds


# Carregue o shapefile com o arquivo de Massas D'água da área de estudo
gdf = gpd.read_file('C:/Users/gus_h/OneDrive/Área de Trabalho/MASSA DAGUA BAIXO TOCANTINS.shp')


# Criar uma grade para rasterizar os polígonos
pixel_size = 0.0002  # Tamanho do pixel para rasterização
bounds = gdf.total_bounds
width = int((bounds[2] - bounds[0]) / pixel_size)
height = int((bounds[3] - bounds[1]) / pixel_size)


# Gerar a transformação Affine com base nos limites do GeoDataFrame
transform = from_bounds(bounds[0], bounds[1], bounds[2], bounds[3], width, height)


# Rasterizar os polígonos em uma imagem binária
shapes = ((geom, 1) for geom in tqdm(gdf.geometry, desc="Rasterizando polígonos"))
raster = rasterize(shapes, out_shape=(height, width), fill=0, transform=transform)


# Plotar o rasterizado
plt.figure(figsize=(10, 10))
plt.imshow(raster, cmap='gray')
plt.title("Polígonos Rasterizados")
plt.axis('off')
plt.show()


skeleton = skeletonize(raster)


# Visualizar o resultado
plt.figure(figsize=(10, 10))
inverted_skeleton = np.where(skeleton == 1, 0, 1)
plt.imshow(inverted_skeleton, cmap='gray', vmin=0, vmax=1)  # Usar vmin e vmax para garantir a escala
plt.title("Esqueleto Interno")
plt.axis('off')
plt.show()


## Salvar o arquivo Raster
# Converter o skeleton para uint8 (0 e 1)
skeleton_uint8 = (skeleton > 0).astype(np.uint8)

with rasterio.open(
    'C:/Users/gus_h/OneDrive/Área de Trabalho/skeleton.tiff', # troque para o caminho que deseja salvar seu arquivo raster com o skeleton
    'w',
    driver='GTiff',
    height=skeleton_uint8.shape[0],
    width=skeleton_uint8.shape[1],
    count=1,
    dtype=skeleton_uint8.dtype,
    crs='EPSG:4326',  # Troque o CRS, se necessário
    transform=transform  # Use a transformação Affine com base nos limites do GeoDataFrame
) as dst:
    dst.write(skeleton_uint8, 1)  # Escrever a matriz do skeleton na primeira banda

