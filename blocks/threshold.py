class Threshold(Block):
    input = Input()
    ratio = Output(input)
    #passfail = Output(input)


    average_period = .35
    epoch = 13.0

    # auto_mode = Bool(True)
    # mode = Enum('increase', 'decrease', 'range')

    auto_target = 0.8

    # low_target = Float(0.90)
    # high_target = Float(0.90)


    def init(self, mode):
        assert mode in ('increase', 'decrease')
        self.mode = mode


        epoch_samples = int(self.input.sample_rate * self.epoch)
        self.gr_block.set_history(epoch_samples)
        print ('Threshold set_history(%d)' % epoch_samples)
        
        self.threshold = 1.0
        self.high_threshold = 0.0
        self.calc_cnt = 0

        self.auto_mode = True

        self.color = QtGui.QColor(self.input.color)

        self.widget = Threshold.Widget(self)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateGUI)
        self.timer.start(100)


        self.current_passfail = False
        self.current_value = 0.0


    def updateGUI(self):
        self.widget.update()

    def general_work(self, input_items, output_items):
        #print ('Threshold work', len(input_items[0]), output_items, input_items[0][0])
        self.gr_block.consume_each(1)   

        avg_period_samples = int(self.average_period * self.input.sample_rate)

        avg = sum(input_items[0][-avg_period_samples:]) / avg_period_samples
        self.current_value = avg
        #self.signal.append([avg])
        #self.signal.process()

        self.calc_cnt += 1
        #self.calc_cnt = avg_period_samples
        if self.auto_mode and self.calc_cnt >= avg_period_samples:
            self.calc_cnt = 0
            avg_period = input_items[0][-avg_period_samples:]

            if self.mode == 'decrease':
                self.threshold = np.percentile(input_items[0], 100 * self.auto_target)
            elif self.mode == 'increase':
                self.threshold = np.percentile(input_items[0], 100 - 100 * self.auto_target)
            else:
                self.high_threshold = np.percentile(input_items[0], self.high_target)
                self.threshold = np.percentile(input_items[0], 100 - 100 * self.low_target)

        success = False

        if self.mode == 'decrease':
            if avg < self.threshold:
                success = True
        elif self.mode == 'increase':
            if avg > self.threshold:
                success = True
        else:
            if avg > self.threshold and avg < self.high_threshold:
                success = True

        output_items[0][0] = avg / self.threshold
        #self.output_items[1] = success
        self.gr_block.produce(0, 1)

        self.current_passfail = success
        return 0



    class Widget(QtGui.QWidget):
        MAX = 25

        def __init__(self, threshold):
            QtGui.QWidget.__init__(self)

            self.threshold = threshold

            self.setMinimumSize(42, 23 * 5)

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)

            width = self.width()
            height = self.height()

            top, bottom = height * .1, height * .8
            left, right = width * .1, width * .8

            rect = QtCore.QRect(left, top, right, bottom)       
            painter.fillRect(rect, QtGui.QColor('black'))

            #painter.setWindow(rect)

            dist = bottom - top

            relval = self.threshold.current_value / self.MAX
            relval = min(1.0, relval)

            reltop = (1.0 - relval) * bottom + top
            relbottom = height * 0.9 - reltop 

            rect = QtCore.QRect(left, reltop, right, relbottom)

            color = QtGui.QColor('green' if self.threshold.current_passfail else 'red')
            painter.fillRect(rect, color)


            thr_height = self.threshold.threshold / self.MAX

            thr_top = (1.0 - thr_height) * bottom + top

            rect = QtCore.QRect(left, thr_top, right, 2)        
            painter.fillRect(rect, QtGui.QColor('white'))


            #painter.setBrush

