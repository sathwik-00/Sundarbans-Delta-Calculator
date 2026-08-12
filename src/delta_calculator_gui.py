import sys
import numpy as np
import rasterio
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap, BoundaryNorm

class DeltaCalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        self.path_2020 = ""
        self.path_2024 = ""

    def initUI(self):
        self.setWindowTitle('Mangrove Delta Change Calculator')
        self.setGeometry(100, 100, 900, 700)

        # Main Widget & Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # File Selection Controls
        file_layout = QHBoxLayout()
        
        self.btn_load_2020 = QPushButton('Select 2020 Raster')
        self.btn_load_2020.clicked.connect(self.select_2020)
        self.lbl_2020 = QLabel('No file selected')
        
        self.btn_load_2024 = QPushButton('Select 2024 Raster')
        self.btn_load_2024.clicked.connect(self.select_2024)
        self.lbl_2024 = QLabel('No file selected')

        file_layout.addWidget(self.btn_load_2020)
        file_layout.addWidget(self.lbl_2020)
        file_layout.addWidget(self.btn_load_2024)
        file_layout.addWidget(self.lbl_2024)
        layout.addLayout(file_layout)

        # Run Button
        self.btn_process = QPushButton('Calculate & Display Delta')
        self.btn_process.clicked.connect(self.calculate_delta)
        layout.addWidget(self.btn_process)

        # Matplotlib Canvas for Map Rendering
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def select_2020(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select 2020 Raster', '', 'GeoTIFF (*.tif *.tiff)')
        if path:
            self.path_2020 = path
            self.lbl_2020.setText(path.split('/')[-1])

    def select_2024(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select 2024 Raster', '', 'GeoTIFF (*.tif *.tiff)')
        if path:
            self.path_2024 = path
            self.lbl_2024.setText(path.split('/')[-1])

    def calculate_delta(self):
        if not self.path_2020 or not self.path_2024:
            QMessageBox.warning(self, "Input Error", "Please select both 2020 and 2024 rasters.")
            return

        try:
            # Read input rasters
            with rasterio.open(self.path_2020) as src2020:
                band_2020 = src2020.read(1)
                profile = src2020.profile

            with rasterio.open(self.path_2024) as src2024:
                band_2024 = src2024.read(1)

            # Delta Calculation: (2020 * 10) + 2024
            delta_band = (band_2020 * 10) + band_2024

            # Prompt user to save the output file
            save_path, _ = QFileDialog.getSaveFileName(self, 'Save Output GeoTIFF', 'Sundarbans_Delta_Output.tif', 'GeoTIFF (*.tif)')
            if save_path:
                profile.update(dtype=rasterio.int32, count=1)
                with rasterio.open(save_path, 'w', **profile) as dst:
                    dst.write(delta_band.astype(rasterio.int32), 1)

            # Render the Map Plot
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            # Define Custom Color Palette and Legend
            colors = ['#006400', '#FF0000', '#00FFFF', '#32CD32', '#FF8C00', '#000080']
            cmap = ListedColormap(colors)
            bounds = [-0.5, 0.5, 1.5, 2.5, 10.5, 11.5, 22.5]
            norm = BoundaryNorm(bounds, cmap.N)

            cax = ax.imshow(delta_band, cmap=cmap, norm=norm)
            ax.set_title("Sundarbans Delta Canopy Change Map", fontsize=12, fontweight='bold')
            ax.axis('off')

            self.canvas.draw()
            QMessageBox.information(self, "Success", "Delta calculation and map rendering complete!")

        except Exception as e:
            QMessageBox.critical(self, "Processing Error", f"An error occurred: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DeltaCalculatorApp()
    window.show()
    sys.exit(app.exec_())