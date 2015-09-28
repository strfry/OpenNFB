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

	SPEC = flow.BarSpectrogram('Spectrogram', raw)

	lowInhibitBand = flow.BandPass(lowInhibitRange[1], lowInhibitRange[2], raw)
	rewardBand = flow.BandPass(rewardRange[1], rewardRange[2], raw)
	highInhibitBand = flow.BandPass(highInhibitRange[1], highInhibitRange[2], raw)

	OSC = flow.Oscilloscope('Oscilloscope', {raw, lowInhibitBand, rewardBand, highInhibitBand})

	artifactInhibit = flow.Threshold('Artifact Inhibit', flow.RMS(raw))
	artifactInhibit.mode = 'decrease'
	artifactInhibit.auto_mode = false

	liTreshold = flow.Threshold('Low Inhibit', flow.RMS(lowInhibitBand))
	liTreshold.auto_target = 0.85
	liTreshold.mode = 'decrease'

	-- lowInhibitAverage = 

	rThreshold = flow.Threshold('Reward', flow.RMS(rewardBand))
	rThreshold.auto_target = 0.75
	rThreshold.mode = 'increase'

	hiThreshold = flow.Threshold('High Inhibit', highInhibitBand)
	hiThreshold.auto_target = 0.95
	hiThreshold.mode = 'decrease'

	rewardRatio = flow.Expression(function(x) return x * 2 - 1 end, rThreshold.ratio)

	flow.Expression(function(x, y) return x + min(y, 1) - 1 end, artifactInhibit.passfail, rewardRatio)

	combinedInhibit = flow.Expression(function(x, y) return x and y end,
		liTreshold.passfail, artifactInhibit.passfail)

	combinedRatio = flow.Expression(function(x, y) return min(x, 1) + y - 1 end,
		rewardRatio, combinedInhibit)

	meter1 = flow.NumberBox('Reward Ratio', rewardRatio)
	meter2 = flow.NumberBox('Combined Ratio', combinedRatio)

	flow.BEServer({rewardRatio})

	return OSC, SPEC, meter1, meter2
end



-----------------------Auto-Generated config - DO NOT EDIT-----------------------
function doc_config()
	return { float = { }, main = { 'vertical', { { 'dock', 'Oscilloscope', { }}, { 'horizontal', { { 'dock', 'Spectrogram', { }}, { 'vertical', { { 'dock', 'Reward Ratio', { }}, { 'dock', 'Combined Ratio', { }}}, { sizes = { 127, 126}}}}, { sizes = { 493, 140}}}}, { sizes = { 378, 260}}}}
end