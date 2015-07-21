import pyqtgraph as pg
from PySide import QtCore
import numpy as np

class SpectrogramWidget(pg.PlotWidget):
    def __init__(self, blockSize = 1024, samplingFreq = 250):
        super(SpectrogramWidget, self).__init__()

        self.blockSize = blockSize

        self.img = pg.ImageItem()
        self.addItem(self.img)

        self.img_array = np.zeros((100, (blockSize/2)+1))

        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        self.img.setLookupTable(lut)
        self.img.setLevels([-50,40])

        freq = np.arange((blockSize/2)+1)/(float(blockSize)/samplingFreq)
        yscale = 1.0/(self.img_array.shape[1]/freq[-1])
        self.img.scale((1./samplingFreq)*blockSize, yscale)

        self.setLabel('left', 'Frequency', units='Hz')

        self.win = np.hanning(blockSize)
        self.show()

        self.buffer = np.zeros(blockSize)

    def updateValue(self, chunk):
        self.buffer = np.roll(self.buffer, -1)
        self.buffer[-1] = chunk

    def updateGUI(self):
        # normalized, windowed frequencies in data chunk
        spec = np.fft.rfft(self.buffer*self.win) / self.blockSize
        #spec = self.buffer[:self.blockSize / 2 + 1]
        # get magnitude 
        psd = abs(spec)
        # convert to dB scale
        psd = 20 * np.log10(psd)

        # roll down one and replace leading edge with new data
        self.img_array = np.roll(self.img_array, -1, 0)
        self.img_array[-1:] = psd

        self.img.setImage(self.img_array, autoLevels=True)
