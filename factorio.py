import math
import heapq
from fractions import Fraction

EMPTY_DICT = {}
TIME = "time"
PRODUCT_COUNT = "product count"
INGREDIENTS = "ingredients"
SPEED = "speed"
MACHINE = "machine"
TIER = "tier"
RESOURCE = "resource"
FLUID_RESOURCE = "fluid resource"
FURNACE = "furnace"
ASSEMBLER = "assembler"
CHEMICAL_PLANT = "chemical plant"
FLUID_CHEMICAL_PLANT = "fluid chemical plant"
ELECTROMECHANICAL_PLANT = "electromechanical plant"
ELECTROMECHANICAL_PLANT_P5 = "electromechanical plant +5"
CRYOGENIC_PLANT = "cryogenic plant"
BASIC_MACHINE = "basic machine"
RESOURCE_MACHINES = [RESOURCE, FLUID_RESOURCE]
ACCEPTS_PRODUCTIVITY = "accepts productivity"
ALTERNATE_OUTPUTS = "alternate outputs"
RECIPE_INGREDIENTS = "recipe ingredients"
MACHINE_CRAFT_RATE = "machine craft rate"
MACHINE_PRODUCTIVITY = "machine productivity"
BASE_PRODUCTIVITY = "base productivity"
BELT_SPEED = "belt speed"
MEGABASE_BELT_SPEED = 45
PRODUCTION_MODE = "production mode"
SPEEDRUN = "speedrun"
MEGABASE = "megabase"
SA_SPACE_PLATFORM = "SA space platform"
SA_MEGABASE = "SA megabase"
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
	SA_SPACE_PLATFORM: {
		RESOURCE: {},
		FLUID_RESOURCE: {},
		FURNACE: {MACHINE_PRODUCTIVITY: 1.2},
		CHEMICAL_PLANT: {MACHINE_PRODUCTIVITY: 1.3},
		FLUID_CHEMICAL_PLANT: {MACHINE_PRODUCTIVITY: 1.3},
		ELECTROMECHANICAL_PLANT: {BASE_PRODUCTIVITY: 1.5, MACHINE_PRODUCTIVITY: 2.0},
		ELECTROMECHANICAL_PLANT_P5: {BASE_PRODUCTIVITY: 1.5, MACHINE_PRODUCTIVITY: 2.5},
		BASIC_MACHINE: {MACHINE_PRODUCTIVITY: 1.0},
	},
	SA_MEGABASE: {
		RESOURCE: {},
		FLUID_RESOURCE: {},
		FURNACE: {MACHINE_PRODUCTIVITY: 1.5},
		CHEMICAL_PLANT: {MACHINE_PRODUCTIVITY: 1.75},
		FLUID_CHEMICAL_PLANT: {MACHINE_PRODUCTIVITY: 1.75},
		ELECTROMECHANICAL_PLANT: {BASE_PRODUCTIVITY: 1.5, MACHINE_PRODUCTIVITY: 2.75},
		ELECTROMECHANICAL_PLANT_P5: {BASE_PRODUCTIVITY: 1.5, MACHINE_PRODUCTIVITY: 3.25},
		CRYOGENIC_PLANT: {MACHINE_PRODUCTIVITY: 3.0},
		BASIC_MACHINE: {MACHINE_PRODUCTIVITY: 1.0},
	},
}

INGREDIENTS_LIST = []
RECIPES = {}

class ItemProduction:
	def __init__(self, name):
		self.name = name
		self.tier = RECIPES[name][TIER]

	def __lt__(self, other):
		return self.tier > other.tier

def add_recipe(name, recipe):
	RECIPES[name] = recipe
	INGREDIENTS_LIST.append(name)
	return name

def add_item(
		name,
		time = 0,
		product_count = 1,
		machine = ASSEMBLER,
		accepts_productivity = True,
		ingredients = None,
		alternate_outputs = None,
		original_name = None,
		alt_ingredients = None):
	recipe = {
		TIME: time,
		PRODUCT_COUNT: product_count,
		MACHINE: machine,
		ACCEPTS_PRODUCTIVITY: accepts_productivity,
		TIER: (max(RECIPES[ingredient][TIER] for ingredient in ingredients) + 1 if ingredients else 0),
	}
	for field, value in [(INGREDIENTS, ingredients), (ALTERNATE_OUTPUTS, alternate_outputs)]:
		if value:
			recipe[field] = value
	if original_name and alt_ingredients is not None:
		alt_ingredients[original_name] = name
	return add_recipe(name, recipe)

def set_recipe_ingredients(names, recipe_sequence):
	tier = max(RECIPES[recipe_name][TIER] for recipe_name in recipe_sequence)
	for name in names:
		recipe = RECIPES[name]
		tier += 1
		recipe[TIER] = tier
		recipe_ingredients = recipe_sequence.copy()
		while (name not in (output for output in RECIPES[recipe_ingredients[-1]][ALTERNATE_OUTPUTS])):
			recipe_ingredients.pop()
		recipe[RECIPE_INGREDIENTS] = recipe_ingredients

def clone_recipe_with_alt_ingredients(name, original_name, alt_ingredients, machine = None):
	recipe = RECIPES[original_name].copy()
	if machine:
		recipe[MACHINE] = machine
	for ingredients_name in [INGREDIENTS, ALTERNATE_OUTPUTS]:
		if ingredients_name in recipe:
			recipe[ingredients_name] = \
				{alt_ingredients.get(ingredient, ingredient): count
					for ingredient, count in recipe[ingredients_name].items()}
	recipe[TIER] = max(RECIPES[ingredient][TIER] for ingredient in recipe[INGREDIENTS]) + 1
	alt_ingredients[original_name] = name
	return add_recipe(name, recipe)

IRON_ORE = add_item("Iron ore", machine = RESOURCE)
COPPER_ORE = add_item("Copper ore", machine = RESOURCE)
COAL = add_item("Coal", machine = RESOURCE)
STONE = add_item("Stone", machine = RESOURCE)
WATER = add_item("Water", machine = FLUID_RESOURCE)
CRUDE_OIL = add_item("Crude oil", machine = FLUID_RESOURCE)
PETROLEUM = add_item("Petroleum gas", machine = FLUID_RESOURCE)
LIGHT_OIL = add_item("Light oil", machine = FLUID_RESOURCE)
HEAVY_OIL = add_item("Heavy oil", machine = FLUID_RESOURCE)
ADVANCED_OIL = add_item(
	"Advanced oil processing", time = 5, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		CRUDE_OIL: 100,
		WATER: 50,
	},
	alternate_outputs = {
		PETROLEUM: 55,
		LIGHT_OIL: 45,
		HEAVY_OIL: 25,
	})
HEAVY_OIL_CRACKING = add_item(
	"Heavy oil cracking", time = 2, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		HEAVY_OIL: 40,
		WATER: 30,
	},
	alternate_outputs = {
		LIGHT_OIL: 30,
	})
LIGHT_OIL_CRACKING = add_item(
	"Light oil cracking", time = 2, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		LIGHT_OIL: 30,
		WATER: 30,
	},
	alternate_outputs = {
		PETROLEUM: 20,
	})
set_recipe_ingredients([PETROLEUM, LIGHT_OIL, HEAVY_OIL], [ADVANCED_OIL, HEAVY_OIL_CRACKING, LIGHT_OIL_CRACKING])
IRON = add_item(
	"Iron plate", time = 3.2, machine = FURNACE,
	ingredients = {
		IRON_ORE: 1,
	})
COPPER = add_item(
	"Copper plate", time = 3.2, machine = FURNACE,
	ingredients = {
		COPPER_ORE: 1,
	})
STONE_BRICK = add_item(
	"Stone brick", time = 3.2, machine = FURNACE,
	ingredients = {
		STONE: 2,
	})
STEEL = add_item(
	"Steel plate", time = 16, machine = FURNACE,
	ingredients = {
		IRON: 5,
	})
GEAR = add_item(
	"Iron gear wheel", time = 0.5,
	ingredients = {
		IRON: 2,
	})
CABLE = add_item(
	"Copper cable", time = 0.5, product_count = 2,
	ingredients = {
		COPPER: 1,
	})
CIRCUIT = add_item(
	"Electronic circuit", time = 0.5,
	ingredients = {
		IRON: 1,
		CABLE: 3,
	})
BELT = add_item(
	"Transport belt", time = 0.5, product_count = 2, accepts_productivity = False,
	ingredients = {
		IRON: 1,
		GEAR: 1,
	})
INSERTER = add_item(
	"Inserter", time = 0.5, accepts_productivity = False,
	ingredients = {
		IRON: 1,
		GEAR: 1,
		CIRCUIT: 1,
	})
BULLET = add_item(
	"Firearm magazine", time = 1, accepts_productivity = False,
	ingredients = {
		IRON: 4,
	})
PIERCING = add_item(
	"Piercing rounds magazine", time = 3, accepts_productivity = False,
	ingredients = {
		COPPER: 5,
		STEEL: 1,
		BULLET: 1,
	})
GRENADE = add_item(
	"Grenade", time = 8, accepts_productivity = False,
	ingredients = {
		COAL: 10,
		IRON: 5,
	})
WALL = add_item(
	"Wall", time = 0.5, accepts_productivity = False,
	ingredients = {
		STONE_BRICK: 5,
	})
SULFUR = add_item(
	"Sulfur", time = 1, product_count = 2, machine = CHEMICAL_PLANT,
	ingredients = {
		WATER: 30,
		PETROLEUM: 30,
	})
PLASTIC = add_item(
	"Plastic bar", time = 1, product_count = 2, machine = CHEMICAL_PLANT,
	ingredients = {
		COAL: 1,
		PETROLEUM: 20,
	})
ADVANCED_CIRCUIT = add_item(
	"Advanced circuit", time = 6,
	ingredients = {
		PLASTIC: 2,
		CABLE: 4,
		CIRCUIT: 2,
	})
PIPE = add_item(
	"Pipe", time = 0.5, accepts_productivity = False,
	ingredients = {
		IRON: 1,
	})
ENGINE = add_item(
	"Engine unit", time = 10,
	ingredients = {
		STEEL: 1,
		GEAR: 1,
		PIPE: 2,
	})
STICK = add_item(
	"Iron stick", time = 0.5, product_count = 2,
	ingredients = {
		IRON: 1,
	})
RAIL = add_item(
	"Rail", time = 0.5, product_count = 2, accepts_productivity = False,
	ingredients = {
		STONE: 1,
		STEEL: 1,
		STICK: 1,
	})
ELECTRIC_FURNACE = add_item(
	"Electric furnace", time = 5, accepts_productivity = False,
	ingredients = {
		STEEL: 10,
		ADVANCED_CIRCUIT: 5,
		STONE_BRICK: 10,
	})
PRODUCTIVITY = add_item(
	"Productivity module", time = 15, accepts_productivity = False,
	ingredients = {
		CIRCUIT: 5,
		ADVANCED_CIRCUIT: 5,
	})
SULFURIC_ACID = add_item(
	"Sulfuric acid", time = 1, product_count = 50, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		IRON: 1,
		SULFUR: 5,
		WATER: 100,
	})
PROCESSING = add_item(
	"Processing unit", time = 10,
	ingredients = {
		CIRCUIT: 20,
		ADVANCED_CIRCUIT: 2,
		SULFURIC_ACID: 5,
	})
BATTERY = add_item(
	"Battery", time = 4, machine = CHEMICAL_PLANT,
	ingredients = {
		IRON: 1,
		COPPER: 1,
		SULFURIC_ACID: 20,
	})
LUBRICANT = add_item(
	"Lubricant", time = 1, product_count = 10, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		HEAVY_OIL: 10,
	})
ELECTRIC_ENGINE = add_item(
	"Electric engine unit", time = 10,
	ingredients = {
		CIRCUIT: 2,
		ENGINE: 1,
		LUBRICANT: 15,
	})
ROBOT_FRAME = add_item(
	"Flying robot frame", time = 20,
	ingredients = {
		STEEL: 1,
		BATTERY: 2,
		CIRCUIT: 3,
		ELECTRIC_ENGINE: 1,
	})
STRUCTURE = add_item(
	"Low density structure", time = 20,
	ingredients = {
		COPPER: 20,
		STEEL: 2,
		PLASTIC: 5,
	})
SOLID_FUEL = add_item(
	"Solid fuel", time = 2, machine = CHEMICAL_PLANT,
	ingredients = {
		LIGHT_OIL: 10,
	})
ROCKET_FUEL = add_item(
	"Rocket fuel", time = 30,
	ingredients = {
		SOLID_FUEL: 10,
		LIGHT_OIL: 10,
	})
AUTOMATION = add_item(
	"Automation science pack", time = 5,
	ingredients = {
		COPPER: 1,
		GEAR: 1,
	})
LOGISTIC = add_item(
	"Logistic science pack", time = 6,
	ingredients = {
		BELT: 1,
		INSERTER: 1,
	})
CHEMICAL = add_item(
	"Chemical science pack", time = 24, product_count = 2,
	ingredients = {
		SULFUR: 1,
		ADVANCED_CIRCUIT: 3,
		ENGINE: 2,
	})
MILITARY = add_item(
	"Military science pack", time = 10, product_count = 2,
	ingredients = {
		PIERCING: 1,
		GRENADE: 1,
		WALL: 2,
	})
PRODUCTION = add_item(
	"Production science pack", time = 21, product_count = 3,
	ingredients = {
		RAIL: 30,
		ELECTRIC_FURNACE: 1,
		PRODUCTIVITY: 1,
	})
UTILITY = add_item(
	"Utility science pack", time = 21, product_count = 3,
	ingredients = {
		PROCESSING: 2,
		ROBOT_FRAME: 1,
		STRUCTURE: 3,
	})
ROCKET = add_item(
	"Rocket launch", time = 300,
	ingredients = {
		PROCESSING: 1000,
		STRUCTURE: 1000,
		ROCKET_FUEL: 1000,
	})
SOLAR_PANEL = add_item(
	"Solar panel", time = 10, accepts_productivity = False,
	ingredients = {
		COPPER: 5,
		STEEL: 5,
		CIRCUIT: 15,
	})
ACCUMULATOR = add_item(
	"Accumulator", time = 10, accepts_productivity = False,
	ingredients = {
		IRON: 2,
		BATTERY: 5,
	})
RADAR = add_item(
	"Radar", time = 0.5, accepts_productivity = False,
	ingredients = {
		IRON: 10,
		GEAR: 5,
		CIRCUIT: 5,
	})
SATELLITE = add_item(
	"Satellite", time = 5, accepts_productivity = False,
	ingredients = {
		PROCESSING: 100,
		STRUCTURE: 100,
		ROCKET_FUEL: 50,
		SOLAR_PANEL: 100,
		ACCUMULATOR: 100,
		RADAR: 5,
	})
SATELLITE_LAUNCH = add_item(
	"Satellite launch", time = 1, accepts_productivity = False,
	ingredients = {
		ROCKET: 1,
		SATELLITE: 1,
	})
SPACE_ALT_INGREDIENTS = {}
SPACE_IRON = add_item("Space Iron plate", machine = RESOURCE, original_name = IRON, alt_ingredients = SPACE_ALT_INGREDIENTS)
SPACE_COPPER = add_item(
	"Space Copper plate", machine = RESOURCE, original_name = COPPER, alt_ingredients = SPACE_ALT_INGREDIENTS)
SPACE_PETROLEUM = add_item(
	"Space Petroleum gas", machine = FLUID_RESOURCE, original_name = PETROLEUM, alt_ingredients = SPACE_ALT_INGREDIENTS)
SPACE_LIGHT_OIL = add_item(
	"Space Light oil", machine = FLUID_RESOURCE, original_name = LIGHT_OIL, alt_ingredients = SPACE_ALT_INGREDIENTS)
SPACE_HEAVY_OIL = add_item(
	"Space Heavy oil", machine = FLUID_RESOURCE, original_name = HEAVY_OIL, alt_ingredients = SPACE_ALT_INGREDIENTS)
SPACE_SULFUR = add_item("Space Sulfur", machine = RESOURCE, original_name = SULFUR, alt_ingredients = SPACE_ALT_INGREDIENTS)
SPACE_ICE = add_item("Space Ice", machine = RESOURCE)
SPACE_CALCITE = add_item("Space Calcite", machine = RESOURCE)
SPACE_CARBON = add_item("Space Carbon", machine = RESOURCE)
SPACE_STEAM = add_item("Space Steam", machine = FLUID_RESOURCE)
SPACE_WATER = add_item(
	"Space Water", time = 1, product_count = 20, machine = BASIC_MACHINE,
	ingredients = {
		SPACE_ICE: 1,
	},
	original_name = WATER, alt_ingredients = SPACE_ALT_INGREDIENTS)
SPACE_COAL = add_item(
	"Space Coal", time = 2, machine = BASIC_MACHINE,
	ingredients = {
		SPACE_SULFUR: 1,
		SPACE_CARBON: 5,
		SPACE_WATER: 10,
	},
	original_name = COAL, alt_ingredients = SPACE_ALT_INGREDIENTS)
SPACE_COAL_LIQUEFACTION = add_item(
	"Space Coal liquefaction", time = 5, machine = FLUID_CHEMICAL_PLANT,
	ingredients = {
		SPACE_COAL: 10,
		SPACE_STEAM: 50,
	},
	alternate_outputs = {
		SPACE_HEAVY_OIL: 65,
		SPACE_LIGHT_OIL: 20,
		SPACE_PETROLEUM: 10,
	})
SPACE_HEAVY_OIL_CRACKING = clone_recipe_with_alt_ingredients(
	"Space Heavy oil cracking", HEAVY_OIL_CRACKING, SPACE_ALT_INGREDIENTS)
SPACE_LIGHT_OIL_CRACKING = clone_recipe_with_alt_ingredients(
	"Space Light oil cracking", LIGHT_OIL_CRACKING, SPACE_ALT_INGREDIENTS)
set_recipe_ingredients(
	[SPACE_PETROLEUM, SPACE_LIGHT_OIL, SPACE_HEAVY_OIL],
	[SPACE_COAL_LIQUEFACTION, SPACE_HEAVY_OIL_CRACKING, SPACE_LIGHT_OIL_CRACKING])
SPACE_CABLE = clone_recipe_with_alt_ingredients(
	"Space Copper cable", CABLE, SPACE_ALT_INGREDIENTS, machine = ELECTROMECHANICAL_PLANT)
SPACE_CIRCUIT = clone_recipe_with_alt_ingredients(
	"Space Electronic circuit", CIRCUIT, SPACE_ALT_INGREDIENTS, machine = ELECTROMECHANICAL_PLANT)
SPACE_PLASTIC = clone_recipe_with_alt_ingredients(
	"Space Plastic bar", PLASTIC, SPACE_ALT_INGREDIENTS)
SPACE_ADVANCED_CIRCUIT = clone_recipe_with_alt_ingredients(
	"Space Advanced circuit", ADVANCED_CIRCUIT, SPACE_ALT_INGREDIENTS, machine = ELECTROMECHANICAL_PLANT)
SPACE_SULFURIC_ACID = clone_recipe_with_alt_ingredients(
	"Space Sulfuric acid", SULFURIC_ACID, SPACE_ALT_INGREDIENTS)
SPACE_PROCESSING = clone_recipe_with_alt_ingredients(
	"Space Processing unit", PROCESSING, SPACE_ALT_INGREDIENTS, machine = ELECTROMECHANICAL_PLANT_P5)
SPACE_MODULE_1 = add_item(
	"Space Module 1", time = 15, machine = ELECTROMECHANICAL_PLANT, accepts_productivity = False,
	ingredients = {
		SPACE_ADVANCED_CIRCUIT: 5,
		SPACE_CIRCUIT: 5,
	})
SPACE_MODULE_2 = add_item(
	"Space Module 2", time = 30, machine = ELECTROMECHANICAL_PLANT, accepts_productivity = False,
	ingredients = {
		SPACE_ADVANCED_CIRCUIT: 5,
		SPACE_PROCESSING: 5,
		SPACE_MODULE_1: 4,
	})
SA_ALT_INGREDIENTS = {}
SA_ICE = add_item("SA Ice", machine = RESOURCE)
SA_AMMONIA = add_item("SA Ammonia", machine = RESOURCE)
SA_LITHIUM_BRINE = add_item("SA Lithium brine", machine = RESOURCE)
SA_FLUORINE = add_item("SA Fluorine", machine = RESOURCE)
SA_SOLID_FUEL = add_item("SA Solid fuel", machine = RESOURCE)
SA_HOLMIUM = add_item("SA Holmium plate", machine = RESOURCE)
SA_CABLE = clone_recipe_with_alt_ingredients(
	"SA Copper cable", CABLE, SA_ALT_INGREDIENTS, machine = ELECTROMECHANICAL_PLANT)
SA_CIRCUIT = clone_recipe_with_alt_ingredients(
	"SA Electronic circuit", CIRCUIT, SA_ALT_INGREDIENTS, machine = ELECTROMECHANICAL_PLANT)
SA_ADVANCED_CIRCUIT = clone_recipe_with_alt_ingredients(
	"SA Advanced circuit", ADVANCED_CIRCUIT, SA_ALT_INGREDIENTS, machine = ELECTROMECHANICAL_PLANT)
SA_PROCESSING = clone_recipe_with_alt_ingredients(
	"SA Processing unit", PROCESSING, SA_ALT_INGREDIENTS, machine = ELECTROMECHANICAL_PLANT_P5)
SA_MODULE_1 = add_item(
	"SA Module 1", time = 15, machine = ELECTROMECHANICAL_PLANT, accepts_productivity = False,
	ingredients = {
		SA_ADVANCED_CIRCUIT: 5,
		SA_CIRCUIT: 5,
	})
SA_MODULE_2 = add_item(
	"SA Module 2", time = 30, machine = ELECTROMECHANICAL_PLANT, accepts_productivity = False,
	ingredients = {
		SA_ADVANCED_CIRCUIT: 5,
		SA_PROCESSING: 5,
		SA_MODULE_1: 4,
	})
SA_MODULE_3 = add_item(
	"SA Module 3", time = 60, machine = ELECTROMECHANICAL_PLANT, accepts_productivity = False,
	ingredients = {
		SA_ADVANCED_CIRCUIT: 5,
		SA_PROCESSING: 5,
		SA_MODULE_2: 4,
	})
SA_LITHIUM = add_item(
	"SA Lithium", time = 20, product_count = 5, machine = CRYOGENIC_PLANT,
	ingredients = {
		SA_HOLMIUM: 1,
		SA_LITHIUM_BRINE: 50,
		SA_AMMONIA: 50,
	})
SA_FLUOROKETONE = add_item(
	"SA Fluoroketone", time = 10, product_count = 50, machine = CRYOGENIC_PLANT,
	ingredients = {
		SA_SOLID_FUEL: 1,
		SA_LITHIUM: 1,
		SA_FLUORINE: 50,
		SA_AMMONIA: 50,
	})
SA_LITHIUM_PLATE = add_item(
	"SA Lithium plate", time = 6.4, machine = FURNACE,
	ingredients = {
		SA_LITHIUM: 1,
	})
SA_CRYO_SCIENCE = add_item(
	"SA Cryogenic science pack", time = 20, machine = CRYOGENIC_PLANT,
	ingredients = {
		SA_ICE: 3,
		SA_LITHIUM_PLATE: 1,
		SA_FLUOROKETONE: 3,
	})

INTEGRATED_INGREDIENTS = [GEAR, CABLE]

def get_productivity_with_machine_stats(recipe, recipe_machine_stats, default_productivity):
	productivity = recipe_machine_stats.get(MACHINE_PRODUCTIVITY)
	#in certain machines and production modes, machines don't have productivity modules
	if not productivity:
		return default_productivity
	if not recipe[ACCEPTS_PRODUCTIVITY]:
		return recipe_machine_stats.get(BASE_PRODUCTIVITY, 1.0)
	return productivity

def get_productivity(recipe, machine_stats, default_productivity):
	return get_productivity_with_machine_stats(recipe, machine_stats[recipe[MACHINE]], default_productivity)

def get_machines_speeds(desired_output, production_mode):
	net_machine_speeds = {}
	remaining_machines_needed = []
	produced_recipes = {}
	produced_ingredients = {}
	machine_stats = MACHINE_STATS_BY_PRODUCTION_MODE[production_mode]
	def add_ingredient_production(ingredient, speed):
		if ingredient in net_machine_speeds:
			net_machine_speeds[ingredient] += speed
		else:
			net_machine_speeds[ingredient] = speed
			heapq.heappush(remaining_machines_needed, ItemProduction(ingredient))
	def produce_recipe(recipe, speed):
		produced_recipes[recipe] = produced_recipes.get(recipe, 0) + speed
		for ingredient, count in RECIPES[recipe][ALTERNATE_OUTPUTS].items():
			produced_ingredients[ingredient] = produced_ingredients.get(ingredient, 0) + speed * count

	#setup our initial required products
	for output, speed in desired_output.items():
		net_machine_speeds[output] = speed
		remaining_machines_needed.append(ItemProduction(output))
	heapq.heapify(remaining_machines_needed)

	#go through products and add all their prerequisites
	while len(remaining_machines_needed) > 0:
		next_machine_needed = heapq.heappop(remaining_machines_needed)
		ingredient = next_machine_needed.name
		speed = net_machine_speeds[ingredient] - produced_ingredients.get(ingredient, 0)
		recipe = RECIPES[ingredient]
		sub_ingredients = recipe.get(INGREDIENTS, None)
		recipe_ingredients = recipe.get(RECIPE_INGREDIENTS, None)
		#simple craft: add all the ingredients to the list
		if sub_ingredients:
			sub_ingredient_base_speed = speed / get_productivity(recipe, machine_stats, 1.0) / recipe[PRODUCT_COUNT]
			for sub_ingredient, count in sub_ingredients.items():
				add_ingredient_production(sub_ingredient, count * sub_ingredient_base_speed)
			#any recipe with alternate outputs needs to add its products as byproducts, if they haven't already been
			#	accounted for
			alternate_outputs = recipe.get(ALTERNATE_OUTPUTS, None)
			if alternate_outputs:
				produce_recipe(ingredient, speed - produced_recipes[ingredient])
		#recipe sequence craft: calculate how much of each recipe we need to get our desired ingredient at its speed
		elif recipe_ingredients:
			#start by calculating the products we get per initial recipe craft
			#start that by producing the ingredients for one initial recipe craft
			ingredient_productions = dict([next(iter(RECIPES[recipe_ingredients[0]][INGREDIENTS].items()))])
			recipe_productions = {}
			#go through each recipe in the sequence to convert ingredients into our desired final ingredient
			for recipe_name in recipe_ingredients:
				next_recipe = RECIPES[recipe_name]
				next_ingredients = next_recipe[INGREDIENTS]
				#each recipe consumes at least one of the ingredients already produced
				produced_ingredient = next(
					ingredient for ingredient in next_ingredients if ingredient in ingredient_productions)
				#scale production of the recipe to make its consumption match previous production
				scale_factor = \
					(ingredient_productions[produced_ingredient]
						/ next_ingredients[produced_ingredient]
						#and then factor in productivity
						* get_productivity(next_recipe, machine_stats, 1.0))
				del ingredient_productions[produced_ingredient]
				recipe_productions[recipe_name] = scale_factor
				#update productions
				for sub_ingredient, count in next_recipe[ALTERNATE_OUTPUTS].items():
					ingredient_productions[sub_ingredient] = \
						ingredient_productions.get(sub_ingredient, 0) + count * scale_factor
			#we now know the products we get per initial recipe craft
			#calculate how many of each recipe we need and update productions
			scale_factor = speed / ingredient_productions[ingredient]
			for recipe_name in recipe_ingredients:
				recipe_speed = recipe_productions[recipe_name] * scale_factor
				add_ingredient_production(recipe_name, recipe_speed)
				produce_recipe(recipe_name, recipe_speed)

	return net_machine_speeds

#remove any machine speeds if they're only used in a single recipe, we'll show the speeds directly as part of that recipe
def prune_single_use_ingredients(desired_output, net_machine_speeds):
	pruned_net_machine_speeds = {}
	ingredient_recipe_use_counts = {}
	for ingredient in net_machine_speeds:
		recipe = RECIPES[ingredient]
		for sub_ingredient in recipe.get(INGREDIENTS, EMPTY_DICT):
			ingredient_recipe_use_counts[sub_ingredient] = ingredient_recipe_use_counts.get(sub_ingredient, 0) + 1
		#keep recipes with alternate outputs
		if ALTERNATE_OUTPUTS in recipe:
			pruned_net_machine_speeds[ingredient] = net_machine_speeds[ingredient]

	#keep ingredients in our desired output
	for ingredient in desired_output:
		pruned_net_machine_speeds[ingredient] = net_machine_speeds[ingredient]
		ingredient_recipe_use_counts.pop(ingredient, None)
	#keep ingredients used in more than one recipe, and all resources
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
	#print sub-ingredients if specified, and always print ingredients that are produced where they are used
	if print_sub_ingredients or ingredient in INTEGRATED_INGREDIENTS:
		for sub_ingredient, sub_count in recipe.get(INGREDIENTS, EMPTY_DICT).items():
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
	for ingredient, speed in ordered_ingredients:
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

	#apply recipe adjustments as needed
	def add_extra_resources(resource_names, machine):
		for extra_resource in resource_names:
			old_recipes[extra_resource] = RECIPES[extra_resource]
			add_item(extra_resource, machine = machine)
			INGREDIENTS_LIST.pop()
	add_extra_resources(extra_resources, RESOURCE)
	add_extra_resources(extra_fluid_resources, FLUID_RESOURCE)

	#print desired output and machine speeds for one or more sets of desired outputs
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

	#restore recipes to what they were before
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
print_desired_output_and_machine_speeds(
	{ADVANCED_CIRCUIT: 45}, MEGABASE, extra_resources = [CABLE], extra_fluid_resources = [PETROLEUM])
print_desired_output_and_machine_speeds(
	{SPACE_PROCESSING: 0.125, SPACE_ADVANCED_CIRCUIT: 0.125, SPACE_MODULE_2: 0.1}, SA_SPACE_PLATFORM)
print_desired_output_and_machine_speeds({SA_MODULE_3: 0.5}, SA_MEGABASE)
print_desired_output_and_machine_speeds({SA_CRYO_SCIENCE: 600}, SA_MEGABASE)
