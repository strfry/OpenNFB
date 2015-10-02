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
	artifactInhibit.threshold = 1000
	-- TODO: AI threshold target

	liThreshold = flow.Threshold('Low Inhibit', flow.RMS(lowInhibitBand))
	liThreshold.auto_target = .85
	liThreshold.mode = 'decrease'

	rThreshold = flow.Threshold('Reward', flow.RMS(rewardBand))
	rThreshold.auto_target = .75
	rThreshold.mode = 'increase'

	hiThreshold = flow.Threshold('High Inhibit', highInhibitBand)
	hiThreshold.auto_target = .95
	hiThreshold.mode = 'decrease'


	function ratioRangeFunction(x)
		return 1.0 - ((x * 2.8571) - 1.8571)
	end

	liRatio = flow.Expression(ratioRangeFunction, liThreshold.ratio)
	hiRatio = flow.Expression(ratioRangeFunction, hiThreshold.ratio)

	inhibitRatio = flow.Expression(function(x, y, z) return ((min(x,1) + min(y,1)) / 2) + z - 1 end,
		liRatio, hiRatio, artifactInhibit.passfail)


	rewardRatio = flow.Expression(function(x) return x * 2 - 1 end, rThreshold.ratio)
	rewardRatio = flow.Expression(function (x, y) return (x + min(y,1)) - 1 end,
		artifactInhibit.passfail, rewardRatio)

	combinedInhibit = flow.Expression(function(x, y) return x and x end,
		liThreshold.passfail, artifactInhibit.passfail)


	combinedRatio = flow.Expression(function(x, y) return min(x, 1) + y - 1 end,
		rewardRatio, combinedInhibit)

	rewardThreshold = flow.Expression(function(x, y) return x and y end,
		artifactInhibit.passfail, rThreshold.passfail)

	combinedThreshold = flow.Expression(function(x, y) return x and y end,
		rewardThreshold, combinedInhibit)


	combinedRatio.output.name = 'Combined Ratio'
	combinedThreshold.output.name =  'Combined Thresh'
	inhibitRatio.output.name = 'Inhibit Ratio'
	combinedInhibit.output.name = 'Inhibit Thresh'
	rewardRatio.output.name = 'Reward Ratio'
	rewardThreshold.output.name = 'Reward Thresh'

	meter1 = flow.NumberBox('Reward Ratio', rewardRatio)
	meter2 = flow.NumberBox('Combined Ratio', combinedRatio)
	meter3 = flow.NumberBox('Inhibit Ratio', inhibitRatio)
	meter4 = flow.NumberBox('Combined Inhibit (Thresh)', combinedInhibit)
	meter5= flow.NumberBox('Reward Ratio', rewardRatio)
	meter6 = flow.NumberBox('Reward Thresh', rewardThreshold)

	flow.BEServer({combinedRatio, combinedThreshold, inhibitRatio, combinedInhibit,
		rewardRatio, rewardThreshold})

	return OSC, SPEC, meter1, meter2, meter3, meter4, meter5, meter6
end




-----------------------Auto-Generated config - DO NOT EDIT-----------------------
function doc_config()
	return { float = { }, main = { 'vertical', { { 'dock', 'Oscilloscope', { }}, { 'horizontal', { { 'dock', 'Spectrogram', { }}, { 'vertical', { { 'dock', 'Reward Ratio', { }}, { 'dock', 'Combined Ratio', { }}, { 'dock', 'Inhibit Ratio', { }}, { 'dock', 'Combined Inhibit (Thresh)', { }}, { 'dock', 'Reward Ratio', { }}, { 'dock', 'Reward Thresh', { }}}, { sizes = { 39, 39, 38, 39, 39, 39}}}}, { sizes = { 544, 89}}}}, { sizes = { 367, 268}}}}
end