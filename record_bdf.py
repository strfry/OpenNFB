from BDFWriter import BDFWriter
from open_bci_v3 import OpenBCIBoard
import thread

NUM_CHANNELS = 8

bdf = BDF(NUM_CHANNELS)

board = OpenBCIBoard(port='/dev/ttyUSB0', baud=115200, scaled_output=False)
board.print_register_settings()
#board.test_signal(2)
board.print_register_settings()


def handle_sample(sample):
    bdf.append_sample(sample.channel_data)

    if sample.id == 0:
        bdf.write_file(file('record.bdf', 'wb'))

#thread.start_new_thread(board.start_streaming, (handle_sample,))

board.start_streaming(handle_sample)
