-- tools/ApplyPets: turns the imported Blender FBX into templates.   require(game.ServerStorage.Tools.ApplyPets)()
--   art/models/SF_Pets_v2.fbx (tools/blender/build_pets_v2.py, T-04-02): 18 rigged pets, 5 rigged eggs, PetFuser, FuserRig
--   art/models/SF_Pets.fbx    (tools/blender/build_pets.py, v1): 16 pets, 4 eggs, ForgeDrone, LaunchPad  (still works)
-- Part names from Blender: <Model>__<Part>__<MatKey> (Part may contain "_", e.g. Shard_1). MatKey -> Roblox Material + Color.
--   Pet<Id>    -> ReplicatedStorage.Assets.PetMeshes.<Id>   (pivot = bottom centre, faces -Z, PrimaryPart "Body")
--   Egg<Name>  -> ReplicatedStorage.Assets.EggMeshes.<Name>Egg (RockEgg, EmberEgg, FrostEgg, CosmicEgg, CoreEgg)
--   ForgeDrone, LaunchPad -> ServerStorage.Art.Gadgets      (GadgetService builds from these when present)
--   PetFuser   -> ServerStorage.Art.Machines.PetFuser + every plot's Items.PetFuser.Visual (replaces the Tools.ApplyFuser
--                 part-built model; FusePrompt stays on Base, the Collider and other prompt/FX children are carried over,
--                 Visual keeps ItemId = PetFuser, Machine = PetFuser). Rigid parts Base, Orb1-3, Core, Chamber, Tip1-3.
--   FuserRig   -> ReplicatedStorage.Assets.FuserRig (rigged copy for the fusion reveal, plays Fuser_Fuse)
-- Rigs (v2): each rig's Bones are re-parented under the template's PrimaryPart and the template gets an
-- AnimationController + Animator, so Animator:LoadAnimation(<clip>) works on a clone (in a ViewportFrame use a WorldModel).
-- Import scale is normalised from the LaunchPad base (9 studs wide, v1) or the PetFuser base (7 studs wide, v2).
-- Only templates present in the import are replaced; everything else in the folders is left alone.
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SP, NEON, SLATE, ICE, GLASS = Enum.Material.SmoothPlastic, Enum.Material.Neon, Enum.Material.Slate, Enum.Material.Ice, Enum.Material.Glass
local MAT = {
	-- shared with ApplyModels
	Red = { SP, "D95542" }, Cream = { SP, "FFF0CF" }, Steel = { SP, "344658" }, SteelLight = { SP, "6E7F93" },
	Dark = { SP, "1F2430" }, Yellow = { SP, "FFC83D" }, Glow = { NEON, "FF9A3C" }, Gold = { NEON, "FFD24A" },
	Teal = { NEON, "64DFD1" }, Green = { NEON, "50DC78" }, RockDark = { SLATE, "4A4652" }, Basalt = { Enum.Material.Basalt, "3B3540" },
	Lava = { NEON, "FF6A1E" }, IceRock = { SP, "9FC9E0" }, Ice = { ICE, "BDEBFF", 0.15 }, ChargedRock = { SP, "3E4A66" },
	Bolt = { NEON, "FFE14A" }, CosmicRock = { SP, "3A2A5E" }, CosmicGlow = { NEON, "B07CFF" }, Ember = { NEON, "FF5A1E" },
	-- pets v1
	EyeBlack = { SP, "16131C" }, EyeShine = { NEON, "FFFFFF" }, Blush = { SP, "FF8FB0" }, White = { SP, "F4F6FF" },
	Pebble = { SLATE, "8C8597" }, PebbleDark = { SLATE, "5E5868" }, Rubble = { SLATE, "6E6585" }, EmberFur = { SP, "6A332C" },
	Flare = { SP, "FF8A2B" }, SunGold = { SP, "FFB13D" }, Snow = { SP, "DDEFFF" }, IceTeal = { ICE, "7FEAF2", 0.1 },
	Glacio = { SP, "6FA8D8" }, Aurora = { SP, "64DFD1", 0.15 }, Pink = { NEON, "FF4FD8" }, Void = { SP, "1F1A33" },
	Cyan = { NEON, "19F0F5" }, Whale = { SP, "2C3E8C" }, WhaleBelly = { SP, "9FB3F0" }, Celest = { SP, "FFD9F2" },
	Wing = { SP, "FFFFFF", 0.3 }, WingGold = { SP, "FFE9A0", 0.2 }, Orange = { SP, "FF9A3C" },
	-- pets v2 (T-04-02): hex codes from Astra's sheets (art/concepts/PETS), matte bodies, Neon only on the glowing accents
	PebBody = { SP, "8C8597" }, PebSpot = { SP, "5E5868" }, PebCrystal = { SP, "B9A8E0" },
	CinderBody = { SP, "4A3B44" }, CinderGlow = { NEON, "FF7A2A" }, RubBody = { SP, "6E6585" }, RubSpike = { SP, "C9B6A6" },
	KitBody = { SP, "5A2E2A" }, DarkRock = { SP, "3B3540" }, MawJaw = { SP, "6B6470" }, MawGlow = { NEON, "FFB13D" },
	GoldGlow = { NEON, "FFE21B" }, FrostCrystal = { SP, "BDEBFF" }, FrostGlow = { NEON, "BDEBFF" }, GlacioBeak = { SP, "3D5C8A" },
	AuroraBody = { SP, "64DFD1" }, Cloud = { SP, "FFE6F6" }, NebStar = { SP, "B07CFF" }, WhaleBelly2 = { SP, "4C64B8" },
	Magenta = { SP, "FF4FD8" }, CoreRed = { NEON, "FF3B1F" }, CoreArmor = { SP, "241E2C" }, Glass = { GLASS, "BDEFFF", 0.55 },
}
local EGG_ID = { EggRock = "RockEgg", EggEmber = "EmberEgg", EggFrost = "FrostEgg", EggCosmic = "CosmicEgg", EggCore = "CoreEgg" }
-- PetFollow hover height per pet. v2 sheets: Solarix and Celestia now stand on four / two legs, so they walk (0)
local HOVER = { Glintmoth = 1.1, Flarefly = 1.3, Solarix = 0, Aurorabe = 1.0, Voidling = 1.1, Starwhale = 1.2, Celestia = 0 }
local PAD_WIDTH, FUSER_WIDTH = 9, 7
local STATIC = { PetFuser = true, ForgeDrone = true, LaunchPad = true }

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

local function setVisible(model: Instance, visible: boolean)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("BasePart") then d.Transparency = visible and (d:GetAttribute("BaseTransparency") or 0) or 1 end
	end
end

local function replace(parent: Instance, m: Instance)
	local old = parent:FindFirstChild(m.Name)
	if old then old:Destroy() end
	m.Parent = parent
end

-- the PetFuser Visual on one plot item: same pivot as the old one, prompt/collider/FX carried over
local function dressFuser(item: Instance, template: Model, surface: CFrame?): boolean
	local old = item:FindFirstChild("Visual")
	local pivot: CFrame
	local hidden = false
	if old and old:IsA("Model") then
		local cf, size = old:GetBoundingBox()
		local yaw = surface and (surface - surface.Position) or (old:GetPivot() - old:GetPivot().Position)
		pivot = CFrame.new(cf.Position - Vector3.new(0, size.Y / 2, 0)) * yaw
		hidden = true
		for _, d in ipairs(old:GetDescendants()) do
			if d:IsA("BasePart") and d.Name ~= "Collider" and d.Transparency < 1 then
				hidden = false
				break
			end
		end
	elseif item:IsA("PVInstance") then
		pivot = (item :: PVInstance):GetPivot()
	else
		return false
	end
	local v = template:Clone()
	v.Name = "Visual"
	v:PivotTo(pivot)
	v.Parent = item
	if old then
		for k, val in pairs(old:GetAttributes()) do v:SetAttribute(k, val) end
		-- children of the old parts (prompt attachments, lights, emitters) move to the new part with the same name
		for _, op in ipairs(old:GetDescendants()) do
			if op:IsA("BasePart") and op.Name ~= "Collider" then
				local np = v:FindFirstChild(op.Name)
				if np then
					for _, ch in ipairs(op:GetChildren()) do
						if not (ch:IsA("DataModelMesh") or ch:IsA("SurfaceAppearance") or ch:IsA("JointInstance") or ch:IsA("WeldConstraint")) then
							ch.Parent = np
						end
					end
				end
			end
		end
		local col = old:FindFirstChild("Collider", true)
		if col then col.Parent = v end
		for _, ch in ipairs(old:GetChildren()) do -- loose non-part children of the old Visual (scripts, values, attachments)
			if not ch:IsA("BasePart") and not ch:IsA("Model") then ch.Parent = v end
		end
	end
	local prompt = (old and old:FindFirstChild("FusePrompt", true)) or item:FindFirstChild("FusePrompt", true)
	if prompt and not prompt:IsDescendantOf(v.Base) then prompt.Parent = v.Base end
	v:SetAttribute("ItemId", "PetFuser")
	v:SetAttribute("Machine", "PetFuser")
	if old then old:Destroy() end
	if hidden then setVisible(v, false) end
	return true
end

return function()
	-- 1) find imported mesh parts
	local groups, imported = {}, {}
	for _, d in ipairs(workspace:GetDescendants()) do
		if d:IsA("MeshPart") then
			local model, pname, mat = string.match(d.Name, "^(%w+)__(.-)__(%w+)$")
			local known = model and (model:sub(1, 3) == "Pet" or EGG_ID[model] or STATIC[model] or model == "FuserRig")
			if known and MAT[mat] then
				groups[model] = groups[model] or {}
				table.insert(groups[model], { part = d, name = pname, mat = mat })
				local top = d
				while top.Parent and top.Parent ~= workspace do top = top.Parent end
				imported[top] = true
			end
		end
	end
	assert(groups.PetPebblit and (groups.LaunchPad or groups.PetFuser),
		"No imported pets found. Import art/models/SF_Pets_v2.fbx (or SF_Pets.fbx) first (File > Import 3D).")

	-- 2) uniform scale from the launch pad base (v1) or the fuser base (v2)
	local factor = 1
	local ref, refWidth = groups.LaunchPad or groups.PetFuser, groups.LaunchPad and PAD_WIDTH or FUSER_WIDTH
	for _, e in ipairs(ref) do
		if e.name == "Base" then
			local mn, mx = bboxOf({ e.part })
			factor = refWidth / math.max(mx.X - mn.X, mx.Z - mn.Z)
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

	-- 4) rig root bones (v2). The importer may parent them anywhere, so each rig's "Root" bone is matched to the
	-- model whose bottom centre it sits on (every rig's Root is modelled exactly at its pivot).
	local rootBones = {}
	for top in pairs(imported) do
		for _, b in ipairs(top:GetDescendants()) do
			if b:IsA("Bone") and not (b.Parent and b.Parent:IsA("Bone")) then table.insert(rootBones, b) end
		end
	end
	local boneOf = {}
	for name, list in pairs(groups) do
		if not STATIC[name] and #rootBones > 0 then
			local parts = {}
			for _, e in ipairs(list) do table.insert(parts, e.part) end
			local a, b = bboxOf(parts)
			local bottom = Vector3.new((a.X + b.X) / 2, a.Y, (a.Z + b.Z) / 2)
			local best, bestD = nil, math.huge
			for _, rb in ipairs(rootBones) do
				local dd = (rb.WorldPosition - bottom).Magnitude
				if dd < bestD then best, bestD = rb, dd end
			end
			if best and bestD < 2 / factor then boneOf[name] = best end -- rigs are laid out >= 5 studs apart in the FBX
		end
	end

	-- 5) templates
	local assets = folder(ReplicatedStorage, "Assets")
	local petF, eggF = folder(assets, "PetMeshes"), folder(assets, "EggMeshes")
	local art = folder(ServerStorage, "Art")
	local gadF, macF = folder(art, "Gadgets"), folder(art, "Machines")
	local report, rigs = {}, 0
	local fuserTemplate: Model? = nil
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
			p.CastShadow = spec[1] ~= NEON and spec[1] ~= GLASS
			p.TextureID = ""
			for _, c in ipairs(p:GetChildren()) do
				if c:IsA("SurfaceAppearance") then c:Destroy() end
			end
			p:SetAttribute("Mat", e.mat)
			p.Parent = m
			table.insert(parts, p)
		end
		local primary = m:FindFirstChild("Body") or m:FindFirstChild("ShellBottom") or m:FindFirstChild("Shell") or m:FindFirstChild("Base") or parts[1]
		local rb = boneOf[name]
		if rb then -- keep the bone where it is in the world, now owned by this template
			local world = rb.WorldCFrame
			rb.Parent = primary
			rb.CFrame = (primary :: BasePart).CFrame:Inverse() * world
			local ac = Instance.new("AnimationController")
			Instance.new("Animator").Parent = ac
			ac.Parent = m
			m:SetAttribute("Rig", true)
			rigs += 1
		end
		local a, b = bboxOf(parts)
		local bottom = Vector3.new((a.X + b.X) / 2, a.Y, (a.Z + b.Z) / 2)
		local centre = (a + b) / 2
		local pivotPos = (name == "ForgeDrone") and centre or bottom
		m.PrimaryPart = primary
		primary.PivotOffset = primary.CFrame:ToObjectSpace(CFrame.lookAt(pivotPos, pivotPos + frontDir))
		m:ScaleTo(factor)
		if name:sub(1, 3) == "Pet" and name ~= "PetFuser" then
			local id = name:sub(4)
			m.Name = id
			m:SetAttribute("Def", id)
			m:SetAttribute("Hover", HOVER[id] or 0)
			replace(petF, m)
		elseif EGG_ID[name] then
			m.Name = EGG_ID[name]
			replace(eggF, m)
		elseif name == "PetFuser" then
			m.Name = "PetFuser"
			m:SetAttribute("ItemId", "PetFuser")
			m:SetAttribute("Machine", "PetFuser")
			replace(macF, m)
			fuserTemplate = m
		elseif name == "FuserRig" then
			m.Name = "FuserRig"
			replace(assets, m)
		else
			m.Name = name
			m:SetAttribute("ItemId", name)
			replace(gadF, m)
		end
		m:PivotTo(CFrame.new(0, -200, 0)) -- park the templates out of sight (they live in storage anyway)
		local _, sz = m:GetBoundingBox()
		table.insert(report, ("%s %d parts %.1fx%.1fx%.1f%s"):format(m.Name, #parts, sz.X, sz.Y, sz.Z, rb and " rig" or ""))
	end
	for top in pairs(imported) do
		if top.Parent then top:Destroy() end
	end

	-- 6) Pet Fuser on every plot (placed or still in the purchase stash)
	local fusers = 0
	if fuserTemplate then
		local stash = ServerStorage:FindFirstChild("PlotItems")
		local plots = workspace:FindFirstChild("Map") and workspace.Map:FindFirstChild("Plots")
		for _, plot in ipairs(plots and plots:GetChildren() or {}) do
			local base = plot:FindFirstChild("Base")
			-- plot-local -Z faces the crater (same convention as ApplyModels / every other plot machine)
			local surface = base and base:IsA("BasePart") and base.CFrame * CFrame.new(0, base.Size.Y / 2, 0) or nil
			for _, f in ipairs({ plot:FindFirstChild("Items"), stash and stash:FindFirstChild(plot.Name) }) do
				local item = f and f:FindFirstChild("PetFuser")
				if item and dressFuser(item, fuserTemplate, surface) then fusers += 1 end
			end
		end
	end
	table.sort(report)
	local msg = ("[ApplyPets] scale %.3f front %s, %d rigs, %d plot fusers"):format(factor, tostring(frontDir), rigs, fusers)
	if math.abs(factor - 1) > 0.02 then
		msg ..= "\n  NOTE: import scale is not 1 stud per Blender unit. Static models are fixed by ScaleTo; if imported clips look too big/small, re-import with the 3D Importer's scale unit set so this reads 1.000"
	end
	print(msg .. "\n" .. table.concat(report, "\n"))
	return #report
end
