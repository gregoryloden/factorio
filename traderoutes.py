import sys
from decimal import Decimal

class Item:
	def __init__(self, name):
		self.name = name
		self.trades = {}
		self.next_trade = None

class Trade:
	def __init__(self, from_item, to_item, ratio, consumption, yes_siphon):
		self.from_item = from_item
		self.to_item = to_item
		self.ratio = ratio
		self.consumption = consumption
		self.yes_siphon = yes_siphon

class Siphon:
	def __init__(self, trade):
		self.trade = trade
		self.consumption = trade.consumption
		self.production = trade.consumption * trade.ratio
		self.siphon = 0
		self.last_siphon = None
		self.next_siphon = None
		self.last_yes_siphon = None
		self.next_yes_siphon = None

	def printout(self):
		consumption_percentage = str(int(self.consumption * 100 / self.trade.consumption)).rjust(3)
		consumption = decimal_str(self.consumption)
		production_for_trade = decimal_str(self.production - self.siphon)
		siphon = decimal_str(self.siphon)
		return f"{consumption_percentage}% {consumption} -> {production_for_trade} + {siphon}"

class TradeRoute:
	def __init__(self, trades, ratio):
		self.trades = trades
		(self.siphons, self.has_siphons) = TradeRoute.compute_siphon_trades(trades)
		self.ratio = float(ratio)
		self.avg = self.ratio ** (1 / len(trades))

	@staticmethod
	def compute_siphon_trades(trades):
		siphons = [Siphon(trade) if trade.consumption is not None else None for trade in trades]
		if not all(siphons) or not any(siphon.trade.yes_siphon for siphon in siphons):
			return (siphons, False)
		TradeRoute.link_siphons(siphons)
		TradeRoute.compute_consumption_production(siphons)
		TradeRoute.compute_basic_siphons(siphons)
		TradeRoute.enforce_nosiphon(siphons)
		TradeRoute.redistribute_siphons(siphons)
		return (siphons, True)

	@staticmethod
	def link_siphons(siphons):
		siphons_count = len(siphons)
		for (i, siphon) in enumerate(siphons):
			siphon.last_siphon = siphons[(i - 1) % siphons_count]
			siphon.next_siphon = siphons[(i + 1) % siphons_count]
		yes_siphons = [siphon for siphon in siphons if siphon.trade.yes_siphon]
		yes_siphons_count = len(yes_siphons)
		for (i, yes_siphon) in enumerate(yes_siphons):
			yes_siphon.last_yes_siphon = yes_siphons[(i - 1) % yes_siphons_count]
			yes_siphon.next_yes_siphon = yes_siphons[(i + 1) % yes_siphons_count]

	@staticmethod
	def compute_consumption_production(siphons):
		siphon = siphons[-1]
		last_modified = siphons[0]
		while True:
			last_siphon = siphon.last_siphon
			if last_siphon.production < siphon.consumption:
				siphon.consumption = last_siphon.production
				siphon.production = siphon.consumption * siphon.trade.ratio
				last_modified = siphon
			elif siphon is last_modified:
				break
			siphon = last_siphon

	@staticmethod
	def compute_basic_siphons(siphons):
		for siphon in siphons:
			siphon.siphon = siphon.production - siphon.next_siphon.consumption

	@staticmethod
	def enforce_nosiphon(siphons):
		siphon = siphons[-1]
		last_modified = siphons[0]
		while True:
			last_siphon = siphon.last_siphon
			if not siphon.trade.yes_siphon and siphon.siphon > 0:
				siphon.production = siphon.next_siphon.consumption
				siphon.siphon = Decimal(0)
				siphon.consumption = siphon.production / siphon.trade.ratio
				last_siphon.siphon = last_siphon.production - siphon.consumption
				last_modified = siphon
			elif siphon is last_modified:
				break
			siphon = last_siphon

	@staticmethod
	def redistribute_siphons(siphons):
		siphon = siphons[-1]
		while not siphon.trade.yes_siphon:
			siphon = siphon.last_siphon
		last_modified = siphon.next_yes_siphon
		while True:
			next_siphon = siphon.next_yes_siphon
			if siphon.siphon < next_siphon.siphon:
				#go backwards to find the siphon with the lowest siphon
				while siphon.last_yes_siphon.siphon <= siphon.siphon:
					siphon = siphon.last_yes_siphon
				#go forwards to find the siphon with the highest siphon
				end_siphon = next_siphon
				while end_siphon.next_yes_siphon.siphon >= end_siphon.siphon:
					end_siphon = end_siphon.next_yes_siphon
				#collect all the siphons with their ratios
				total_siphon = siphon.siphon
				total_distribution = 1
				current_ratio = 1
				next_siphon = siphon
				next_siphons = []
				while next_siphon is not end_siphon:
					next_siphon = next_siphon.next_siphon
					next_siphons.append(next_siphon)
					current_ratio *= next_siphon.trade.ratio
					if next_siphon.trade.yes_siphon:
						total_siphon += next_siphon.siphon / current_ratio
						total_distribution += 1 / current_ratio
				#distribute the siphon
				each_siphon = total_siphon / total_distribution
				siphon.siphon = each_siphon
				for next_siphon in next_siphons:
					next_siphon.consumption = siphon.production - siphon.siphon
					next_siphon.production = next_siphon.consumption * next_siphon.trade.ratio
					if next_siphon.trade.yes_siphon:
						next_siphon.siphon = each_siphon
					siphon = next_siphon
				last_modified = end_siphon
			elif siphon is last_modified:
				break
			siphon = siphon.last_yes_siphon

def decimal_str(d):
	d = d.quantize(Decimal("0.0001")).normalize()
	return str(d if d.as_tuple()[2] <= 0 else d.quantize(Decimal(1)))

MIN_RATIO = Decimal(sys.argv[2])

items = {}
reading_items = True
trade_routes = []

with open(sys.argv[1], "r") as file:
	for (i, line) in enumerate(file.readlines()):
		line = line.rstrip()
		try:
			if line.startswith("--") or line.startswith("\t") or line == "":
				continue
			if reading_items:
				if line == "*":
					reading_items = False
				else:
					items[line] = Item(line)
			else:
				from_name, to_name, ratio, *other_trade_details = line.split(" ")
				from_item = items[from_name]
				ratio = Decimal(ratio)
				old_trade = from_item.trades.get(to_name, None)
				if old_trade is None or old_trade.ratio < ratio:
					to_item = items[to_name]
					consumption = None
					yes_siphon = True
					try:
						consumption = Decimal(other_trade_details[0])
						yes_siphon = other_trade_details[1] != "nosiphon"
					except:
						pass
					from_item.trades[to_name] = Trade(from_item, to_item, ratio, consumption, yes_siphon)
		except:
			print(f"Error on line {(i + 1)}: {line}")
			raise

#The given item has its trade route in a linked list
def add_found_trade_route(original_item):
	ratio = Decimal(1)
	trades = []
	item = original_item
	while True:
		ratio *= item.next_trade.ratio
		trades.append(item.next_trade)
		item = item.next_trade.to_item
		if item is original_item:
			break
	if ratio >= MIN_RATIO:
		trade_routes.append(TradeRoute(trades, ratio))

def extend_trade_routes(original_item, current_item):
	for (_, trade) in current_item.trades.items():
		current_item.next_trade = trade
		if trade.to_item is original_item:
			add_found_trade_route(original_item)
		elif trade.to_item.next_trade is None:
			extend_trade_routes(original_item, trade.to_item)
	current_item.next_trade = None

for (_, item) in items.items():
	extend_trade_routes(item, item)
	#Disable this item from being used in any future trade routes, as they have already been discovered
	item.next_trade = False

#Print out all the items and their individual trades
for (_, item) in items.items():
	print(item.name)
	for (to_name, trade) in item.trades.items():
		print(f"   -> {to_name}: {trade.ratio}")
print("\n")

#Print out all the trade routes
trade_routes.sort(key=lambda trade_route: trade_route.ratio)
for trade_route in trade_routes:
	print(
		f"Trade route {trade_route.ratio:.4f}".ljust(22) +
		f"avg {trade_route.avg:.4f}".ljust(18) +
		("---- siphon ----" if trade_route.has_siphons else ""))
	for (trade, siphon) in zip(trade_route.trades, trade_route.siphons):
		print(
			f"    {trade.from_item.name} -> {trade.to_item.name}: {trade.ratio}".ljust(40) +
			(siphon.printout() if trade_route.has_siphons else ""))
