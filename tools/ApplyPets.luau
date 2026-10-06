-- tools/ApplyPets: turns the imported Blender FBX (tools/blender/build_pets.py -> art/models/SF_Pets.fbx)
-- into templates.   require(game.ServerStorage.Tools.ApplyPets)()
-- Part names from Blender: <Model>__<Part>__<MatKey>. MatKey -> Roblox Material + Color (no baked textures).
--   Pet<Id>    -> ReplicatedStorage.Assets.PetMeshes.<Id>   (pivot = bottom centre, faces -Z, PrimaryPart "Body")
--   Egg<Name>  -> ReplicatedStorage.Assets.EggMeshes.<Name>Egg (RockEgg, EmberEgg, FrostEgg, CosmicEgg)
--   ForgeDrone, LaunchPad -> ServerStorage.Art.Gadgets      (GadgetService builds from these when present)
-- Import scale is normalised from the LaunchPad base, modelled exactly 9 studs wide.
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SP, NEON, SLATE, ICE = Enum.Material.SmoothPlastic, Enum.Material.Neon, Enum.Material.Slate, Enum.Material.Ice
local MAT = {
	-- shared with ApplyModels
	Red = { SP, "D95542" }, Cream = { SP, "FFF0CF" }, Steel = { SP, "344658" }, SteelLight = { SP, "6E7F93" },
	Dark = { SP, "1F2430" }, Yellow = { SP, "FFC83D" }, Glow = { NEON, "FF9A3C" }, Gold = { NEON, "FFD24A" },
	Teal = { NEON, "64DFD1" }, Green = { NEON, "50DC78" }, RockDark = { SLATE, "4A4652" }, Basalt = { Enum.Material.Basalt, "3B3540" },
	Lava = { NEON, "FF6A1E" }, IceRock = { SP, "9FC9E0" }, Ice = { ICE, "BDEBFF", 0.15 }, ChargedRock = { SP, "3E4A66" },
	Bolt = { NEON, "FFE14A" }, CosmicRock = { SP, "3A2A5E" }, CosmicGlow = { NEON, "B07CFF" },
	-- pets
	EyeBlack = { SP, "16131C" }, EyeShine = { NEON, "FFFFFF" }, Blush = { SP, "FF8FB0" }, White = { SP, "F4F6FF" },
	Pebble = { SLATE, "8C8597" }, PebbleDark = { SLATE, "5E5868" }, Rubble = { SLATE, "6E6585" }, EmberFur = { SP, "6A332C" },
	Flare = { SP, "FF8A2B" }, SunGold = { SP, "FFB13D" }, Snow = { SP, "DDEFFF" }, IceTeal = { ICE, "7FEAF2", 0.1 },
	Glacio = { SP, "6FA8D8" }, Aurora = { SP, "64DFD1", 0.15 }, Pink = { NEON, "FF4FD8" }, Void = { SP, "1F1A33" },
	Cyan = { NEON, "19F0F5" }, Whale = { SP, "2C3E8C" }, WhaleBelly = { SP, "9FB3F0" }, Celest = { SP, "FFD9F2" },
	Wing = { SP, "FFFFFF", 0.3 }, WingGold = { SP, "FFE9A0", 0.2 }, Orange = { SP, "FF9A3C" },
}
local EGG_ID = { EggRock = "RockEgg", EggEmber = "EmberEgg", EggFrost = "FrostEgg", EggCosmic = "CosmicEgg" }
local HOVER = { Glintmoth = 1.1, Flarefly = 1.3, Solarix = 1.2, Aurorabe = 1.0, Voidling = 1.1, Starwhale = 1.2, Celestia = 0.8 }
local PAD_WIDTH = 9

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

local function folder(parent: Instance, name: string): Folder
	local f = parent:FindFirstChild(name) or Instance.new("Folder")
	f.Name = name
	f.Parent = parent
	return f :: Folder
end

return function()
	-- 1) find imported mesh parts
	local groups, imported = {}, {}
	for _, d in ipairs(workspace:GetDescendants()) do
		if d:IsA("MeshPart") then
			local model, pname, mat = string.match(d.Name, "^(%w+)__(%w+)__(%w+)$")
			local known = model and (model:sub(1, 3) == "Pet" or EGG_ID[model] or model == "ForgeDrone" or model == "LaunchPad")
			if known and MAT[mat] then
				groups[model] = groups[model] or {}
				table.insert(groups[model], { part = d, name = pname, mat = mat })
				local top = d
				while top.Parent and top.Parent ~= workspace do top = top.Parent end
				imported[top] = true
			end
		end
	end
	assert(groups.LaunchPad and groups.PetPebblit, "No imported pets found. Import art/models/SF_Pets.fbx first (File > Import 3D).")

	-- 2) uniform scale from the launch pad base
	local factor = 1
	for _, e in ipairs(groups.LaunchPad) do
		if e.name == "Base" then
			local mn, mx = bboxOf({ e.part })
			factor = PAD_WIDTH / math.max(mx.X - mn.X, mx.Z - mn.Z)
		end
	end

	-- 3) front direction (all models share the import transform): Pebblit's eyes sit on its face
	local frontDir = Vector3.new(0, 0, -1)
	do
		local eyesP, all = {}, {}
		for _, e in ipairs(groups.PetPebblit) do
			table.insert(all, e.part)
			if e.name == "Eyes" then table.insert(eyesP, e.part) end
		end
		local a, b = bboxOf(all)
		local ea, eb = bboxOf(eyesP)
		local d = (ea + eb) / 2 - (a + b) / 2
		frontDir = math.abs(d.X) > math.abs(d.Z) and Vector3.new(math.sign(d.X), 0, 0) or Vector3.new(0, 0, math.sign(d.Z))
	end

	-- 4) templates
	local assets = folder(ReplicatedStorage, "Assets")
	local petF, eggF = folder(assets, "PetMeshes"), folder(assets, "EggMeshes")
	local gadF = folder(folder(ServerStorage, "Art"), "Gadgets")
	petF:ClearAllChildren()
	eggF:ClearAllChildren()
	gadF:ClearAllChildren()
	local report = {}
	for name, list in pairs(groups) do
		local m = Instance.new("Model")
		local parts = {}
		local rotor = 0
		for _, e in ipairs(list) do
			local p = e.part
			local spec = MAT[e.mat]
			p.Name = e.name
			if e.name:match("^Rotor%d") then
				p.Name = "Rotor"
				rotor += 1
			end
			p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
			p.Material = spec[1]
			p.Color = Color3.fromHex(spec[2])
			p.Transparency = spec[3] or 0
			p:SetAttribute("BaseTransparency", spec[3] or 0)
			p.CastShadow = spec[1] ~= NEON
			p.TextureID = ""
			for _, c in ipairs(p:GetChildren()) do
				if c:IsA("SurfaceAppearance") then c:Destroy() end
			end
			p:SetAttribute("Mat", e.mat)
			p.Parent = m
			table.insert(parts, p)
		end
		local a, b = bboxOf(parts)
		local bottom = Vector3.new((a.X + b.X) / 2, a.Y, (a.Z + b.Z) / 2)
		local centre = (a + b) / 2
		local pivotPos = (name == "ForgeDrone") and centre or bottom
		m.WorldPivot = CFrame.lookAt(pivotPos, pivotPos + frontDir)
		m:ScaleTo(factor)
		m.PrimaryPart = m:FindFirstChild("Body") or m:FindFirstChild("Shell") or m:FindFirstChild("Base") or parts[1]
		if name:sub(1, 3) == "Pet" then
			local id = name:sub(4)
			m.Name = id
			m:SetAttribute("Def", id)
			m:SetAttribute("Hover", HOVER[id] or 0)
			m.Parent = petF
		elseif EGG_ID[name] then
			m.Name = EGG_ID[name]
			m.Parent = eggF
		else
			m.Name = name
			m:SetAttribute("ItemId", name)
			m.Parent = gadF
		end
		m:PivotTo(CFrame.new(0, -200, 0)) -- park the templates out of sight (they live in storage anyway)
		local _, sz = m:GetBoundingBox()
		table.insert(report, ("%s %d parts %.1fx%.1fx%.1f"):format(m.Name, #parts, sz.X, sz.Y, sz.Z))
	end
	for top in pairs(imported) do
		if top.Parent then top:Destroy() end
	end
	table.sort(report)
	print("[ApplyPets] scale " .. string.format("%.3f", factor) .. " front " .. tostring(frontDir) .. "\n" .. table.concat(report, "\n"))
	return #report
end
