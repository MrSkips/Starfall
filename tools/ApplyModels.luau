-- tools/ApplyModels: turns the imported Blender FBX (tools/blender/build_models.py -> art/models/SF_Models.fbx)
-- into templates and dresses every plot.
--   require(game.ServerStorage.Tools.ApplyModels)()
-- Part names from Blender: <Model>__<Part>__<MatKey>. MatKey -> Roblox Material + Color (no baked textures).
-- Templates:  ServerStorage.Art.Machines  (plot items, animated by the client MachineAnimator)
--             ServerStorage.Art.Props     (Pad, Sign)
--             ServerStorage.Art.Meteors   (Normal, Molten, Frozen, Charged, Cosmic, Starheart; MeteorService welds them on)
local ServerStorage = game:GetService("ServerStorage")

local SP = Enum.Material.SmoothPlastic
local NEON = Enum.Material.Neon
local MAT = {
	Red = { SP, "D95542" }, Cream = { SP, "FFF0CF" }, Steel = { SP, "344658" }, SteelLight = { SP, "6E7F93" },
	Dark = { SP, "1F2430" }, Yellow = { SP, "FFC83D" },
	Glow = { NEON, "FF9A3C" }, Ember = { NEON, "FF5A1E" }, Gold = { NEON, "FFD24A" },
	Leather = { SP, "9B5B3A" }, Wood = { SP, "C98A4E" }, WoodDark = { SP, "8A5A34" }, Boot = { SP, "4FA3FF" },
	Teal = { NEON, "64DFD1" }, Green = { NEON, "50DC78" },
	RockGrey = { Enum.Material.Slate, "7D7A85" }, RockDark = { Enum.Material.Slate, "4A4652" },
	Basalt = { Enum.Material.Basalt, "3B3540" }, Lava = { NEON, "FF6A1E" },
	IceRock = { SP, "9FC9E0" }, Ice = { Enum.Material.Ice, "BDEBFF" },
	ChargedRock = { SP, "3E4A66" }, Bolt = { NEON, "FFE14A" },
	CosmicRock = { SP, "3A2A5E" }, CosmicGlow = { NEON, "B07CFF" },
}

-- kind + plot-local spot (origin = plot surface centre, -Z faces the crater; matches BuildGreybox)
local REG = {
	Crusher = { kind = "Machines", spot = Vector3.new(-18, 0, 16) },
	Smelter = { kind = "Machines", spot = Vector3.new(-6, 0, 16) },
	Forge = { kind = "Machines", spot = Vector3.new(6, 0, 16) },
	StarAnvil = { kind = "Machines", spot = Vector3.new(18, 0, 16) },
	Conveyor = { kind = "Machines", spot = Vector3.new(-18, 0, 3.5) },
	Bellows = { kind = "Machines", spot = Vector3.new(-0.5, 0, 22) },
	CarryBoots1 = { kind = "Machines", spot = Vector3.new(25, 0, 2) },
	Pad = { kind = "Props" },
	Sign = { kind = "Props" },
	MeteorNormal = { kind = "Meteors", id = "Normal" },
	MeteorMolten = { kind = "Meteors", id = "Molten" },
	MeteorFrozen = { kind = "Meteors", id = "Frozen" },
	MeteorCharged = { kind = "Meteors", id = "Charged" },
	MeteorCosmic = { kind = "Meteors", id = "Cosmic" },
	Starheart = { kind = "Meteors", id = "Starheart" },
}
local CRUSHER_HEIGHT = 11.4 -- modelled height in Blender: normalises the FBX import scale

local function bboxOf(parts)
	local mn, mx = Vector3.new(math.huge, math.huge, math.huge), Vector3.new(-math.huge, -math.huge, -math.huge)
	for _, p in ipairs(parts) do
		local cf, s = p.CFrame, p.Size / 2
		for _, sx in ipairs({ -1, 1 }) do for _, sy in ipairs({ -1, 1 }) do for _, sz in ipairs({ -1, 1 }) do
			local w = cf * Vector3.new(sx * s.X, sy * s.Y, sz * s.Z)
			mn = mn:Min(w)
			mx = mx:Max(w)
		end end end
	end
	return mn, mx
end

local function setVisible(model: Instance, visible: boolean)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("BasePart") then d.Transparency = visible and (d:GetAttribute("BaseTransparency") or 0) or 1 end
	end
end

return function()
	-- 1) find imported mesh parts
	local groups, imported = {}, {}
	for _, d in ipairs(workspace:GetDescendants()) do
		if d:IsA("MeshPart") then
			local model, pname, mat = string.match(d.Name, "^(%w+)__(%w+)__(%w+)$")
			if model and REG[model] and MAT[mat] then
				groups[model] = groups[model] or {}
				table.insert(groups[model], { part = d, name = pname, mat = mat })
				local top = d
				while top.Parent and top.Parent ~= workspace do top = top.Parent end
				imported[top] = true
			end
		end
	end
	assert(groups.Crusher, "No imported models found. Import art/models/SF_Models.fbx first (File > Import 3D).")

	-- 2) uniform scale from the Crusher
	local cParts = {}
	for _, e in ipairs(groups.Crusher) do table.insert(cParts, e.part) end
	local mn, mx = bboxOf(cParts)
	local factor = CRUSHER_HEIGHT / (mx.Y - mn.Y)

	-- 3) templates
	local art = ServerStorage:FindFirstChild("Art") or Instance.new("Folder", ServerStorage)
	art.Name = "Art"
	local folders = {}
	for _, k in ipairs({ "Machines", "Props", "Meteors" }) do
		local f = art:FindFirstChild(k) or Instance.new("Folder", art)
		f.Name = k
		f:ClearAllChildren()
		folders[k] = f
	end
	local frontDir: Vector3? = nil
	local report = {}
	local built = {}
	for name, list in pairs(groups) do
		local reg = REG[name]
		local m = Instance.new("Model")
		m.Name = reg.id or name
		local parts = {}
		for _, e in ipairs(list) do
			local p = e.part
			p.Name = e.name
			p.Anchored = true
			p.CanCollide = false
			p.CanQuery = false
			p.CanTouch = false
			p.CastShadow = MAT[e.mat][1] ~= NEON
			p.Material = MAT[e.mat][1]
			p.Color = Color3.fromHex(MAT[e.mat][2])
			p.TextureID = ""
			if e.mat == "Ice" then
				p.Transparency = 0.15
				p:SetAttribute("BaseTransparency", 0.15)
			end
			for _, c in ipairs(p:GetChildren()) do
				if c:IsA("SurfaceAppearance") then c:Destroy() end
			end
			p:SetAttribute("Mat", e.mat)
			p.Parent = m
			table.insert(parts, p)
		end
		local a, b = bboxOf(parts)
		if reg.kind == "Meteors" then
			m.WorldPivot = CFrame.new((a + b) / 2)
		else
			m.WorldPivot = CFrame.new(Vector3.new((a.X + b.X) / 2, a.Y, (a.Z + b.Z) / 2))
		end
		m:ScaleTo(factor)
		if name == "Crusher" and m:FindFirstChild("Chute") then
			local d = m.Chute.Position - m:GetBoundingBox().Position
			d = Vector3.new(d.X, 0, d.Z)
			frontDir = math.abs(d.X) > math.abs(d.Z) and Vector3.new(math.sign(d.X), 0, 0) or Vector3.new(0, 0, math.sign(d.Z))
		end
		if reg.kind == "Machines" then m:SetAttribute("Machine", name) end
		m.Parent = folders[reg.kind]
		built[name] = m
		local _, sz = m:GetBoundingBox()
		table.insert(report, ("%s %d parts %.1fx%.1fx%.1f"):format(name, #parts, sz.X, sz.Y, sz.Z))
	end
	frontDir = frontDir or Vector3.new(0, 0, -1)
	for name, m in pairs(built) do
		if REG[name].kind ~= "Meteors" then
			local p = m.WorldPivot.Position
			m.WorldPivot = CFrame.lookAt(p, p + frontDir)
		end
	end
	-- the bellows nozzle must point at the smelter (model -X)
	local bel = built.Bellows
	if bel and bel:FindFirstChild("Nozzle") then
		local lx = bel.WorldPivot:PointToObjectSpace(bel.Nozzle.Position).X
		if lx > 0 then bel.WorldPivot = bel.WorldPivot * CFrame.Angles(0, math.pi, 0) end
	end
	for top in pairs(imported) do
		if top.Parent then top:Destroy() end
	end

	-- 4) dress plots
	local placed, pads, signs = 0, 0, 0
	local function dress(item: Instance, surface: CFrame)
		local reg = REG[item.Name]
		local t = folders.Machines:FindFirstChild(item.Name)
		if not t or not reg or not reg.spot then return end
		local old = item:FindFirstChild("Visual")
		if old then old:Destroy() end
		for _, d in ipairs(item:GetDescendants()) do
			if d:IsA("BasePart") then d.Transparency = 1 end
		end
		local v = t:Clone()
		v.Name = "Visual"
		v.Parent = item
		v:PivotTo(surface * CFrame.new(reg.spot))
		placed += 1
	end
	local stash = ServerStorage:FindFirstChild("PlotItems")
	for _, plot in ipairs(workspace.Map.Plots:GetChildren()) do
		local base = plot.Base
		local surface = base.CFrame * CFrame.new(0, base.Size.Y / 2, 0)
		for _, f in ipairs({ plot:FindFirstChild("Items"), stash and stash:FindFirstChild(plot.Name) }) do
			if f then
				for _, item in ipairs(f:GetChildren()) do dress(item, surface) end
			end
		end
		-- purchase pads: pad part stays as the touch trigger; PurchaseService toggles the Visual
		if built.Pad and plot:FindFirstChild("Pads") then
			for _, pad in ipairs(plot.Pads:GetChildren()) do
				if pad:IsA("BasePart") then
					local old = pad:FindFirstChild("Visual")
					if old then old:Destroy() end
					local shown = pad.Transparency < 1
					local v = built.Pad:Clone()
					v.Name = "Visual"
					v:PivotTo(CFrame.lookAt(pad.Position, pad.Position + surface.LookVector) * CFrame.new(0, -pad.Size.Y / 2, 0))
					v.Parent = pad
					local gui = pad:FindFirstChild("Label")
					if gui and gui:IsA("BillboardGui") then gui.StudsOffset = Vector3.new(0, 3.5, 0) end
					pad.Transparency = 1
					pad:SetAttribute("HasVisual", true)
					setVisible(v, shown)
					pads += 1
				end
			end
		end
		-- sign frame + posts (the Sign part stays as the text board)
		if built.Sign and plot:FindFirstChild("Sign") then
			local old = plot:FindFirstChild("SignVisual")
			if old then old:Destroy() end
			local v = built.Sign:Clone()
			v.Name = "SignVisual"
			local sp = surface:PointToObjectSpace(plot.Sign.Position)
			v:PivotTo(surface * CFrame.new(sp.X, 0, sp.Z))
			v.Parent = plot
			for _, n in ipairs({ "SignLegL", "SignLegR" }) do
				local l = plot:FindFirstChild(n)
				if l then l.Transparency = 1 end
			end
			signs += 1
		end
	end
	table.insert(report, ("scale x%.3f, front %s, items %d, pads %d, signs %d"):format(factor, tostring(frontDir), placed, pads, signs))
	return table.concat(report, "\n")
end
