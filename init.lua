-- christmas_view: a purely cosmetic, temporary Christmas mod.
--
-- It only changes how already existing nodes, items and mobs LOOK.
-- Nothing is registered and nothing is written into the map, node meta,
-- inventories or mob staticdata, so after the event the mod folder can simply
-- be deleted and everything returns to the normal look.
--
--   all chests        -> gifts of different colours
--   doors             -> a Christmas wreath on them
--   pine needles      -> decorated with blinking garlands and baubles
--   apples            -> apples made of ice
--   fences            -> a palisade of candy canes (gates and rails striped)
--   torches           -> glowing Christmas tree ornaments
--   smartshops        -> a blinking garland instead of the border
--   player bones      -> snowmen
--   every helmet      -> a Santa hat on top
--   sheep             -> a red cape with white fur and a Santa hat
--   unified_inventory -> falling snow, snow drifts with snowmen, gifts, candy
--                        canes and gingerbread men, a glowing garland around

local modname = minetest.get_current_modname()
local P = modname .. "_"

local function override(name, def)
	if minetest.registered_items[name] then
		minetest.override_item(name, def)
	end
end

-- Calls fn on every texture string of a tiles list, returns a new list.
local function map_tiles(tiles, fn)
	if not tiles then
		return nil
	end
	local out = {}
	for i, tile in ipairs(tiles) do
		if type(tile) == "string" then
			out[i] = fn(tile)
		elseif type(tile) == "table" and not tile.animation then
			local t = table.copy(tile)
			if t.name then
				t.name = fn(t.name)
			elseif t.image then
				t.image = fn(t.image)
			end
			out[i] = t
		else
			out[i] = tile
		end
	end
	return out
end

local function overlay_fn(overlay)
	return function(tex)
		return "(" .. tex .. ")^" .. overlay
	end
end

-- Keeps the tile options (backface_culling etc.) of old, but with a new texture.
local function retile(old, tex)
	if type(old) == "table" then
		local t = table.copy(old)
		t.name, t.image, t.animation = tex, nil, nil
		return t
	end
	return tex
end

local badged = {}

local function badge(name, tex)
	local def = minetest.registered_items[name]
	if badged[name] or not def then
		return
	end
	badged[name] = true
	if def.inventory_image and def.inventory_image ~= "" then
		override(name, {
			inventory_image = "(" .. def.inventory_image .. ")^" .. tex,
			wield_image = def.wield_image ~= "" and
				"(" .. def.wield_image .. ")^" .. tex or nil,
		})
	end
end

---------------------------------------------------------------- ice apples

local function apples()
	local def = minetest.registered_nodes["default:apple"]
	if not def then
		return
	end
	local tex = P .. "apple.png"
	local tiles = map_tiles(def.tiles, function() return tex end)
	if def.drawtype == "nodebox" then
		-- the 3D apple of riesenpilz: top, bottom and side tiles
		tiles = {P .. "apple_top.png", P .. "apple_bottom.png", P .. "apple_side.png"}
	end
	override("default:apple", {
		tiles = tiles,
		inventory_image = tex,
		wield_image = tex,
	})
end

---------------------------------------------------------------- torches

local ball = {
	name = P .. "ornament_ball.png",
	backface_culling = true,
	animation = {type = "vertical_frames", aspect_w = 32, aspect_h = 32, length = 1.6},
}
local cap = {name = P .. "ornament_cap.png", backface_culling = true}
local str = {name = P .. "ornament_string.png", backface_culling = false}

local function torches()
	-- a glass ball of 7/16 node; the meshes keep the placement logic
	-- (floor / wall / ceiling) of default untouched
	override("default:torch", {
		mesh = P .. "ornament_floor.obj",
		tiles = {ball, cap, str},
		inventory_image = P .. "ornament_inv.png",
		wield_image = P .. "ornament_inv.png",
		selection_box = {
			type = "wallmounted",
			wall_bottom = {-4/16, -1/2, -4/16, 4/16, 1.5/16, 4/16},
		},
	})
	override("default:torch_wall", {
		mesh = P .. "ornament_wall.obj",
		tiles = {ball, cap, str},
		selection_box = {
			type = "wallmounted",
			wall_side = {-1/2, -6.5/16, -4/16, 0.5/16, 5/16, 4/16},
		},
	})
	override("default:torch_ceiling", {
		mesh = P .. "ornament_ceiling.obj",
		tiles = {ball, cap, str},
		selection_box = {
			type = "wallmounted",
			wall_top = {-4/16, -5.5/16, -4/16, 4/16, 1/2, 4/16},
		},
	})
end

---------------------------------------------------------------- chests -> gifts

-- {paper colour, ribbon colour}
local C = {
	red = {"#c8102e", "#f2c43b"},
	green = {"#1f8a3b", "#e8343a"},
	blue = {"#2058c0", "#e8eef8"},
	gold = {"#e7b53c", "#d2232a"},
	purple = {"#7b2fbf", "#f2c43b"},
	silver = {"#b9c2cc", "#d2232a"},
	white = {"#f4f4f4", "#d2232a"},
	orange = {"#e8792a", "#2e9b40"},
	cyan = {"#1ba3b8", "#ffffff"},
	pink = {"#e85a9b", "#ffffff"},
	black = {"#34343a", "#f2c43b"},
	teal = {"#138a7e", "#f2c43b"},
	brown = {"#8a5a2b", "#f2c43b"},
	yellow = {"#f0d43a", "#d2232a"},
	lime = {"#7cc242", "#d2232a"},
	darkblue = {"#24398a", "#f2c43b"},
	magenta = {"#c2309b", "#f2c43b"},
	grey = {"#7d8590", "#e8343a"},
	violet = {"#8f4fd6", "#ffffff"},
	dark_green = {"#14532d", "#f2c43b"},
}
local fallback_colors = {"red", "green", "blue", "gold", "purple", "orange", "cyan",
	"pink", "teal", "lime", "magenta", "violet"}

local by_name = {
	["default:chest"] = "red",
	["default:chest_locked"] = "green",
	["protector:chest"] = "blue",
	["digilines:chest"] = "cyan",
	["simple_loots:loot_chest"] = "pink",
	["simple_loots:loot_chest_ocean"] = "teal",
	["x_obsidianmese:chest"] = "black",
	["xdecor:enderchest"] = "violet",
	["caverealms:s_chest"] = "darkblue",
	["treasure_chest:treasure_chest"] = "gold",
	["signs_bot:chest"] = "lime",
	["tubelib_addons1:chest"] = "yellow",
	["tubelib_addons3:chest"] = "orange",
	["tubelib_addons3:pushing_chest"] = "magenta",
	["tubelib_addons3:pushing_chest_defect"] = "grey",
}
local technic_metal = {
	iron = "silver", copper = "orange", silver = "white", gold = "gold", mithril = "purple",
}
-- technic gold chests carry a colour label: the gift takes that colour
local label_color = {
	black = "black", blue = "blue", brown = "brown", cyan = "cyan",
	dark_green = "dark_green", dark_grey = "grey", green = "green", grey = "silver",
	magenta = "magenta", orange = "orange", pink = "pink", red = "red",
	violet = "violet", white = "white", yellow = "yellow",
}

local function hash(s)
	local h = 0
	for i = 1, #s do
		h = (h * 31 + s:byte(i)) % 2147483647
	end
	return h
end

local function chest_color(name)
	-- the item of a chest picked up with the technic wrench looks like the chest
	local inner = name:match("^wrench:picked_up_(.+)$")
	if inner then
		name = inner:gsub("_", ":", 1)
	end
	name = name:gsub("_open$", "")
	if by_name[name] then
		return C[by_name[name]]
	end
	local metal, rest = name:match("^technic:(%a+)_locked_chest_?(.*)$")
	if not metal then
		metal, rest = name:match("^technic:(%a+)_chest_?(.*)$")
	end
	if metal then
		return C[label_color[rest] or technic_metal[metal] or "gold"]
	end
	if name:find("^techage:") then
		if name:find("ta2") then return C.brown end
		if name:find("ta3") then return C.darkblue end
		if name:find("ta5") then return C.violet end
		if name:find("ta4") then return C.teal end
	end
	return C[fallback_colors[hash(name) % #fallback_colors + 1]]
end

local function paper(color, variant)
	return "(" .. P .. "gift_paper" .. (variant or "") .. ".png^[multiply:" .. color[1] ..
		")^" .. P .. "gift_pattern.png"
end

local function ribbon(color, part)
	return "^(" .. P .. "gift_" .. part .. ".png^[multiply:" .. color[2] .. ")"
end

local function gift_tiles(color, badge_tex)
	local side = paper(color) .. ribbon(color, "ribbon_side")
	return {
		top = paper(color) .. ribbon(color, "ribbon_top"),
		bottom = paper(color) .. ribbon(color, "ribbon_bottom"),
		side = side,
		front = badge_tex and side .. "^" .. badge_tex or side,
		inside = P .. "gift_inside.png",
	}
end

-- halves of the big chest of connected_chests: the ribbon and the bow are on
-- the seam between the two nodes ("l" = the half with the seam on its right)
local function big_half(color, part, half)
	return paper(color, "_" .. half) .. ribbon(color, "big_" .. part .. "_" .. half)
end

local function is_chest(name, def)
	local item = name:match(":(.+)$") or ""
	if not item:find("chest") or item:find("cart") or item:find("dummy") then
		return false
	end
	if def.drawtype == "normal" or def.drawtype == nil then
		return true
	end
	return def.drawtype == "mesh" and
		(def.mesh == "chest_open.obj" or def.mesh == "connected_chest_open.obj")
end

local function lock_badge(name, def)
	if name:find("protector") then
		return P .. "gift_tag.png"
	end
	if name:find("locked") then
		return P .. "gift_lock.png"
	end
	return nil
end

local function connected_chest(name, def, color, locked)
	local side = paper(color) .. ribbon(color, "ribbon_side")
	local right = name:find("_connected_right") ~= nil
	local open = name:find("_open$") ~= nil
	local t = def.tiles
	local seam, other = right and "r" or "l", right and "l" or "r"
	local top = big_half(color, "top", seam)
	local bottom = big_half(color, "bottom", seam)
	local front = big_half(color, "side", seam)
	if locked then
		front = front .. "^" .. P .. "gift_big_lock_" .. seam .. ".png"
	end
	local back = big_half(color, "side", other)
	if open then
		local inside = P .. "gift_inside_big.png" .. (right and "^[transformFX" or "")
		return {retile(t[1], top), retile(t[2], P .. "gift_inside.png"), retile(t[3], side),
			retile(t[4], side), retile(t[5], front), retile(t[6], inside)}
	end
	if right then
		return {top, bottom, side, t[4], back, front}
	end
	return {top, bottom, t[3], side, back, front}
end

local function chests()
	for name, def in pairs(minetest.registered_nodes) do
		if is_chest(name, def) and def.tiles then
			local color = chest_color(name:gsub("_connected_[lr]%a+", ""))
			local lock = lock_badge(name, def)
			local tiles
			if name:find("_connected_[lr]") then
				tiles = connected_chest(name, def, color, lock ~= nil)
			elseif def.drawtype == "mesh" then
				-- open chest (chest_open.obj): lid top, lid bottom, sides, front, inside
				local g = gift_tiles(color, lock)
				local t = def.tiles
				tiles = {retile(t[1], g.top), retile(t[2], g.inside), retile(t[3], g.side),
					retile(t[4], g.side), retile(t[5], g.front), retile(t[6], g.inside)}
			else
				local g = gift_tiles(color, lock)
				tiles = {g.top, g.bottom, g.side, g.side, g.side, g.front}
			end
			override(name, {tiles = tiles})
		end
	end
end

---------------------------------------------------------------- doors

local function overlay_base(tiles, base, overlay)
	return map_tiles(tiles, function(tex)
		if type(base) ~= "string" or tex:sub(1, #base) ~= base then
			return tex
		end
		return "(" .. base .. "^" .. overlay .. ")" .. tex:sub(#base + 1)
	end)
end

local function doors_wreath()
	local wreath = overlay_fn(P .. "door_wreath.png")
	for name, def in pairs(minetest.registered_nodes) do
		-- doors of the doors API (also cb_blocks, ethereal, xpanes ...): one
		-- texture in the 38x32 door_a/door_b layout
		if (def.mesh == "door_a.b3d" or def.mesh == "door_b.b3d") and def.tiles then
			override(name, {tiles = map_tiles(def.tiles, wreath)})
			badge((name:gsub("_[abcd]$", "")), P .. "badge_wreath.png")
		end
		-- protector doors: two nodes (_b_* bottom, _t_* top); the 5th and 6th
		-- tiles are the front and back faces, the wreath goes on the top half
		local door, half = name:match("^(protector:door_[%w_]-)_([bt])_[12]$")
		local t = def.tiles
		if door and def.drawtype == "nodebox" and t and #t == 6
				and type(t[5]) == "string" and type(t[6]) == "string" then
			badge(door, P .. "badge_wreath.png")
			if half == "t" then
				local base = #t[5] <= #t[6] and t[5] or t[6]
				if t[5]:sub(1, #base) == base and t[6]:sub(1, #base) == base then
					override(name, {tiles = overlay_base(t, base, P .. "door_wreath_top.png")})
				end
			end
		end
	end
end

---------------------------------------------------------------- fences

-- Boxes in 1/16 node. A connection is drawn for the +X side and turned for
-- the others: two rails and one more candy cane in the middle (a palisade).
local function b(x1, y1, z1, x2, y2, z2)
	return {x1 / 16, y1 / 16, z1 / 16, x2 / 16, y2 / 16, z2 / 16}
end

local post = {
	b(-1.5, -8, -1.5, 1.5, 5.5, 1.5),  -- shaft
	b(-1.5, 5.5, -1.5, 5.5, 8, 1.5),   -- hook, top
	b(3, 2.5, -1.5, 5.5, 5.5, 1.5),    -- hook, end
}
local conn_right = {
	b(1.5, 2.5, -0.75, 8, 4, 0.75),    -- rails
	b(1.5, -4.5, -0.75, 8, -3, 0.75),
	b(4.5, -8, -1, 6.5, 4.5, 1),       -- small cane
	b(4.5, 4.5, -1, 8.5, 6.5, 1),
	b(7, 2.5, -1, 8.5, 4.5, 1),
}

local function turn(boxes, k)
	local out = {}
	for i, bx in ipairs(boxes) do
		local x1, z1, x2, z2 = bx[1], bx[3], bx[4], bx[6]
		for _ = 1, k do -- +X -> +Z -> -X -> -Z
			x1, z1, x2, z2 = -z2, x1, -z1, x2
		end
		out[i] = {math.min(x1, x2), bx[2], math.min(z1, z2), math.max(x1, x2), bx[5],
			math.max(z1, z2)}
	end
	return out
end

local candy_box = {
	type = "connected",
	fixed = post,
	connect_right = conn_right,
	connect_back = turn(conn_right, 1),
	connect_left = turn(conn_right, 2),
	connect_front = turn(conn_right, 3),
}

local function fences()
	local candy = P .. "candy.png"
	for name, def in pairs(minetest.registered_nodes) do
		local g = def.groups or {}
		local is_fence = (g.fence or 0) > 0 or def.drawtype == "fencelike"
		if is_fence and def.tiles then
			local tiles = map_tiles(def.tiles, function() return candy end)
			if def.drawtype == "nodebox" and def.node_box and def.node_box.type == "connected" then
				local new = {tiles = tiles}
				if name:find("rail") then
					new.inventory_image = P .. "fence_rail_inv.png"
				else
					-- only the drawn shape changes: walking and pointing use
					-- the original boxes of the fence
					new.node_box = candy_box
					new.collision_box = def.collision_box or def.node_box
					new.selection_box = def.selection_box or def.node_box
					new.inventory_image = P .. "fence_inv.png"
				end
				new.wield_image = new.inventory_image
				override(name, new)
			elseif def.drawtype == "mesh" or def.drawtype == "fencelike" then
				-- fence gates: the same shape, striped
				override(name, {tiles = tiles})
			end
		end
	end
end

---------------------------------------------------------------- pine trees

local function pine_trees()
	for _, name in ipairs({"default:pine_needles"}) do
		local def = minetest.registered_nodes[name]
		local tile = def and def.tiles and def.tiles[1]
		if type(tile) == "table" then
			tile = not tile.animation and (tile.name or tile.image)
		end
		if type(tile) == "string" then
			-- 4 frames of the needles with the garland on top; the needles are
			-- scaled to 64x64 so texture packs with big textures also work
			local esc = tile:gsub("[\\^:]", "\\%0")
			local frame = esc .. "\\^[resize\\:64x64"
			local strip = "[combine:64x256:0,0=" .. frame .. ":0,64=" .. frame ..
				":0,128=" .. frame .. ":0,192=" .. frame ..
				"^" .. P .. "garland_needles.png"
			local new = {
				tiles = {{name = strip, animation = {type = "vertical_frames",
					aspect_w = 64, aspect_h = 64, length = 2.4}}},
			}
			if def.inventory_image and def.inventory_image ~= "" then
				new.inventory_image = "(" .. def.inventory_image .. ")^" ..
					P .. "garland_needles_inv.png"
				new.wield_image = new.inventory_image
			end
			override(name, new)
		end
	end
end

---------------------------------------------------------------- smartshop

-- The border of the shop is replaced by a blinking garland. The wire keeps the
-- status colour of the shop (full, empty, used, admin, storage needs refill ...).
local shop_wire = {
	["smartshop:shop"] = "#2f7a35",
	["smartshop:shop_full"] = "#b050d0",
	["smartshop:shop_empty"] = "#e83a3a",
	["smartshop:shop_used"] = "#70e070",
	["smartshop:shop_admin"] = "#40d8f0",
	["smartshop:storage"] = "#2f7a35",
	["smartshop:storage_lacks_refill"] = "#e83a3a",
	["smartshop:storage_has_send"] = "#70e070",
}

local function smartshop()
	local frame = "smartshop_face.png\\^[colorize\\:#FFFFFF77\\^[resize\\:32x32"
	local face = "[combine:32x128:0,0=" .. frame .. ":0,32=" .. frame ..
		":0,64=" .. frame .. ":0,96=" .. frame
	for name, color in pairs(shop_wire) do
		local strip = face .. "^(" .. P .. "shop_wire.png^[multiply:" .. color .. ")^" ..
			P .. "shop_bulbs.png"
		override(name, {
			tiles = {{name = strip, animation = {type = "vertical_frames",
				aspect_w = 32, aspect_h = 32, length = 2.0}}},
		})
	end
end

---------------------------------------------------------------- bones

-- Player bones become a snowman. Collision and selection stay a full block.
local function bones()
	local name = "bones:bones"
	if not minetest.registered_nodes[name] then
		return
	end
	local full = {type = "fixed", fixed = {-0.5, -0.5, -0.5, 0.5, 0.5, 0.5}}
	local function bx(x1, y1, z1, x2, y2, z2)
		return {x1 / 16, y1 / 16, z1 / 16, x2 / 16, y2 / 16, z2 / 16}
	end
	override(name, {
		drawtype = "nodebox",
		paramtype = "light",
		node_box = {type = "fixed", fixed = {
			bx(-5, -8, -5, 5, -2, 5),          -- bottom ball
			bx(-4, -2, -4, 4, 1.5, 4),         -- middle
			bx(-3.5, 1.5, -3.5, 3.5, 2.5, 3.5), -- scarf
			bx(-3, 2.5, -3, 3, 6, 3),          -- head
			bx(-3.5, 6, -3.5, 3.5, 6.5, 3.5),  -- hat brim
			bx(-2.5, 6.5, -2.5, 2.5, 8, 2.5),  -- hat crown
			bx(-0.5, 3.5, -5.5, 0.5, 4.5, -3), -- carrot nose
			bx(-8, 0, -0.5, 8, 1, 0.5),        -- stick arms
		}},
		collision_box = full,
		selection_box = full,
		tiles = {
			P .. "bones_top.png", P .. "bones_bottom.png",
			P .. "bones_side.png", P .. "bones_side.png",
			P .. "bones_back.png", P .. "bones_front.png",
		},
	})
end

---------------------------------------------------------------- helmets

local function helmets()
	for name, def in pairs(minetest.registered_tools) do
		local g = def.groups or {}
		if (g.armor_head or 0) > 0 then
			-- same fallbacks as 3d_armor uses (api.lua: armor:set_player_armor)
			local tex = (def.texture or name:gsub(":", "_")):gsub("%.png$", "")
			local prev = (def.preview or tex .. "_preview"):gsub("%.png$", "")
			local inv = def.inventory_image
			override(name, {
				texture = tex .. ".png^" .. P .. "hat_head.png",
				preview = prev .. ".png^" .. P .. "hat_preview.png",
				inventory_image = inv and inv ~= "" and
					"(" .. inv .. ")^" .. P .. "hat_badge.png" or nil,
			})
		end
	end
end

---------------------------------------------------------------- sheep

-- survival_shelter runs an older mobs_animal with a different sheep model
-- (and a separate model for shaved sheep), it needs its own overlays
local function old_sheep_model()
	local mp = minetest.get_modpath("mobs_animal")
	if not mp then
		return false
	end
	local f = io.open(mp .. "/models/mobs_sheep_shaved.b3d", "rb")
	if f then
		f:close()
		return true
	end
	return false
end

-- The cape and the hat are an overlay on the texture of the live object only.
-- The mob's own fields (base_texture etc.) are not touched, so nothing
-- Christmas-related ends up in the saved staticdata.
local function sheep()
	local old_model = old_sheep_model()
	local timers = setmetatable({}, {__mode = "k"})

	local function overlay(props, tex)
		if old_model then
			if props.mesh == "mobs_sheep_shaved.b3d" then
				return P .. "sheep_old_shaved.png"
			end
			return P .. "sheep_old.png"
		end
		if tex:find("mobs_sheep_shaved.png", 1, true) then
			return P .. "sheep_shaved.png"
		end
		return P .. "sheep.png"
	end

	local function apply(self)
		local props = self.object:get_properties()
		local tex = props and props.textures and props.textures[1]
		if type(tex) ~= "string" or tex == "" then
			return
		end
		local suffix = "^" .. overlay(props, tex)
		if tex:sub(-#suffix) ~= suffix then
			-- a different overlay (sheep got shaved etc.) is removed first
			tex = tex:gsub("%^" .. P .. "sheep[%w_]*%.png$", "")
			self.object:set_properties({textures = {tex .. suffix}})
		end
	end

	for name, def in pairs(minetest.registered_entities) do
		if name:find("^mobs_animal:sheep_") then
			local on_activate = def.on_activate
			local on_step = def.on_step
			def.on_activate = function(self, staticdata, dtime)
				if on_activate then
					on_activate(self, staticdata, dtime)
				end
				if self.object:get_pos() then
					apply(self)
				end
			end
			-- mobs_animal resets the texture on shearing, dyeing, regrowing
			-- wool etc., so it is checked again from time to time
			def.on_step = function(self, dtime, moveresult)
				if on_step then
					on_step(self, dtime, moveresult)
				end
				local t = (timers[self] or 0) + dtime
				if t >= 0.5 then
					t = 0
					if self.object:get_pos() then
						apply(self)
					end
				end
				timers[self] = t
			end
		end
	end
end

---------------------------------------------------------------- unified_inventory

local F = minetest.formspec_escape
local ground_h = 0.9

local drift_items = {
	{"ui_snowman.png", 16, 21},
	{"ui_gift_red.png", 14, 15},
	{"ui_cane.png", 12, 24},
	{"ui_ginger.png", 12, 16},
	{"ui_gift_green.png", 12, 17},
	{"ui_snowman.png", 16, 21},
	{"ui_gift_blue.png", 16, 14},
	{"ui_ginger.png", 12, 16},
	{"ui_cane_flip.png", 12, 24},
	{"ui_gift_red.png", 14, 15},
	{"ui_snowman.png", 16, 21},
	{"ui_gift_green.png", 12, 17},
}
local drift_gaps = {0.5, 0.25, 0.7, 0.35, 0.9, 0.3, 0.55, 0.2, 0.8, 0.45, 0.6}

-- garland strips are drawn for the exact window sizes of the servers; for
-- any other size the closest one is stretched
local garland_w = {1775, 1400}
local garland_h = {1225, 1250, 975}

local function closest(list, v)
	local best
	for _, x in ipairs(list) do
		if not best or math.abs(x - v) < math.abs(best - v) then
			best = x
		end
	end
	return best
end

-- Builds the decoration for one unified_inventory layout (full or lite).
-- Everything is drawn right after the standard background, so it is under
-- the slots, buttons and text of the inventory.
local function ui_decor(style)
	local W, H = style.formw, style.formh
	local FH = H + ground_h
	local s = style.is_lite_mode and 0.8 or 1
	local out = {}

	local function bg(x, y, w, h, tex)
		out[#out + 1] = ("background[%.3f,%.3f;%.3f,%.3f;%s;false]"):format(x, y, w, h, F(P .. tex))
	end

	-- falling snow: a grid of seamless animated tiles over the whole window
	local cols = math.max(1, math.floor(W / 3 + 0.5))
	local rows = math.max(1, math.floor(FH / 3 + 0.5))
	local tw, th = W / cols, FH / rows
	local n = 0
	for r = 0, rows - 1 do
		for c = 0, cols - 1 do
			n = n + 1
			local tex = (r + c) % 2 == 0 and "ui_snow1.png" or "ui_snow2.png"
			out[#out + 1] = ("animated_image[%.3f,%.3f;%.3f,%.3f;%s;%s;48;170;%d]"):format(
				c * tw, r * th, tw, th, P .. "snow_" .. n, F(P .. tex), (r * 17 + c * 29) % 48 + 1)
		end
	end

	-- snow drift along the bottom
	bg(0, H - 0.15, W, ground_h + 0.15, "ui_drift.png")

	-- glowing garland along the outline of the window
	local gt = 0.5
	local hw = closest(garland_w, W * 100)
	local vh = closest(garland_h, H * 100)
	bg(0.02, 0, gt, FH, ("ui_garland_v_%d.png"):format(vh))
	bg(W - gt - 0.02, 0, gt, FH, ("ui_garland_v_%d.png"):format(vh) .. "^[transformFX")
	bg(0, 0.02, W, gt, ("ui_garland_h_%d.png"):format(hw))
	bg(0, FH - gt - 0.02, W, gt, ("ui_garland_h_%d.png"):format(hw))

	-- snowmen, gifts, candy canes and gingerbread men standing in the drift
	local px = 0.04 * s -- one sprite pixel
	local x, i = 0.6, 1
	while true do
		local it = drift_items[(i - 1) % #drift_items + 1]
		local w, h = it[2] * px, it[3] * px
		if x + w > W - 0.6 then
			break
		end
		bg(x, FH - 0.32 - h, w, h, it[1])
		x = x + w + drift_gaps[(i - 1) % #drift_gaps + 1] * s
		i = i + 1
	end

	return table.concat(out)
end

-- Wraps unified_inventory.get_formspec: the decoration is inserted right
-- after the standard background and the window is made ground_h taller.
-- Only the formspec string sent to the client changes.
local function unified_inventory_decor()
	local ui = rawget(_G, "unified_inventory")
	if type(ui) ~= "table" or type(ui.get_formspec) ~= "function"
			or type(ui.get_per_player_formspec) ~= "function"
			or type(ui.standard_background) ~= "string" then
		return
	end
	local get_formspec = ui.get_formspec
	local cache = {}

	ui.get_formspec = function(player, page, ...)
		local fs = get_formspec(player, page, ...)
		if type(fs) ~= "string" or fs == "" or not player then
			return fs
		end
		local style = ui.get_per_player_formspec(player:get_player_name())
		if not style or not style.formw or not style.formh then
			return fs
		end
		local size = "size[" .. style.formw .. "," .. style.formh .. "]"
		local s1, e1 = fs:find(size, 1, true)
		local s2, e2 = fs:find(ui.standard_background, 1, true)
		if not s1 or not s2 or s2 < e1 then
			return fs
		end
		local key = style.formw .. "x" .. style.formh .. (style.is_lite_mode and "l" or "")
		cache[key] = cache[key] or ui_decor(style)
		return fs:sub(1, s1 - 1)
			.. "size[" .. style.formw .. "," .. (style.formh + ground_h) .. "]"
			.. fs:sub(e1 + 1, e2) .. cache[key] .. fs:sub(e2 + 1)
	end
end

----------------------------------------------------------------

minetest.register_on_mods_loaded(function()
	apples()
	torches()
	chests()
	doors_wreath()
	fences()
	pine_trees()
	smartshop()
	bones()
	helmets()
	sheep()
	unified_inventory_decor()
end)
