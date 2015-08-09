# Thanks to Kurt Othmer for BioExplorer design this is translated from

from flow import *

class Flow(object):
	def init(self, context):
		ch1 = context.get_channel('Channel 1')
		#ch1 = Notch(50, input=ch1)
		ch1_dc = DCBlock(ch1).ac
		ch1_raw = BandPass(0.0, 40.0, input=ch1_dc)

		ch1_theta = BandPass(3.0, 7.0, input=ch1_raw, type='elliptic', order=3).output
		ch1_beta = BandPass(15.0, 18.0, input=ch1_raw, type='ellipic', order=3).output
		ch1_hibeta = BandPass(22, 38.0, input=ch1_raw, type='elliptic', order=3).output

		ch1_raw.set(label='Left Raw: 0-40', color='white')
		ch1_theta.set(label='Left Theta', color='violet')
		ch1_beta.set(label='Left Beta', color='green')
		ch1_hibeta.set(label='Left Hi Beta', color='yellow')

		self.ch1_theta_threshold = Threshold('L Theta', input=RMS(ch1_theta), mode='decrease', auto_target=90)
		self.ch1_beta_threshold = Threshold('L Beta', input=RMS(ch1_beta), mode='range', low_target=90, high_target=95)
		self.ch1_hibeta_threshold = Threshold('L Hi-Beta', input=RMS(ch1_hibeta), mode='decrease', auto_target=95)

		self.ch1_osci = Oscilloscope('Left Side', moving=False,
			channels=[ch1_raw, ch1_theta, ch1_beta, ch1_hibeta])

		self.left_spectrum = BarSpectrogram('Left', lo=2.0, hi=30.0, input=ch1_raw, align='right')

		ch2 = context.get_channel('Channel 2')
		#ch2 = Notch(50, input=ch2)
		ch2_dc = DCBlock(ch2).ac
		ch2_raw = BandPass(0.0, 40.0, input=ch2_dc)

		ch2_theta = BandPass(3.0, 7.0, input=ch2_raw, type='elliptic', order=3).output
		ch2_smr = BandPass(12.0, 15.0, input=ch2_raw, type='ellipic', order=3).output
		ch2_hibeta = BandPass(22, 38.0, input=ch2_raw, type='elliptic', order=3).output

		ch2_raw.set(label='Right Raw: 0-40', color='white')
		ch2_theta.set(label='Right Theta', color='violet')
		ch2_smr.set(label='Right SMR', color='blue')
		ch2_hibeta.set(label='Right Hi Beta', color='yellow')

		self.ch2_theta_threshold = Threshold('R Theta', input=RMS(ch2_theta), mode='decrease', auto_target=90)
		self.ch2_smr_threshold = Threshold('R SMR', input=RMS(ch2_smr), mode='range', low_target=90, high_target=95)
		self.ch2_hibeta_threshold = Threshold('R Hi-Beta', input=RMS(ch2_hibeta), mode='decrease', auto_target=95)

		self.ch2_osci = Oscilloscope('Right Side', moving=False,
			channels=[ch2_raw, ch2_theta, ch2_smr, ch2_hibeta])

		self.right_spectrum = BarSpectrogram('Right', lo=2.0, hi=30.0, input=ch2_raw, align='left')


		and_cond = Expression(lambda *args: all(args),
			self.ch1_theta_threshold.passfail, self.ch1_beta_threshold.passfail, self.ch1_hibeta_threshold.passfail,
			#self.ch2_theta_threshold.passfail, self.ch2_smr_threshold.passfail, self.ch2_hibeta_threshold.passfail
			)

		video_path = '/Users/jonathansieber/Movies/Adventure.Time.S06E22.The.Cooler.720p.HDTV.x264-W4F.mkv'
		self.video = MPlayerControl(video_path, enable=and_cond)
		
	def widget(self):
		w = QtGui.QWidget()
		layout = QtGui.QGridLayout()
		w.setLayout(layout)

		layout.addWidget(self.ch1_osci.widget(), 0, 0, 1, 4)

		layout.addWidget(self.ch1_theta_threshold.widget(), 1, 0)
		layout.addWidget(self.ch1_beta_threshold.widget(), 1, 1)
		layout.addWidget(self.ch1_hibeta_threshold.widget(), 1, 2)

		layout.addWidget(self.left_spectrum.widget(), 1, 3)


		layout.addWidget(self.ch2_osci.widget(), 0, 4, 1, 4)
		layout.addWidget(self.ch2_theta_threshold.widget(), 1, 5)
		layout.addWidget(self.ch2_smr_threshold.widget(), 1, 6)
		layout.addWidget(self.ch2_hibeta_threshold.widget(), 1, 7)
		layout.addWidget(self.right_spectrum.widget(), 1, 4)



		return w

def flow():
	return Flow()

