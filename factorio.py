import math
from collections import deque
from fractions import Fraction

TIME = "time"
PRODUCT_COUNT = "product count"
INGREDIENTS = "ingredients"
INGREDIENT = "ingredient"
SPEED = "speed"
MACHINE = "machine"
FURNACE = "furnace"
ASSEMBLER = "assembler"
CHEMICAL_PLANT = "chemical plant"
FLUID_CHEMICAL_PLANT = "fluid chemical plant"
RESOURCE = "resource"
FLUID_RESOURCE = "fluid resource"
RESOURCE_MACHINES = [RESOURCE, FLUID_RESOURCE]
ACCEPTS_PRODUCTIVITY = "accepts productivity"
ALTERNATE_OUTPUTS = "alternate outputs"
MACHINE_CRAFT_RATE = "machine craft rate"
MACHINE_PRODUCTIVITY = "machine productivity"
BELT_SPEED = "belt speed"
MEGABASE_BELT_SPEED = 45
PRODUCTION_MODE = "production mode"
SPEEDRUN = "speedrun"
MEGABASE = "megabase"
BASE_INDENT = "        "
MACHINE_STATS_BY_PRODUCTION_MODE = {
	SPEEDRUN: {
		RESOURCE: {BELT_SPEED: 15},
		FLUID_RESOURCE: {},
		FURNACE: {MACHINE_CRAFT_RATE: 2},
		ASSEMBLER: {MACHINE_CRAFT_RATE: 0.75},
		CHEMICAL_PLANT: {MACHINE_CRAFT_RATE: 1},
		FLUID_CHEMICAL_PLANT: {MACHINE_CRAFT_RATE: 1},
	},
	MEGABASE: {
		RESOURCE: {BELT_SPEED: MEGABASE_BELT_SPEED},
		FLUID_RESOURCE: {},
		FURNACE: {MACHINE_PRODUCTIVITY: 1.2, BELT_SPEED: MEGABASE_BELT_SPEED},
		ASSEMBLER: {MACHINE_PRODUCTIVITY: 1.4, BELT_SPEED: MEGABASE_BELT_SPEED},
		CHEMICAL_PLANT: {MACHINE_PRODUCTIVITY: 1.3, BELT_SPEED: MEGABASE_BELT_SPEED},
		FLUID_CHEMICAL_PLANT: {MACHINE_PRODUCTIVITY: 1.3},
	},
}

INGREDIENTS_LIST = []
RECIPES = {}

def add_item(
		name,
		time = 0,
		product_count = 1,
		machine = ASSEMBLER,
		accepts_productivity = True,
		ingredients = {},
		alternate_outputs = {}):
	RECIPES[name] = {
		TIME: time,
		PRODUCT_COUNT: product_count,
		INGREDIENTS: ingredients,
		MACHINE: machine,
		ACCEPTS_PRODUCTIVITY: accepts_productivity,
		ALTERNATE_OUTPUTS: alternate_outputs,
	}
	INGREDIENTS_LIST.append(name)
	return name

IRON_ORE = add_item("Iron ore", machine = RESOURCE)
COPPER_ORE = add_item("Copper ore", machine = RESOURCE)
COAL = add_item("Coal", machine = RESOURCE)
STONE = add_item("Stone", machine = RESOURCE)
WATER = add_item("Water", machine = FLUID_RESOURCE)
CRUDE_OIL = add_item("Crude oil", machine = FLUID_RESOURCE)
PETROLEUM = add_item("Petroleum gas", machine = FLUID_CHEMICAL_PLANT)
LIGHT_OIL = add_item("Light oil", machine = FLUID_CHEMICAL_PLANT)
HEAVY_OIL = add_item("Heavy oil", machine = FLUID_CHEMICAL_PLANT)
LUBRICANT = add_item("Lubricant", machine = FLUID_CHEMICAL_PLANT)
SOLID_FUEL = add_item(
	name = "Solid fuel", time = 2, machine = CHEMICAL_PLANT,
	ingredients = {
		LIGHT_OIL: 10,
	})
IRON = add_item(
	name = "Iron plate", time = 3.2, machine = FURNACE,
	ingredients = {
		IRON_ORE: 1,
	})
COPPER = add_item(
	name = "Copper plate", time = 3.2, machine = FURNACE,
	ingredients = {
		COPPER_ORE: 1,
	})
STONE_BRICK = add_item(
	name = "Stone brick", time = 3.2, machine = FURNACE,
	ingredients = {
		STONE: 2,
	})
STEEL = add_item(
	name = "Steel plate", time = 16, machine = FURNACE,
	ingredients = {
		IRON: 5,
	})
GEAR = add_item(
	name = "Iron gear wheel", time = 0.5,
	ingredients = {
		IRON: 2,
	})
CABLE = add_item(
	name = "Copper cable", time = 0.5, product_count = 2,
	ingredients = {
		COPPER: 1,
	})
CIRCUIT = add_item(
	name = "Electronic circuit", time = 0.5,
	ingredients = {
		IRON: 1,
		CABLE: 3,
	})
BELT = add_item(
	name = "Transport belt", time = 0.5, product_count = 2, accepts_productivity = False,
	ingredients = {
		IRON: 1,
		GEAR: 1,
	})
INSERTER = add_item(
	name = "Inserter", time = 0.5, accepts_productivity = False,
	ingredients = {
		IRON: 1,
		GEAR: 1,
		CIRCUIT: 1,
	})
BULLET = add_item(
	name = "Firearm magazine", time = 1, accepts_productivity = False,
	ingredients = {
		IRON: 4,
	})
PIERCING = add_item(
	name = "Piercing rounds magazine", time = 3, accepts_productivity = False,
	ingredients = {
		COPPER: 5,
		STEEL: 1,
		BULLET: 1,
	})
GRENADE = add_item(
	name = "Grenade", time = 8, accepts_productivity = False,
	ingredients = {
		COAL: 10,
		IRON: 5,
	})
WALL = add_item(
	name = "Wall", time = 0.5, accepts_productivity = False,
	ingredients = {
		STONE_BRICK: 5,
	})
SULFUR = add_item(
	name = "Sulfur", time = 1, product_count = 2, machine = CHEMICAL_PLANT,
	ingredients = {
		WATER: 30,
		PETROLEUM: 30,
	})
PLASTIC = add_item(
	name = "Plastic bar", time = 1, product_count = 2, machine = CHEMICAL_PLANT,
	ingredients = {
		COAL: 1,
		PETROLEUM: 20,
	})
ADVANCED_CIRCUIT = add_item(
	name = "Advanced circuit", time = 6,
	ingredients = {
		PLASTIC: 2,
		CABLE: 4,
		CIRCUIT: 2,
	})
PIPE = add_item(
	name = "Pipe", time = 0.5, accepts_productivity = False,
	ingredients = {
		IRON: 1,
	})
ENGINE = add_item(
	name = "Engine unit", time = 10,
	ingredients = {
		STEEL: 1,
		GEAR: 1,
		PIPE: 2,
	})
STICK = add_item(
	name = "Iron stick", time = 0.5, product_count = 2,
	ingredients = {
		IRON: 1,
	})
RAIL = add_item(
	name = "Rail", time = 0.5, product_count = 2, accepts_productivity = False,
	ingredients = {
		STONE: 1,
		STEEL: 1,
		STICK: 1,
	})
ELECTRIC_FURNACE = add_item(
	name = "Electric furnace", time = 5, accepts_productivity = False,
	ingredients = {
		STEEL: 10,
		ADVANCED_CIRCUIT: 5,
		STONE_BRICK: 10,
	})
PRODUCTIVITY = add_item(
	name = "Productivity module", time = 15, accepts_productivity = False,
	ingredients = {
		CIRCUIT: 5,
		ADVANCED_CIRCUIT: 5,
	})
SULFURIC_ACID = add_item(
	name = "Sulfuric acid", time = 1, product_count = 50, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		IRON: 1,
		SULFUR: 5,
		WATER: 100,
	})
PROCESSING = add_item(
	name = "Processing unit", time = 10,
	ingredients = {
		CIRCUIT: 20,
		ADVANCED_CIRCUIT: 2,
		SULFURIC_ACID: 5,
	})
BATTERY = add_item(
	name = "Battery", time = 4, machine = CHEMICAL_PLANT,
	ingredients = {
		IRON: 1,
		COPPER: 1,
		SULFURIC_ACID: 20,
	})
ELECTRIC_ENGINE = add_item(
	name = "Electric engine unit", time = 10,
	ingredients = {
		CIRCUIT: 2,
		ENGINE: 1,
		LUBRICANT: 15,
	})
ROBOT_FRAME = add_item(
	name = "Flying robot frame", time = 20,
	ingredients = {
		STEEL: 1,
		BATTERY: 2,
		CIRCUIT: 3,
		ELECTRIC_ENGINE: 1,
	})
STRUCTURE = add_item(
	name = "Low density structure", time = 20,
	ingredients = {
		COPPER: 20,
		STEEL: 2,
		PLASTIC: 5,
	})
ROCKET_FUEL = add_item(
	name = "Rocket fuel", time = 30,
	ingredients = {
		SOLID_FUEL: 10,
		LIGHT_OIL: 10,
	})
AUTOMATION = add_item(
	name = "Automation science pack", time = 5,
	ingredients = {
		COPPER: 1,
		GEAR: 1,
	})
LOGISTIC = add_item(
	name = "Logistic science pack", time = 6,
	ingredients = {
		BELT: 1,
		INSERTER: 1,
	})
CHEMICAL = add_item(
	name = "Chemical science pack", time = 24, product_count = 2,
	ingredients = {
		SULFUR: 1,
		ADVANCED_CIRCUIT: 3,
		ENGINE: 2,
	})
MILITARY = add_item(
	name = "Military science pack", time = 10, product_count = 2,
	ingredients = {
		PIERCING: 1,
		GRENADE: 1,
		WALL: 2,
	})
PRODUCTION = add_item(
	name = "Production science pack", time = 21, product_count = 3,
	ingredients = {
		RAIL: 30,
		ELECTRIC_FURNACE: 1,
		PRODUCTIVITY: 1,
	})
UTILITY = add_item(
	name = "Utility science pack", time = 21, product_count = 3,
	ingredients = {
		PROCESSING: 2,
		ROBOT_FRAME: 1,
		STRUCTURE: 3,
	})
ROCKET = add_item(
	name = "Rocket launch", time = 300,
	ingredients = {
		PROCESSING: 1000,
		STRUCTURE: 1000,
		ROCKET_FUEL: 1000,
	})
SOLAR_PANEL = add_item(
	name = "Solar panel", time = 10, accepts_productivity = False,
	ingredients = {
		COPPER: 5,
		STEEL: 5,
		CIRCUIT: 15,
	})
ACCUMULATOR = add_item(
	name = "Accumulator", time = 10, accepts_productivity = False,
	ingredients = {
		IRON: 2,
		BATTERY: 5,
	})
RADAR = add_item(
	name = "Radar", time = 0.5, accepts_productivity = False,
	ingredients = {
		IRON: 10,
		GEAR: 5,
		CIRCUIT: 5,
	})
SATELLITE = add_item(
	name = "Satellite", time = 5, accepts_productivity = False,
	ingredients = {
		PROCESSING: 100,
		STRUCTURE: 100,
		ROCKET_FUEL: 50,
		SOLAR_PANEL: 100,
		ACCUMULATOR: 100,
		RADAR: 5,
	})
SATELLITE_LAUNCH = add_item(
	name = "Satellite launch", time = 1, accepts_productivity = False,
	ingredients = {
		ROCKET: 1,
		SATELLITE: 1,
	})
ADVANCED_OIL = add_item(
	name = "Advanced oil processing", time = 5, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		CRUDE_OIL: 100,
		WATER: 50,
	},
	alternate_outputs = {
		PETROLEUM: 55,
		LIGHT_OIL: 45,
		HEAVY_OIL: 25,
	})
LUBRICANT_RECIPE = add_item(
	name = "Lubricant (recipe)", time = 1, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		HEAVY_OIL: 10,
	},
	alternate_outputs = {
		LUBRICANT: 10,
	})
HEAVY_OIL_CRACKING = add_item(
	name = "Heavy oil cracking", time = 2, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		HEAVY_OIL: 40,
		WATER: 30,
	},
	alternate_outputs = {
		LIGHT_OIL: 30,
	})
LIGHT_OIL_CRACKING = add_item(
	name = "Light oil cracking", time = 2, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		LIGHT_OIL: 30,
		WATER: 30,
	},
	alternate_outputs = {
		PETROLEUM: 20,
	})

INTEGRATED_INGREDIENTS = [GEAR, CABLE]

def get_productivity_with_machine_stats(recipe, recipe_machine_stats, default_productivity):
	productivity = recipe_machine_stats.get(MACHINE_PRODUCTIVITY)
	#in certain machines and production modes, machines don't have productivity modules
	if not productivity:
		return default_productivity
	if not recipe[ACCEPTS_PRODUCTIVITY]:
		return 1.0
	return productivity

def get_productivity(recipe, machine_stats, default_productivity):
	return get_productivity_with_machine_stats(recipe, machine_stats[recipe[MACHINE]], default_productivity)

def get_machines_speeds(desired_output, production_mode):
	net_machine_speeds = {}
	remaining_machines_needed = deque()
	machine_stats = MACHINE_STATS_BY_PRODUCTION_MODE[production_mode]

	for output, speed in desired_output.items():
		remaining_machines_needed.append({INGREDIENT: output, SPEED: speed})

	while len(remaining_machines_needed) > 0:
		next_machine_needed = remaining_machines_needed.popleft()
		ingredient = next_machine_needed[INGREDIENT]
		speed = next_machine_needed[SPEED]
		net_machine_speeds[ingredient] = net_machine_speeds.get(ingredient, 0) + speed
		recipe = RECIPES[ingredient]
		sub_ingredient_base_speed = speed / get_productivity(recipe, machine_stats, 1.0) / recipe[PRODUCT_COUNT]
		for sub_ingredient, count in recipe[INGREDIENTS].items():
			remaining_machines_needed.append({INGREDIENT: sub_ingredient, SPEED: count * sub_ingredient_base_speed})

	if production_mode == MEGABASE:
		add_oil(net_machine_speeds, machine_stats)

	return net_machine_speeds

def add_oil(net_machine_speeds, machine_stats):
	oil_ingredients_and_recipe_sequences = [
		(LUBRICANT, [ADVANCED_OIL, LUBRICANT_RECIPE]),
		(HEAVY_OIL, [ADVANCED_OIL]),
		(LIGHT_OIL, [ADVANCED_OIL, HEAVY_OIL_CRACKING]),
		(PETROLEUM, [ADVANCED_OIL, HEAVY_OIL_CRACKING, LIGHT_OIL_CRACKING])
	]
	consumptions = {}
	machine_speeds = {}
	productions = {}

	advanced_oil_ingredients = RECIPES[ADVANCED_OIL][INGREDIENTS]
	for oil_ingredient, recipe_sequence in oil_ingredients_and_recipe_sequences:
		#skip if we don't need this ingredient
		net_oil_ingredient_needed = \
			net_machine_speeds.get(oil_ingredient, 0) \
				- productions.get(oil_ingredient, 0) \
				+ consumptions.get(oil_ingredient, 0)
		if net_oil_ingredient_needed == 0:
			continue
		#skip anything that is temporarily a resource
		if RECIPES[oil_ingredient][MACHINE] == FLUID_RESOURCE:
			continue
		#start by producing the ingredients for one advanced oil craft
		ingredient_consumptions = {}
		ingredient_machine_speeds = {}
		ingredient_productions = advanced_oil_ingredients.copy()
		#go through each recipe in the sequence to convert ingredients into our desired oil
		for recipe_name in recipe_sequence:
			recipe = RECIPES[recipe_name]
			ingredients = recipe[INGREDIENTS]
			#recipes only consume one oil ingredient, find it first
			consumed_ingredient = \
				next(ingredient for ingredient in ingredients if ingredient_productions.get(ingredient) != None)
			scale_factor = ingredient_productions[consumed_ingredient] / ingredients[consumed_ingredient]
			#update the productions
			for ingredient, count in ingredients.items():
				ingredient_consumptions[ingredient] = \
					ingredient_consumptions.get(ingredient, 0) + count * scale_factor
			#crafts and outputs both need to account for productivity
			scale_factor *= get_productivity(recipe, machine_stats, 1.0)
			ingredient_machine_speeds[recipe_name] = scale_factor
			for ingredient, count in recipe[ALTERNATE_OUTPUTS].items():
				ingredient_productions[ingredient] = \
					ingredient_productions.get(ingredient, 0) + count * scale_factor
		#find out how much we need total
		net_scale_factor = net_oil_ingredient_needed / ingredient_productions[oil_ingredient]
		#add all the values to the totals
		#this includes the fake production of the advanced oil ingredients but those will eventually get discarded
		combined_value_maps = [
			(ingredient_consumptions, consumptions),
			(ingredient_machine_speeds, machine_speeds),
			(ingredient_productions, productions)
		]
		for ingredient_values, total_values in combined_value_maps:
			for ingredient, value in ingredient_values.items():
				total_values[ingredient] = total_values.get(ingredient, 0) + value * net_scale_factor
	#finally, combine machine speeds
	for resource_name, speed in consumptions.items():
		net_machine_speeds[resource_name] = net_machine_speeds.get(resource_name, 0) + speed
	for recipe_name, speed in machine_speeds.items():
		net_machine_speeds[recipe_name] = speed

#remove any machine speeds if they're only used in a single recipe, we'll show the speeds directly as part of that recipe
def prune_single_use_ingredients(desired_output, net_machine_speeds):
	pruned_net_machine_speeds = {}
	ingredient_recipe_use_counts = {}
	for ingredient in net_machine_speeds:
		recipe = RECIPES[ingredient]
		for sub_ingredient in recipe[INGREDIENTS]:
			ingredient_recipe_use_counts[sub_ingredient] = ingredient_recipe_use_counts.get(sub_ingredient, 0) + 1
		if recipe[ALTERNATE_OUTPUTS]:
			pruned_net_machine_speeds[ingredient] = net_machine_speeds[ingredient]

	for ingredient in desired_output:
		pruned_net_machine_speeds[ingredient] = net_machine_speeds[ingredient]
		ingredient_recipe_use_counts.pop(ingredient, None)
	for ingredient, count in ingredient_recipe_use_counts.items():
		if count > 1 or RECIPES[ingredient][MACHINE] in RESOURCE_MACHINES:
			pruned_net_machine_speeds[ingredient] = net_machine_speeds[ingredient]
	return pruned_net_machine_speeds

def print_single_speed(ingredient, speed, indent, recipe, recipe_machine_stats):
	speed_prefix = "{}{:.20f}/s {}".format(indent, speed, ingredient)
	extra_stats = []
	recipe_craft_rate = recipe_machine_stats.get(MACHINE_CRAFT_RATE, None)
	if recipe_craft_rate:
		machines_count = math.ceil(speed * recipe[TIME] / recipe[PRODUCT_COUNT] / recipe_craft_rate)
		extra_stats.append("{} machines".format(machines_count))
	belt_speed = recipe_machine_stats.get(BELT_SPEED, None)
	if belt_speed:
		belts = math.ceil(speed * 10.0 / belt_speed) / 10
		extra_stats.append("{:.1f} belts".format(belts))
	recipe_productivity = get_productivity_with_machine_stats(recipe, recipe_machine_stats, None)
	#don't show craft rate if the machine won't use productivity
	if recipe_productivity:
		machine_craft_rate = speed * recipe[TIME] / recipe[PRODUCT_COUNT] / recipe_productivity
		extra_stats.append("{:.4f} craft rate".format(machine_craft_rate))
	if extra_stats:
		print("{} ({})".format(speed_prefix, ", ".join(extra_stats)))
	else:
		print(speed_prefix)

def print_speed(ingredient, speed, indent, machine_stats, net_machine_speeds, print_sub_ingredients):
	recipe = RECIPES[ingredient]
	recipe_machine_stats = machine_stats[recipe[MACHINE]]
	recipe_productivity = get_productivity_with_machine_stats(recipe, recipe_machine_stats, 1.0)
	print_single_speed(ingredient, speed, indent, recipe, recipe_machine_stats)
	if print_sub_ingredients or ingredient in INTEGRATED_INGREDIENTS:
		for sub_ingredient, sub_count in recipe[INGREDIENTS].items():
			print_speed(
				sub_ingredient,
				sub_count * speed / recipe_productivity / recipe[PRODUCT_COUNT],
				indent + BASE_INDENT,
				machine_stats,
				net_machine_speeds,
				sub_ingredient not in net_machine_speeds)

def print_desired_output(desired_output, production_mode):
	print("Desired output:")
	machine_stats = MACHINE_STATS_BY_PRODUCTION_MODE[production_mode]
	for output, speed in desired_output.items():
		print_speed(output, speed, "", machine_stats, {}, False)
	print("")

def print_machine_speeds(desired_output, net_machine_speeds, production_mode):
	print("Net machines:")
	net_machine_speeds = prune_single_use_ingredients(desired_output, net_machine_speeds)
	machine_stats = MACHINE_STATS_BY_PRODUCTION_MODE[production_mode]

	resource_ingredients = []
	intermediate_ingredients = []
	output_ingredients = []
	for ingredient in INGREDIENTS_LIST:
		speed = net_machine_speeds.get(ingredient)
		if not speed:
			continue
		ingredient_and_speed = (ingredient, speed)
		recipe = RECIPES[ingredient]
		if recipe[MACHINE] in RESOURCE_MACHINES:
			resource_ingredients.append(ingredient_and_speed)
		elif ingredient in desired_output:
			output_ingredients.append(ingredient_and_speed)
		else:
			intermediate_ingredients.append(ingredient_and_speed)

	ordered_ingredients = resource_ingredients + intermediate_ingredients + output_ingredients
	for (ingredient, speed) in ordered_ingredients:
		print_speed(ingredient, speed, "", machine_stats, net_machine_speeds, True)
	print("")

def merge_machine_speeds(all_machine_speeds):
	new_machine_speeds = {}
	for ingredient in INGREDIENTS_LIST:
		new_machine_speed = 0
		for machine_speeds in all_machine_speeds:
			new_machine_speed = max(new_machine_speed, machine_speeds.get(ingredient, 0))
		if new_machine_speed > 0:
			new_machine_speeds[ingredient] = new_machine_speed
	return new_machine_speeds

def print_desired_output_and_machine_speeds(desired_outputs, production_mode, extra_resources = [], extra_fluid_resources = []):
	old_recipes = {}
	for extra_resource in extra_resources:
		old_recipes[extra_resource] = RECIPES.pop(extra_resource)
		add_item(extra_resource, machine = RESOURCE)
		INGREDIENTS_LIST.pop()
	for extra_fluid_resource in extra_fluid_resources:
		old_recipes[extra_fluid_resource] = RECIPES.pop(extra_fluid_resource)
		add_item(extra_fluid_resource, machine = FLUID_RESOURCE)
		INGREDIENTS_LIST.pop()

	if not isinstance(desired_outputs, list):
		print_desired_output(desired_outputs, production_mode)
		print_machine_speeds(
			desired_outputs.keys(), get_machines_speeds(desired_outputs, production_mode), production_mode)
	else:
		all_machine_speeds = []
		all_desired_output_ingredients = []
		for desired_output in desired_outputs:
			print_desired_output(desired_output, production_mode)
			all_machine_speeds.append(get_machines_speeds(desired_output, production_mode))
			all_desired_output_ingredients.extend(list(desired_output.keys()))
		print_machine_speeds(all_desired_output_ingredients, merge_machine_speeds(all_machine_speeds), production_mode)
	for old_name, old_recipe in old_recipes.items():
		RECIPES[old_name] = old_recipe

def print_megabase_belt_splits(output, input, supply_belt_speed_sequence=[], craft_rate_sequence=[]):
	if not supply_belt_speed_sequence:
		recipe = RECIPES[output]
		if type(input) != list:
			input = [input]
		last_input = input[0]
		input_per_supply_belt = recipe[INGREDIENTS][last_input] / Fraction(recipe[TIME]).limit_denominator(100)
		megabase_machine_stats = MACHINE_STATS_BY_PRODUCTION_MODE[MEGABASE]
		input_iter = iter(input)
		next(input_iter)
		for next_input in input_iter:
			recipe = RECIPES[last_input]
			input_per_supply_belt *= \
				Fraction(recipe[INGREDIENTS][next_input], recipe[PRODUCT_COUNT]) \
					/ Fraction(get_productivity(recipe, megabase_machine_stats, 1.0))
			last_input = next_input
		supply_belt_speed_sequence = \
			list(map(lambda x: Fraction(x).limit_denominator(1000000) * input_per_supply_belt, craft_rate_sequence))
	if type(input) == list:
		input = input[-1]
	next_supply_belt = 0
	supply_belts = len(supply_belt_speed_sequence)
	input_belt = 0
	input_spare = 0
	input_belt_texts = []
	used_spare_texts = []
	supply_belts_texts = []
	input_spare_texts = []
	while next_supply_belt < supply_belts:
		input_belt += 1
		input_belt_texts.append("Belt " + str(input_belt))
		used_spare_texts.append("" if input_spare == 0 else " + spare")
		input_spare += MEGABASE_BELT_SPEED
		supply_belts_filled = []
		while next_supply_belt < supply_belts:
			supply_needed = supply_belt_speed_sequence[next_supply_belt]
			if supply_needed > input_spare:
				break
			input_spare -= supply_needed
			next_supply_belt += 1
			supply_belts_filled.append(str(next_supply_belt))
		supply_belts_texts.append(", ".join(supply_belts_filled))
		input_spare_texts.append("" if input_spare == 0 else "{:.20f}".format(float(input_spare)).rstrip("0"))
	input_belt_text_max_len = len(max(input_belt_texts, key=lambda x: len(x))) 
	used_spare_text_max_len = len(max(used_spare_texts, key=lambda x: len(x)))
	supply_belts_text_max_len = len(max(supply_belts_texts, key=lambda x: len(x)))
	input_spare_text_max_len = len(max(input_spare_texts, key=lambda x: len(x)))

	print("{} -> {}".format(input, output))
	#no spare at all
	if used_spare_text_max_len == 0:
		for input_belt_text, supply_belts_text in zip(input_belt_texts, supply_belts_texts):
			print("{:{}}: {:{}}".format(
				input_belt_text, input_belt_text_max_len,
				supply_belts_text, supply_belts_text_max_len))
	#spare at some point
	else:
		texts = zip(input_belt_texts, used_spare_texts, supply_belts_texts, input_spare_texts)
		for input_belt_text, used_spare_text, supply_belts_text, input_spare_text in texts:
			if input_spare_text:
				print("{:{}}{:{}}: {:{}} + {:{}} spare".format(
					input_belt_text, input_belt_text_max_len,
					used_spare_text, used_spare_text_max_len,
					supply_belts_text, supply_belts_text_max_len,
					input_spare_text, input_spare_text_max_len))
			else:
				print("{:{}}{:{}}: {:{}}".format(
					input_belt_text, input_belt_text_max_len,
					used_spare_text, used_spare_text_max_len,
					supply_belts_text, supply_belts_text_max_len))
	print("")

print("\n\n")

print_desired_output_and_machine_speeds(
	[
		{
			AUTOMATION: 1,
			LOGISTIC: 1,
			CHEMICAL: 1,
			MILITARY: 1,
			PRODUCTION: 1,
			UTILITY: 1,
		},
		{
			ROCKET: 1 / 1200,
		},
	],
	SPEEDRUN)
print_desired_output_and_machine_speeds(
	{
		AUTOMATION: 45,
		LOGISTIC: 45,
		CHEMICAL: 45,
		MILITARY: 45,
		PRODUCTION: 45,
		UTILITY: 45,
		SATELLITE_LAUNCH: 45 / 1000,
	},
	MEGABASE)
print_megabase_belt_splits(IRON, IRON_ORE, [Fraction(MEGABASE_BELT_SPEED * 5, 6)] * 6)
