

--[[
Code based on github.com/y0ast/VAE-Torch

]]


local KLDCriterion, parent = torch.class('nn.KLDCriterion', 'nn.Criterion')

function KLDCriterion:updateOutput(mean, log_var)

	local mean_sq = torch.pow(mean, 2)
	local KLDelements = log_var:clone()

	KLDelements:exp():mul(-1)
	KLDelements:add(-1, mean_sq)
	KLDelements:add(1)
	KLDelements:add(log_var)

	self.output = -0.5 * torch.sum(KLDelements)

	return self.output
end

function KLDCriterion:updateGradInput(mean, log_var)
	self.gradInput = {}
	self.gradInput[1] = mean:clone()
	self.gradInput[2] = torch.exp(log_var):mul(-1):add(1):mul(-0.5)
	return self.gradInput
end