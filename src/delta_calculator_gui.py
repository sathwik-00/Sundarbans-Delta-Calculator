import sys
import os
import numpy as np
import rasterio
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox, QGroupBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap, BoundaryNorm

class GenericDeltaCalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.path_year1 = ""
        self.path_year2 = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Universal GeoTIFF Delta Change Calculator')
        self.setGeometry(100, 100, 950, 750)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # File Selection Box
        file_group = QGroupBox("1. Select Custom Input Rasters")
        file_layout = QVBoxLayout()
        
        # Year 1 File Picker
        y1_layout = QHBoxLayout()
        self.btn_load_y1 = QPushButton('Load Base Year Raster (T1)')
        self.btn_load_y1.clicked.connect(self.select_year1)
        self.lbl_y1 = QLabel('No dataset selected')
        y1_layout.addWidget(self.btn_load_y1)
        y1_layout.addWidget(self.lbl_y1)

        # Year 2 File Picker
        y2_layout = QHBoxLayout()
        self.btn_load_y2 = QPushButton('Load Comparison Year Raster (T2)')
        self.btn_load_y2.clicked.connect(self.select_year2)
        self.lbl_y2 = QLabel('No dataset selected')
        y2_layout.addWidget(self.btn_load_y2)
        y2_layout.addWidget(self.lbl_y2)

        file_layout.addLayout(y1_layout)
        file_layout.addLayout(y2_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Execution Button
        self.btn_process = QPushButton('Run Delta Matrix & Export GeoTIFF')
        self.btn_process.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background-color: #2e7d32; color: white;")
        self.btn_process.clicked.connect(self.calculate_delta)
        layout.addWidget(self.btn_process)

        # Matplotlib Visualization Canvas
        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def select_year1(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select Base Year GeoTIFF', '', 'GeoTIFF (*.tif *.tiff)')
        if path:
            self.path_year1 = path
            self.lbl_y1.setText(os.path.basename(path))

    def select_year2(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select Comparison Year GeoTIFF', '', 'GeoTIFF (*.tif *.tiff)')
        if path:
            self.path_year2 = path
            self.lbl_y2.setText(os.path.basename(path))

    def calculate_delta(self):
        if not self.path_year1 or not self.path_year2:
            QMessageBox.warning(self, "Dataset Error", "Please select both T1 and T2 raster datasets.")
            return

        try:
            # Read Year 1 Raster
            with rasterio.open(self.path_year1) as src1:
                band_1 = src1.read(1)
                profile = src1.profile
                crs1 = src1.crs
                shape1 = src1.shape

            # Read Year 2 Raster
            with rasterio.open(self.path_year2) as src2:
                band_2 = src2.read(1)
                crs2 = src2.crs
                shape2 = src2.shape

            # Dimension & CRS Check
            if shape1 != shape2:
                QMessageBox.critical(self, "Spatial Error", "Rasters have different dimensions! Resample them to match before processing.")
                return
            
            if crs1 != crs2:
                QMessageBox.warning(self, "CRS Notice", "Datasets have different Coordinate Reference Systems. Ensure both are projected identically (e.g., UTM).")

            # Execute Transition Formula: (T1 * 10) + T2
            delta_band = (band_1 * 10) + band_2

            # Save Output GeoTIFF
            save_path, _ = QFileDialog.getSaveFileName(
                self, 'Save Delta GeoTIFF Output', 'Custom_Delta_Output.tif', 'GeoTIFF (*.tif)'
            )
            
            if save_path:
                profile.update(dtype=rasterio.int32, count=1)
                with rasterio.open(save_path, 'w', **profile) as dst:
                    dst.write(delta_band.astype(rasterio.int32), 1)

            # Render Preview
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            colors = ['#006400', '#FF0000', '#00FFFF', '#32CD32', '#FF8C00', '#000080']
            cmap = ListedColormap(colors)
            bounds = [-0.5, 0.5, 1.5, 2.5, 10.5, 11.5, 22.5]
            norm = BoundaryNorm(bounds, cmap.N)

            ax.imshow(delta_band, cmap=cmap, norm=norm)
            ax.set_title("Spatio-Temporal Delta Change Map", fontsize=12, fontweight='bold')
            ax.axis('off')

            self.canvas.draw()
            QMessageBox.information(self, "Success", "Delta map calculated and exported successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Processing Error", f"Failed to process custom datasets:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GenericDeltaCalculatorApp()
    window.show()
    sys.exit(app.exec_())