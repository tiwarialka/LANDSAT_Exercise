'''
cretaed by Alka Tiwari
date: June 30, 2024
This script requests and downloads the landsat data
and plots the time series.
'''

import ee
import wxee as wx
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for rendering to files
import matplotlib.pyplot as plt
import numpy as np


# Authenticate and initialize Earth Engine
ee.Authenticate()
ee.Initialize()
wx.Initialize()

# Apply scale factors to Landsat images
def apply_scale_factors(image):
    opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True)

# Define function to calculate NDVI and extract time series
def extract_ndvi_timeseries(aoi, product_id, start_date, end_date):
    dataset = ee.ImageCollection(product_id).filterDate(start_date, end_date).filterBounds(aoi)
    dataset = dataset.map(apply_scale_factors)
    ds = dataset.wx.to_xarray(region=aoi.bounds(), scale=30)
    ds_ndvi = (ds.SR_B5 - ds.SR_B4) / (ds.SR_B5 + ds.SR_B4)
    mean_ndvi = ds_ndvi.mean(dim='x').mean(dim='y')
    return mean_ndvi

# Plot NDVI timeseries for different Landsat products and tiers
def plot_ndvi_timeseries(aoi, landsat_products):
    plt.figure(figsize=(12, 6))
    for product_name, product_info in landsat_products.items():
        mean_ndvi = extract_ndvi_timeseries(aoi, product_info['id'], product_info['start_date'], product_info['end_date'])
        mean_ndvi.plot(label=product_name, alpha=0.7, marker='o')
    plt.grid()
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('NDVI', fontsize=12)
    plt.title('NDVI Timeseries for Different Landsat Products')
    plt.legend()
    plt.show()

# Define AOI and Landsat products with details
aoi = ee.Geometry.Polygon([[[-91.3625, 46.1597], [-91.3625, 46.1416], [-91.33, 46.1416], [-91.33, 46.1597]]])

# landsat_products = {
#     'LANDSAT 9 Tier 2': {'id': 'LANDSAT/LC09/C02/T2_L2', 'start_date': '2021-10-31', 'end_date': '2024-04-18'},
#     'LANDSAT 9 Tier 1': {'id': 'LANDSAT/LC09/C02/T1_L2', 'start_date': '2021-10-31', 'end_date': '2024-04-18'},
#     'LANDSAT 8 Tier 2': {'id': 'LANDSAT/LC08/C02/T2_L2', 'start_date': '2013-03-18', 'end_date': '2024-04-13'},
#     'LANDSAT 8 Tier 1': {'id': 'LANDSAT/LC08/C02/T1_L2', 'start_date': '2013-03-18', 'end_date': '2024-04-13'},
#     'LANDSAT 7 Tier 2': {'id': 'LANDSAT/LE07/C02/T2_L2', 'start_date': '2013-01-01', 'end_date': '2024-01-19'},
#     'LANDSAT 7 Tier 1': {'id': 'LANDSAT/LE07/C02/T1_L2', 'start_date': '2013-01-01', 'end_date': '2024-01-19'}
# }

landsat_products = {
    'LANDSAT 9 Tier 2': {'id': 'LANDSAT/LC09/C02/T2_L2', 'start_date': '2021-10-31', 'end_date': '2024-04-18'},
    'LANDSAT 9 Tier 1': {'id': 'LANDSAT/LC09/C02/T1_L2', 'start_date': '2021-10-31', 'end_date': '2024-04-18'},
 }
# Plot and save NDVI timeseries for each Landsat product
for product_name, product_info in landsat_products.items():
    mean_ndvi = extract_ndvi_timeseries(aoi, product_info['id'], product_info['start_date'], product_info['end_date'])
    plt.figure(figsize=(10, 5))
    mean_ndvi.plot(alpha=0.7, marker='o', color='maroon')
    plt.grid()
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('NDVI', fontsize=12)
    plt.title(f'{product_name} NDVI Timeseries')
    plt.savefig(f'{product_name}_NDVI_Timeseries.png')
    plt.show()

# Plot composite NDVI timeseries
plot_ndvi_timeseries(aoi, landsat_products)
