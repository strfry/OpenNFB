function setup()

	ch1_raw = channels[1]	

	ch1 = flow.DCBlock(ch1_raw).ac

	ch1 = flow.BandPass(0.1, 33.0, ch1)
	--ch1 = flow.BandPass(0.01, 32.0, input=ch1)
	--ch1 = flow.BandPass(1.0, 32.0, input=ch1)

	OSC1 = flow.Oscilloscope('Raw', {ch1})
	Spec = flow.BarSpectrogram('Raw Spec', ch1)

	theta = flow.BandPass(4, 8, ch1)
	theta = flow.RMS(theta)
	OSC2 = flow.Oscilloscope('Theta', {theta})

	theta.color = 'green'
	thresh = flow.Threshold('Theta Threshold', theta)

	return OSC1, Spec, OSC2, thresh
end


-----------------------Auto-Generated config - DO NOT EDIT-----------------------
function doc_config()
	return { float = { }, main = { 'horizontal', { { 'vertical', { { 'dock', 'Raw', { }}, { 'dock', 'Raw Spec', { }}, { 'dock', 'Theta', { }}}, { sizes = { 165, 164, 165}}}, { 'dock', 'Theta Threshold', { }}}, { sizes = { 680, 137}}}}
end