function setup()

	left_raw = channels[0]
	right_raw = channels[1]

	left = flow.DCBlock(left_raw).dc
	right = flow.DCBlock(right_raw).dc

	left = flow.NotchFilter(left)
	right = flow.NotchFilter(right)
	left.module_pole = 0.8
	right.module_pole = 0.8

	left = flow.NotchFilter(left)
	left.frequency = 100
	right = flow.NotchFilter(right)
	right.frequency = 100

	--left = flow.BandPass(1, 60.0, left)
	
	--right = flow.BandPass(1, 60.0, right)
	
	OSCL = flow.Oscilloscope('Raw Left', {left})
	OSCR = flow.Oscilloscope('Raw Right', {right})

	SpecL = flow.BarSpectrogram('Left Spectrogram', left)
	SpecR = flow.BarSpectrogram('Right Spectrogram', right)

	SpecL.lo, SpecL.hi = 0, 40
	SpecR.lo, SpecR.hi = 0, 40

	leftWaterfall = flow.Waterfall('Left Waterfall')
	leftWaterfall.input = left

	leftWaterfall.lo, leftWaterfall.hi = 0, 40

	rightWaterfall = flow.Waterfall('Right Waterfall')
	rightWaterfall.input = right
	rightWaterfall.lo, rightWaterfall.hi = 0, 40

	return OSCL, OSCR, SpecL, SpecR, leftWaterfall, rightWaterfall
end

-----------------------Auto-Generated config - DO NOT EDIT-----------------------
function doc_config()
	return { main = { 'vertical', { { 'horizontal', { { 'vertical', { { 'dock', 'Raw Left', { }}, { 'dock', 'Left Spectrogram', { }}, { 'dock', 'Left Waterfall', { }}}, { sizes = { 209, 135, 282}}}, { 'vertical', { { 'dock', 'Raw Right', { }}, { 'dock', 'Right Spectrogram', { }}, { 'dock', 'Right Waterfall', { }}}, { sizes = { 209, 134, 283}}}}, { sizes = { 538, 538}}}}, { sizes = { 640}}}, float = { }}
end