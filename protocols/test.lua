function setup()

	left_raw = channels[0]
	right_raw = channels[1]

	left = flow.DCBlock(left_raw).ac
	right = flow.DCBlock(right_raw).ac

	left = flow.BandPass(0.1, 33.0, left)
	left = flow.BandPass(0.1, 33.0, left)
	left = flow.BandPass(0.1, 33.0, left)

	right = flow.BandPass(0.1, 33.0, right)
	right = flow.BandPass(0.1, 33.0, right)
	right = flow.BandPass(0.1, 33.0, right)
	--left = flow.BandPass(0.01, 32.0, left)
	--left = flow.BandPass(1.0, 32.0, input=left)

	OSCL = flow.Oscilloscope('Raw Left', {left})
	OSCR = flow.Oscilloscope('Raw Right', {right})

	SpecL = flow.BarSpectrogram('Left Spectrogram', left)
	SpecR = flow.BarSpectrogram('Right Spectrogram', right)

	leftWaterfall = flow.Waterfall('Left Waterfall')
	leftWaterfall.input = left

	rightWaterfall = flow.Waterfall('Right Waterfall')
	rightWaterfall.input = right

	return OSCL, OSCR, SpecL, SpecR, leftWaterfall, rightWaterfall
end-----------------------Auto-Generated config - DO NOT EDIT-----------------------
function doc_config()
	return { main = { 'vertical', { { 'horizontal', { { 'vertical', { { 'dock', 'Raw Left', { }}, { 'dock', 'Left Spectrogram', { }}}, { sizes = { 197, 197}}}, { 'vertical', { { 'dock', 'Raw Right', { }}, { 'dock', 'Right Spectrogram', { }}}, { sizes = { 197, 197}}}}, { sizes = { 329, 328}}}, { 'dock', 'Left Waterfall', { }}}, { sizes = { 401, 201}}}, float = { }}
end