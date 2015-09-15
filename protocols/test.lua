function setup()

	ch1_raw = channels[1]	

	ch1 = flow.DCBlock(ch1_raw).ac

	ch1 = flow.BandPass(0.01, 32.0, ch1)
	--ch1 = flow.BandPass(0.01, 32.0, input=ch1)
	--ch1 = flow.BandPass(1.0, 32.0, input=ch1)

	OSC1 = flow.Oscilloscope('Raw', {ch1})
	Spec = flow.BarSpectrogram('Raw Spec', ch1)

	return OSC1, Spec
end

function gui()
	print ('FOOOOOO')
	print (OSC1)
end