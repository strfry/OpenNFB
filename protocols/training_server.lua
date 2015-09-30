lowInhibitRange = {0.5, 13.0}
rewardRange = {12.0, 15.0}
highInhibitRange = {14.0, 38.0}

-- TODO: Move this kind of function to a lua library, or include something existing
function min(x, y)
	if x < y then
		return x
	else
		return y
	end
end

function setup()

	raw = channels[0]
	raw = flow.NotchFilter(raw)
	raw = flow.DCBlock(raw).ac

	rawOsc = flow.Oscilloscope('Raw', {flow.NotchFilter(channels[0])})

	SPEC = flow.BarSpectrogram('Spectrogram', raw)

	lowInhibitBand = flow.BandPass(lowInhibitRange[1], lowInhibitRange[2], raw)
	rewardBand = flow.BandPass(rewardRange[1], rewardRange[2], raw)
	highInhibitBand = flow.BandPass(highInhibitRange[1], highInhibitRange[2], raw)

	OSC = flow.Oscilloscope('Oscilloscope', {raw, lowInhibitBand, rewardBand, highInhibitBand})

	artifactInhibit = flow.Threshold('Artifact Inhibit', flow.RMS(raw))
	artifactInhibit.mode = 'decrease'
	artifactInhibit.auto_mode = false
	artifactInhibit.threshold = 1000
	-- TODO: AI threshold target

	liThreshold = flow.Threshold('Low Inhibit', flow.RMS(lowInhibitBand))
	liThreshold.auto_target = .85
	liThreshold.mode = 'decrease'

	-- lowInhibitAverage = 

	rThreshold = flow.Threshold('Reward', flow.RMS(rewardBand))
	rThreshold.auto_target = .75
	rThreshold.mode = 'increase'

	hiThreshold = flow.Threshold('High Inhibit', highInhibitBand)
	hiThreshold.auto_target = .95
	hiThreshold.mode = 'decrease'

	rewardRatio = flow.Expression(function(x) return x * 2 - 1 end, rThreshold.ratio)

	flow.Expression(function(x, y) return x + min(y, 1) - 1 end, artifactInhibit.passfail, rewardRatio)

	combinedInhibit = flow.Expression(function(x, y) return x and x end,
		liThreshold.passfail, artifactInhibit.passfail)

	combinedInhibit = artifactInhibit.passfail

	combinedRatio = flow.Expression(function(x, y) return min(x, 1) + y - 1 end,
		rewardRatio, combinedInhibit)

	meter1 = flow.NumberBox('Reward Ratio', rewardRatio)
	meter2 = flow.NumberBox('Combined Ratio', combinedRatio)
	meter3 = flow.NumberBox('Combined Inhibit', combinedInhibit)

	flow.BEServer({rewardRatio, combinedRatio})

	return rawOsc, OSC, SPEC, meter1, meter2, meter3
end




-----------------------Auto-Generated config - DO NOT EDIT-----------------------
function doc_config()
	return { main = { 'vertical', { { 'dock', 'Raw', { }}, { 'dock', 'Oscilloscope', { }}, { 'horizontal', { { 'dock', 'Spectrogram', { }}, { 'vertical', { { 'dock', 'Reward Ratio', { }}, { 'dock', 'Combined Ratio', { }}, { 'dock', 'Combined Inhibit', { }}}, { sizes = { 89, 90, 89}}}}, { sizes = { 509, 124}}}}, { sizes = { 126, 225, 282}}}, float = { }}
end