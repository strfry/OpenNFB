--sample_rate = flow.Signal()

function update_sample_rate(x)
end

--tc = flow.TestClock(250.0)
--ch1 = tc.output

--ch1 = flow.JitterBuffer(channels[0], 250)
ch1 = channels[0]

function setup()


	sig = flow.ClockAnalyzer(ch1)
	sig.alpha = 0.99999


	OSC = flow.Oscilloscope('Sample Rate (Averaged)', {sig.sample_rate})
	OSC.autoscale = false
	OSC.yrange = {0, 500}
	OSC2 = flow.Oscilloscope('Jitter', {sig.jitter})

	jNum = flow.NumberBox('Average Jitter', flow.Averager(sig.jitter))


	OSC3 = flow.Oscilloscope('Signal', {flow.BandPass(5, 11, ch1)})

	return OSC, OSC2, OSC3, jNum
end




-----------------------Auto-Generated config - DO NOT EDIT-----------------------
function doc_config()
	return { float = { }, main = { 'vertical', { { 'dock', 'Sample Rate (Averaged)', { }}, { 'horizontal', { { 'dock', 'Jitter', { }}, { 'dock', 'Average Jitter', { }}}, { sizes = { 542, 91}}}, { 'dock', 'Signal', { }}}, { sizes = { 158, 159, 158}}}}
end