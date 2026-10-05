-- tools/ApplyMap: turns the imported SF_Map.fbx (Blender) into the visual map.
-- Usage (Edit mode, after File > Import 3D of art/models/SF_Map.fbx):
--   require(game.ServerStorage.Tools.ApplyMap)()
-- Visual meshes are anchored and non-colliding (CanQuery off so meteor raycasts still hit CraterFloor).
-- Gameplay collision stays on the greybox parts, which are made invisible here.

local Lighting = game:GetService("Lighting")

local S = Enum.Material.SmoothPlastic
local MAT = {
	Grass = { "79C94A", S }, GrassDark = { "5FA83B", S },
	Slate = { "687B91", S }, SlateDark = { "55657A", S },
	Floor = { "7A8293", S }, FloorDark = { "6A7180", S },
	Path = { "DB9856", S }, Cream = { "FFF0CF", S },
	Wood = { "C98A4E", S }, WoodDark = { "8A5A34", S },
	Leaf = { "6DBE45", S }, LeafDark = { "4E9E35", S },
	Rock = { "8C96A3", S }, Basalt = { "3B3540", S },
	Ember = { "FF6A1E", Enum.Material.Neon }, LampGlow = { "FFE08A", Enum.Material.Neon },
	Steel = { "344658", S }, FlowerY = { "FFD24A", S }, FlowerP = { "F27B9B", S },
	Red = { "D95542", S },
}

local MARKER_DIST = 175 -- Blender Marker0 (0,0,20) -> Marker1 (175,0,20)
local MARKER0_POS = Vector3.new(0, 20, 0)

local function findImport(): Model?
	for _, d in ipairs(workspace:GetDescendants()) do
		if d:IsA("BasePart") and d.Name:match("^Map__Marker0") then
			local m = d:FindFirstAncestorOfClass("Model")
			while m and m.Parent ~= workspace and m.Parent:IsA("Model") do
				m = m.Parent
			end
			return m
		end
	end
	return nil
end

local function setupLighting()
	pcall(function() Lighting.Technology = Enum.Technology.Future end)
	Lighting.ClockTime = 10.6
	Lighting.GeographicLatitude = 28
	Lighting.Brightness = 1.8
	Lighting.Ambient = Color3.fromRGB(80, 88, 105)
	Lighting.OutdoorAmbient = Color3.fromRGB(128, 136, 155)
	Lighting.EnvironmentDiffuseScale = 0.4
	Lighting.EnvironmentSpecularScale = 0.2
	Lighting.ShadowSoftness = 0.3
	local atm = Lighting:FindFirstChildOfClass("Atmosphere") or Instance.new("Atmosphere", Lighting)
	atm.Density = 0.28
	atm.Offset = 0.1
	atm.Color = Color3.fromRGB(198, 226, 248)
	atm.Decay = Color3.fromRGB(150, 185, 220)
	atm.Glare = 0.1
	atm.Haze = 0.6
	local bloom = Lighting:FindFirstChildOfClass("BloomEffect") or Instance.new("BloomEffect", Lighting)
	bloom.Intensity = 0.35
	bloom.Size = 24
	bloom.Threshold = 1.5
	local cc = Lighting:FindFirstChild("ToyGrade") or Instance.new("ColorCorrectionEffect")
	cc.Name = "ToyGrade"
	cc.Saturation = 0.12
	cc.Contrast = 0.12
	cc.Brightness = -0.02
	cc.Parent = Lighting
	local sky = Lighting:FindFirstChildOfClass("Sky")
	if sky then sky.CelestialBodiesShown = true end
end

local function invisible(p: Instance)
	if p:IsA("BasePart") then
		p.Transparency = 1
		p.CastShadow = false
	end
	for _, c in ipairs(p:GetChildren()) do
		if c:IsA("Decal") or c:IsA("Texture") then c.Transparency = 1 end
	end
end

local function collider(name, size, cf, parent, shape)
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.Size = size
	p.CFrame = cf
	p.Transparency = 1
	p.CastShadow = false
	if shape then p.Shape = shape end
	p.Parent = parent
	return p
end

return function()
	local src = findImport()
	assert(src, "ApplyMap: no imported model with Map__Marker0 found. Import art/models/SF_Map.fbx first.")
	local map = workspace:FindFirstChild("Map")
	assert(map, "ApplyMap: workspace.Map (greybox) missing")

	-- 1) collect visual meshes into one model
	local old = map:FindFirstChild("Visual")
	if old then old:Destroy() end
	local vis = Instance.new("Model")
	vis.Name = "Visual"
	local m0, m1
	local parts = {}
	for _, d in ipairs(src:GetDescendants()) do
		if d:IsA("BasePart") then
			if d.Name:match("^Map__Marker0") then m0 = d
			elseif d.Name:match("^Map__Marker1") then m1 = d
			else table.insert(parts, d) end
		end
	end
	assert(m0 and m1, "ApplyMap: markers missing")

	-- 2) frame from markers: X axis = Marker0->Marker1, Y = up
	local p0, p1 = m0.Position, m1.Position
	local dx = p1 - p0
	local flat = Vector3.new(dx.X, 0, dx.Z)
	local k = MARKER_DIST / dx.Magnitude
	local frame = CFrame.fromMatrix(p0, flat.Unit, Vector3.yAxis)

	-- detect an upside-down import: geometry should sit mostly BELOW Marker0 (y=20 over a 0..36 map)
	local below = 0
	for _, p in ipairs(parts) do
		if p.Position.Y < p0.Y then below += 1 end
	end
	if below < #parts / 2 then
		frame = CFrame.fromMatrix(p0, flat.Unit, -Vector3.yAxis)
	end

	local target = CFrame.new(MARKER0_POS)
	local unknown = {}
	for _, p in ipairs(parts) do
		local rel = frame:ToObjectSpace(p.CFrame)
		rel = CFrame.new(rel.Position * k) * rel.Rotation
		p.Size *= k
		p.CFrame = target * rel
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.CastShadow = true
		pcall(function() (p :: any).CollisionFidelity = Enum.CollisionFidelity.Box end)
		local _, name, key = p.Name:match("^(Map)__(.-)__(%w+)$")
		local spec = key and MAT[key]
		if spec then
			p.Color = Color3.fromHex(spec[1])
			p.Material = spec[2]
			if spec[2] == Enum.Material.Neon then p.CastShadow = false end
			for _, sa in ipairs(p:GetChildren()) do
				if sa:IsA("SurfaceAppearance") or sa:IsA("Texture") or sa:IsA("Decal") then sa:Destroy() end
			end
			pcall(function() (p :: any).TextureID = "" end)
		else
			table.insert(unknown, p.Name)
		end
		p:SetAttribute("Source", name)
		p.Parent = vis
	end
	vis.Parent = map
	src:Destroy()

	-- 3) greybox becomes invisible collision
	for _, d in ipairs(map.Rim:GetDescendants()) do invisible(d) end
	invisible(map.CraterFloor)
	for _, plot in ipairs(map.Plots:GetChildren()) do
		for _, n in ipairs({ "Base", "Ramp", "Walkway" }) do
			local p = plot:FindFirstChild(n)
			if p then invisible(p) end
		end
	end
	local lm = map:FindFirstChild("Landmarks")
	if lm then lm:Destroy() end

	-- 4) extra collision matching the Blender map
	local col = map:FindFirstChild("Collision") or Instance.new("Folder")
	col.Name = "Collision"
	col.Parent = map
	col:ClearAllChildren()
	-- central meteorite (r~11, squashed, centred y=5.5)
	collider("Meteorite", Vector3.new(19, 19, 19), CFrame.new(0, 3.5, 0), col, Enum.PartType.Ball)
	-- plateau extension: greybox grass ends at r=245, Blender grass runs to ~264
	local segs = 40
	for i = 0, segs - 1 do
		local a = (i + 0.5) / segs * math.pi * 2
		local w = 2 * math.pi * 280 / segs + 2
		local r = 245 + 12
		local pos = Vector3.new(math.cos(a) * r, 6.5, math.sin(a) * r)
		collider("PlateauExt", Vector3.new(w, 13, 24), CFrame.lookAt(pos, Vector3.new(0, 6.5, 0)), col)
		-- boundary wall just inside the outer mesas
		local wr = 268 + 3
		local wpos = Vector3.new(math.cos(a) * wr, 13 + 40, math.sin(a) * wr)
		collider("Boundary", Vector3.new(2 * math.pi * 275 / segs + 2, 80, 6), CFrame.lookAt(wpos, Vector3.new(0, 53, 0)), col)
	end
	-- old OuterCliff skyline sat at r=245..265; it is replaced by the boundary wall
	for _, c in ipairs(map.Rim:GetChildren()) do
		if c.Name == "OuterCliff" then c.CanCollide = false end
	end

	setupLighting()
	return string.format("ApplyMap: %d meshes, scale %.3f, flipped=%s, unknown=%s", #parts, k,
		tostring(below < #parts / 2), #unknown > 0 and table.concat(unknown, ",", 1, math.min(#unknown, 8)) or "none")
end
