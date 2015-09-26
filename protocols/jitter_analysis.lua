--sample_rate = flow.Signal()

function update_sample_rate(x)
end


ch1 = flow.TestClock(250.0).output

function setup()

	--ch1 = channels[0]

	sig = flow.ClockAnalyzer(ch1)
	sig.alpha = 0.99999


	OSC = flow.Oscilloscope('Sample Rate (Averaged)', {sig.sample_rate})
	OSC.autoscale = false
	OSC.yrange = {0, 500}
	OSC2 = flow.Oscilloscope('Jitter', {sig.jitter})

	return OSC, OSC2
end

