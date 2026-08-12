Sundarbans Mangrove Delta Change Calculator GUI

A desktop application built using **Python**, **PyQt5**, **Rasterio**, and **Matplotlib** to compute spatio-temporal canopy transition matrices and visualize change detection across the Sundarbans Delta ($2020$–$2024$).

Methodology & Formula

The application executes a post-classification matrix calculation across reprojected UTM (`EPSG:32645`) raster bands:

$$\text{Delta} = (\text{Band}_{2020} \times 10) + \text{Band}_{2024}$$

Transition Codes & Classes

| Value | Classification Class | Color Hex |
| :---: | :--- | :---: |
| **0** | Stable Healthy Canopy | `#006400` |
| **1** | Severe Forest Loss / Defoliation | `#FF0000` |
| **2** | Coastal Inundation / Erosion | `#00FFFF` |
| **10** | Forest Recovery / Regeneration | `#32CD32` |
| **11** | Persistent Degraded Land | `#FF8C00` |
| **22** | Stable Estuarine Water | `#000080` |


How to Generate Custom GeoTIFF Datasets

If you need classified single-band GeoTIFF files for a specific year (e.g., 2021), you can generate and export them directly to your Google Drive using **Google Earth Engine (GEE)**:

1. Open the [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Paste the following JavaScript code into the editor:

```javascript
// 1. Define Sundarbans Region of Interest (ROI)
var roi = ee.Geometry.Rectangle([88.0, 21.5, 89.2, 22.5]);

// 2. Fetch Sentinel-2 Surface Reflectance for Target Year
var targetYear = 2021; // Change year as needed
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(roi)
  .filterDate(targetYear + '-01-01', targetYear + '-12-31')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
  .median()
  .clip(roi);

// 3. Compute Normalized Difference Vegetation Index (NDVI)
var ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI');

// 4. Reclassify into Discrete Classes
// Class 0: Dense/Healthy Mangrove (NDVI >= 0.4)
// Class 1: Degraded Vegetation (0 <= NDVI < 0.4)
// Class 2: Water (NDVI < 0)
var classified = ee.Image(1)
  .where(ndvi.gte(0.4), 0)
  .where(ndvi.lt(0), 2)
  .toInt32();

// 5. Export as Single-Band GeoTIFF to Google Drive
Export.image.toDrive({
  image: classified,
  description: 'Sundarbans_Classification_' + targetYear + '_UTM',
  scale: 20,
  region: roi,
  crs: 'EPSG:32645',
  fileFormat: 'GeoTIFF'
});