import time
from flow import *

ch1 = Signal()
ch1.sample_rate = 250

server = BEServer({1:ch1})

import random, math
cnt = 0

while True:
	cnt += 1
	val = (math.sin(cnt / 250) + 1 )

	ch1.append([val])
	ch1.process()
	time.sleep(1.0 / 250)
