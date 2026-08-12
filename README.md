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

Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/Sundarbans-Delta-Calculator.git](https://github.com/your-username/Sundarbans-Delta-Calculator.git)
   cd Sundarbans-Delta-Calculator