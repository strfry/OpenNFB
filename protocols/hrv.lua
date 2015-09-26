function peak_func(arg)
	arg = arg * arg
	return arg
end

function setup()

	raw = channels[0]
	ch1_raw = flow.DCBlock(raw).ac
	ch1 = flow.NotchFilter(ch1_raw)

	ch1.output.color = 'green'

	lo,hi = 1, 125
	ch1 = flow.BandPass(lo, hi, ch1)
	--ch1 = flow.BandPass(lo, hi, ch1)

	ch1.output.color = 'green'

	peaks = flow.PulseAnalyzer(ch1)

	OSC = flow.Oscilloscope('ECG Plot', {ch1})
	peakPlot = flow.Oscilloscope('Peak Plot', {peaks.pulse, peaks, ch1})

	peaks.bpm.color = 'red'
	bpmPlot = flow.Oscilloscope('Beats per Minute', {peaks.bpm})

	waterfall = flow.Waterfall('ECG Waterfall')
	waterfall.window_size = 256
	waterfall.hi = 125

	waterfall.input = ch1


	ch1.output.buffer_size = 256

	return OSC, peakPlot, bpmPlot,
		waterfall
end

-----------------------Auto-Generated config - DO NOT EDIT-----------------------
function doc_config()
	return { main = { 'horizontal', { { 'vertical', { { 'dock', 'ECG Plot', { }}, { 'dock', 'Peak Plot', { }}, { 'dock', 'Beats per Minute', { }}}, { sizes = { 158, 159, 158}}}, { 'dock', 'ECG Waterfall', { }}}, { sizes = { 423, 423}}}, float = { }}
end