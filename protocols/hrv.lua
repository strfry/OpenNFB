function peak_func(arg)
	arg = arg * arg
	return arg
end

function setup()

	raw = channels[0]
	ch1 = flow.DCBlock(raw).ac

	lo,hi = 5, 21
	ch1 = flow.BandPass(lo, hi, ch1)
	ch1 = flow.BandPass(lo, hi, ch1)
	ch1 = flow.BandPass(lo, hi, ch1)
	--ch1 = flow.BandPass(lo, hi, ch1)

	ch1.output.color = 'green'

	peaks = flow.PulseAnalyzer(ch1)

	OSC = flow.Oscilloscope('ECG Plot', {ch1})
	peakPlot = flow.Oscilloscope('Peak Plot', {peaks.pulse, peaks, ch1})

	peaks.bpm.color = 'red'
	bpmPlot = flow.Oscilloscope('Beats per Minute', {peaks.bpm})

	--waterfall = flow.Waterfall('ECG Waterfall')

	--waterfall.input = ch1


	ch1.output.buffer_size = 256

	return OSC, peakPlot, bpmPlot
end-----------------------Auto-Generated config - DO NOT EDIT-----------------------
function doc_config()
	return { main = { 'vertical', { { 'dock', 'ECG Plot', { }}, { 'dock', 'Peak Plot', { }}, { 'dock', 'Beats per Minute', { }}}, { sizes = { 158, 159, 158}}}, float = { }}
end