-- Tools/OptimizeParts (D-027): static performance pass. Re-run after any Apply* import.
--   require(game.ServerStorage.Tools.OptimizeParts)()            -> applies, returns a report
--   require(game.ServerStorage.Tools.OptimizeParts)(true)        -> dry run (counts only)
-- Only touches NON-colliding parts (decor/visual meshes), so walls, floors, pads and camera occluders keep working:
--   CanTouch off (no touch events to compute)          CanQuery off (raycasts + camera skip them)
--   MeshPart CollisionFidelity Box (no hull/decomposition geometry kept in memory)
--   CastShadow off for Neon, see-through, small (< 3.5 studs) and flat floor parts (phones pay per shadow caster)
--   RenderFidelity Precise -> Automatic (lets Roblox drop to lower LODs at distance)
-- Protected (left alone): anything under a Pads folder, Collision, CameraProxies, Rim, Meteors, Pets folders,
-- parts named Base/Trigger/Hitbox, and parts carrying a ClickDetector or ProximityPrompt.
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PROTECT_FOLDERS = { Pads = true, Collision = true, CameraProxies = true, Rim = true, Meteors = true, Pets = true }
local PROTECT_NAMES = { Base = true, Trigger = true, Hitbox = true, Pad = true, Touch = true }
local SMALL = 3.5

local function protected(p: BasePart): boolean
	if PROTECT_NAMES[p.Name] then return true end
	if p:FindFirstChildWhichIsA("ClickDetector") or p:FindFirstChildWhichIsA("ProximityPrompt", true) then return true end
	local a = p.Parent
	while a and a ~= game do
		if PROTECT_FOLDERS[a.Name] then return true end
		a = a.Parent
	end
	return false
end

local function inFloor(p: BasePart): boolean
	local a = p.Parent
	while a and a ~= game do
		if a.Name == "Floor" or a.Name == "PlotFloor" then return true end
		a = a.Parent
	end
	return false
end

return function(dry: boolean?)
	local n = { scanned = 0, touch = 0, query = 0, fidelity = 0, shadow = 0, render = 0 }
	local roots = { workspace, ReplicatedStorage:FindFirstChild("Assets"), ServerStorage:FindFirstChild("Art"), ServerStorage:FindFirstChild("Templates") }
	for _, root in ipairs(roots) do
		if not root then continue end
		for _, p in ipairs(root:GetDescendants()) do
			if not p:IsA("BasePart") or p:IsA("Terrain") then continue end
			n.scanned += 1
			if p:IsA("MeshPart") and p.RenderFidelity == Enum.RenderFidelity.Precise then
				n.render += 1
				if not dry then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Automatic end) end
			end
			local s = p.Size
			local big = math.max(s.X, s.Y, s.Z)
			local wantShadow = p.CastShadow
				and not (p.Material == Enum.Material.Neon or p.Material == Enum.Material.ForceField or p.Material == Enum.Material.Glass)
				and p.Transparency < 0.5 and big >= SMALL and not inFloor(p)
			if p.CastShadow and not wantShadow then
				n.shadow += 1
				if not dry then p.CastShadow = false end
			end
			if p.CanCollide or protected(p) then continue end
			if p.CanTouch then n.touch += 1 if not dry then p.CanTouch = false end end
			if p.CanQuery then n.query += 1 if not dry then p.CanQuery = false end end
			if p:IsA("MeshPart") and p.CollisionFidelity ~= Enum.CollisionFidelity.Box then
				n.fidelity += 1
				if not dry then pcall(function() p.CollisionFidelity = Enum.CollisionFidelity.Box end) end
			end
		end
	end
	local msg = ("[OptimizeParts]%s scanned %d | CanTouch off %d | CanQuery off %d | Box collision %d | shadows off %d | Precise->Auto %d")
		:format(dry and " (dry)" or "", n.scanned, n.touch, n.query, n.fidelity, n.shadow, n.render)
	print(msg)
	return msg
end
