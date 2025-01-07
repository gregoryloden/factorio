import random
import math

LEVELS = 5
MAX_LEVEL = LEVELS - 1
PRODUCTIVITY = {
	"normal": 0.1,
	"legendary": 0.25,
}
QUALITY = {
	"normal": 0.025,
	"rare": 0.04,
	"epic": 0.0475,
	"legendary": 0.0625,
}
MACHINE_SPECS = {
	"electromagnetic plant": {"slots": 5, "base productivity": 0.5},
	"assembling machine": {"slots": 4, "base productivity": 0},
	"cryochamber": {"slots": 8, "base productivity": 0},
}
SINGLE_LOOP_MACHINE_SPECS = {
	"recycler": {"slots": 4, "return chance": 0.25},
	"crusher": {"slots": 2, "return chance": 0.8},
}

def math_test(p, q, lp, rq, sp, sq, rc):
	def add_and_distribute_quality(amounts, initial_amount, level, dq):
		quality_amount = initial_amount * dq
		amounts[level] += initial_amount - quality_amount
		amounts[level + 1] += quality_amount
		for i in range(level + 1, MAX_LEVEL):
			quality_amount *= 0.1
			amounts[i] -= quality_amount
			amounts[i + 1] += quality_amount
	#calculate starting products from 1 set of inputs
	products = [0] * LEVELS
	add_and_distribute_quality(products, 1 + sp, 0, sq)
	#the ratio of same-level products after recycle and re-craft is the same across all levels
	scale_factor = 1 / (1 - rc * (1 - rq) * (1 + p) * (1 - q))
	ingredients = [0] * LEVELS
	for level in range(MAX_LEVEL):
		base_amount = products[level]
		products[level] = 0
		#recycle
		new_ingredients = [0] * LEVELS
		add_and_distribute_quality(new_ingredients, base_amount * rc, level, rq)
		#re-craft
		new_products = [0] * LEVELS
		new_products[MAX_LEVEL] = new_ingredients[MAX_LEVEL] * (1 + lp)
		for craft_level in range(level, MAX_LEVEL):
			add_and_distribute_quality(new_products, new_ingredients[craft_level] * (1 + p), craft_level, q)
		#add products and consumed ingredients to the totals, scaled based on how many were consumed by recycling and
		#	re-crafting
		new_products[level] = 0
		for add_level in range(level, LEVELS):
			products[add_level] += new_products[add_level] * scale_factor
			ingredients[add_level] += new_ingredients[add_level] * scale_factor
	return {"inputs/legendary": 1 / products[MAX_LEVEL], "re-craft rates": ingredients}

def simulate_test(n, m, base_p, qn, p, q, base_quality):
	def level_apply_quality(level, aq):
		val = random.random()
		while val < aq and level < MAX_LEVEL:
			level += 1
			val *= 10
		return level
	pn = m - qn
	lp = base_p + p * m
	rq = q * 4
	p = base_p + p * pn
	q = q * qn
	sp = (p if base_quality else lp)
	sq = (q if base_quality else 0)
	products = [0] * LEVELS
	bonus = [0] * LEVELS
	total_products = 0
	#craft initial products we have
	bonus[0] = n * sp
	initial_bonus_products = int(bonus[0])
	total_initial_products = n + initial_bonus_products
	#yes base quality means that we used the same machine as the loop will use, so adjust the bonus
	if base_quality:
		bonus[0] -= initial_bonus_products
	#no base quality means that we used a different machine from what the loop will use, so delete any bonus
	else:
		bonus[0] = 0
	for i in range(total_initial_products):
		products[level_apply_quality(0, sq)] += 1
	#recycle and re-craft each level of products until there are none left at that level
	for base_level in range(MAX_LEVEL):
		while products[base_level] > 0:
			ln = products[base_level]
			products[base_level] = 0
			total_products += ln
			for _ in range(ln):
				#recycle product
				if random.random() >= 0.25:
					continue
				level = level_apply_quality(base_level, rq)
				#re-craft: pure productivity if legendary, otherwise quality + productivity
				if level == MAX_LEVEL:
					bonus[MAX_LEVEL] += lp
					products[MAX_LEVEL] += 1
				else:
					bonus[level] += p
					products[level_apply_quality(level, q)] += 1
			bonus_products = int(bonus[base_level])
			products[base_level] += bonus_products
			bonus[base_level] -= bonus_products
	legendary = products[MAX_LEVEL] + int(bonus[MAX_LEVEL])
	total_products += legendary
	inputs_per_legendary = math.ceil(n/legendary)
	products_per_legendary = math.ceil(total_products/legendary)
	math_result = math_test(p, q, lp, rq, sp, sq, 0.25)
	math_inputs_per_legendary = math_result["inputs/legendary"]
	re_craft_rates = [f"{rate * 100:.2f}%" for rate in math_result["re-craft rates"]]
	print(f"\t{qn}x qu, {pn}x pr"
		+ f": {n} | {total_products:8} | {legendary:9}"
		+ f" | {inputs_per_legendary:3} ({math_inputs_per_legendary:>6.2f}) |{products_per_legendary:4}"
		+ f" | [{", ".join(re_craft_rates)}]")

def test_configuration(n, machine=None, pmodules=None, qmodules=None, base_quality=True):
	ms = MACHINE_SPECS[machine]
	p = PRODUCTIVITY[pmodules]
	q = QUALITY[qmodules]
	m = ms["slots"]
	base_p = ms["base productivity"]
	print(f"\nTesting {m} module slots, +{base_p} base productivity, {"with" if base_quality else "without"} base quality"
		+ f"\n    +{p:.4f} {pmodules} productivity modules\n    +{q:.4f} {qmodules} quality modules"
		+ f"\n                      inputs | products | legendary | i/l  (math)  | p/l | re-craft rates")
	for i in range(m + 1):
		simulate_test(n, m, base_p, i, p, q, base_quality)

def single_loop_test(machine=None, qmodules=None):
	slms = SINGLE_LOOP_MACHINE_SPECS[machine]
	q = QUALITY[qmodules] * slms["slots"]
	rc = slms["return chance"]
	math_inputs_per_legendary = math_test(0, 0, 0, q, 0, 0, rc)["inputs/legendary"]
	print(f"\n{machine} with +{q:.4f} {qmodules} quality modules: {math_inputs_per_legendary} inputs/legendary")

print("\n")
test_configuration(100_000, machine="electromagnetic plant", pmodules="legendary", qmodules="legendary")
test_configuration(100_000, machine="assembling machine", pmodules="legendary", qmodules="legendary")
test_configuration(100_000, machine="cryochamber", pmodules="legendary", qmodules="legendary")
test_configuration(100_000, machine="electromagnetic plant", pmodules="legendary", qmodules="legendary", base_quality=False)
single_loop_test(machine="recycler", qmodules="legendary")
single_loop_test(machine="crusher", qmodules="legendary")
