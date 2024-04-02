import json, os, re, sys
from typing import List
import xml.etree.ElementTree as ET


data_dir = os.path.join(os.path.dirname(__file__), 'Vampires Dawn 3', 'www', 'data')


map_data = {}
with open(os.path.join(data_dir, 'MapInfos.json'), 'r', encoding='utf-8-sig') as file_in:
	map_infos = json.load(file_in)
	for map_info in map_infos:
		if map_info is not None:
			map_id = int(map_info['id'])
			map_data[map_id] = {'name': map_info['name']}

item_data = {}
with open(os.path.join(data_dir, 'Items.json'), 'r', encoding='utf-8-sig') as file_in:
	item_infos = json.load(file_in)
	for item_info in item_infos:
		if item_info is not None:
			item_id = int(item_info['id'])
			item_data[item_id] = item_info['name']

weapon_data = {}
with open(os.path.join(data_dir, 'Weapons.json'), 'r', encoding='utf-8-sig') as file_in:
	weapon_infos = json.load(file_in)
	for weapon_info in weapon_infos:
		if weapon_info is not None:
			weapon_id = int(weapon_info['id'])
			weapon_data[weapon_id] = weapon_info['name']

armor_data = {}
with open(os.path.join(data_dir, 'Armors.json'), 'r', encoding='utf-8-sig') as file_in:
	armor_infos = json.load(file_in)
	for armor_info in armor_infos:
		if armor_info is not None:
			armor_id = int(armor_info['id'])
			armor_data[armor_id] = armor_info['name']

# TODO
# from contextlib import nullcontext
# i = 0
# map_id = 46
# map = map_data[map_id]
# with nullcontext() as ctx:
for i, (map_id, map) in enumerate(map_data.items()):
	print(f'Processing map {i+1}/{len(map_data)} ...')
	map_file = os.path.join(data_dir, f'Map{int(map_id):03d}.json')
	with open(map_file, 'r', encoding='utf-8-sig') as file_in:
		map_json = json.load(file_in)

		map['width'] = int(map_json['width'])
		map['height'] = int(map_json['height'])

		map['teleports'] = []	
		map['items'] = []
		map['hiddenPassages'] = []
		map['traps'] = []
		map['events'] = []

		for event in map_json['events']:
			if event is None:
				continue

			# print(f'Processing event {event['id']} ...')
			x = int(event['x'])
			y = int(event['y'])

			hasTeleport = False
			items = []
			teleportParams = {}
			hasTrap = False
			hiddenPassage = -1
			lockLevel = 0
			searchSkill = 0
			readMapSkill = 0

			pages: dict = event['pages']

			for page in pages:
				conditions: dict = page['conditions']
				switch1Id = int(conditions['switch1Id'])
				if switch1Id == 66 and page['image']['characterName'] == '!Anim_sonstiges4':
					hiddenPassage = int(page['image']['direction'])

				for command in page['list']:
					code = int(command['code'])
					params = command['parameters']
					condition = int(command['indent']) > 0

					# Change Gold = 125, params = [(0=Increase |1=Decrease), (0=Constant | 1=Variable), (Ammount | VariableID)]
					if code == 125:
						if int(params[0]) == 0:
							ammount = int(params[2])
							items.append({'name': 'Filar', 'ammount': ammount, 'hasCondition': condition})

					# Change Items = 126, params = [ItemID, (0=Increase |1=Decrease), (0=Constant | 1=Variable), (Ammount | VariableID)]
					if code == 126:
						if int(params[1]) == 0:
							item_id = int(params[0])
							ammount = int(params[3])
							items.append({'name': item_data.get(item_id, '???'), 'ammount': ammount, 'hasCondition': condition})

					# Change Weapons = 127, params = [ItemID, (0=Increase |1=Decrease), (0=Constant | 1=Variable), (Ammount | VariableID)]
					if code == 127:
						if int(params[1]) == 0:
							weapon_id = int(params[0])
							ammount = int(params[3])
							items.append({'name': weapon_data.get(weapon_id, '???'), 'ammount': ammount, 'hasCondition': condition})

					# Change Armors = 128, params = [ItemID, (0=Increase |1=Decrease), (0=Constant | 1=Variable), (Ammount | VariableID)]
					if code == 128:
						if int(params[1]) == 0:
							armor_id = int(params[0])
							ammount = int(params[3])
							items.append({'name': armor_data.get(armor_id, '???'), 'ammount': ammount, 'hasCondition': condition})

					# CallEvent = 117
					if code == 117:
						# 40 SyrakonKleinBelohnung
						# 41 SyrakonMittelBelohnung
						# 42 SyrakonGroßBelohnung
						# 55 SargLoot
						# 71 GeheimgangSchatz
						# 72 Regalschatz
						# 73 Bodenschatz
						# 74 Artefakttruhe
						# 75 ArtefaktTruheSchluessel
						# 76 ArtefaktWaffeLoot
						# 77 ArtefaktRuestungLoot
						# 78 ArtefaktAccessoirLoot
						
      					# 85 GeheimOrtEntdeckt
						# 101 Falle
						# 113 GeheimOrtKompass
						called_common_event_id = int(command['parameters'][0])
						if called_common_event_id in {40, 41, 42, 55, 71, 72, 73, 74, 75, 76, 77, 78}:
							items.append({'name': 'Schatz', 'ammount': 1, 'hasCondition': False})
						elif called_common_event_id == 101:
							hasTrap = True

					# Teleport = 201, params = [(0=Direct | 1=Variable), (MapId | VariableId), (X | VariableId), (Y | VariableId), Direction, FadeType]
					if code == 201:
						hasTeleport = True
						teleportParams ={'map': int(params[1]), 'x': int(params[2]), 'y': int(params[3])}

			if len(items) > 0:
				map['items'].append({'x': x, 'y': y, 'items': items, 'lockLevel': lockLevel, 'searchSkill': searchSkill})
			elif hasTeleport:
				map['teleports'].append({'from': {'x': x, 'y': y}, 'to': teleportParams})
			elif hiddenPassage >= 0 and hiddenPassage < 8:
				map['hiddenPassages'].append({'x': x, 'y': y, 'direction': hiddenPassage})
			elif hasTrap:
				map['traps'].append({'x': x, 'y': y})
			else:
				map['events'].append({'x': x, 'y': y})


json = json.dumps(map_data, separators=(',', ':'))		

outfilename = os.path.join(os.path.dirname(__file__), 'docs', 'map-data.js')
with open(outfilename, 'w', encoding='utf-8') as outfile:
	outfile.write('window.mapData = ')
	outfile.write(json)
	outfile.write(';')
	print(f'Created file {outfilename}')
