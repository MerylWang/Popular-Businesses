import json
import ijson
import pandas as pd

cities = ['Charlotte', 'Pittsburgh']
cats = ['Home Services', 'Shopping', 'Restaurants']
new_cats = ['Home_Services', 'Shopping', 'Restaurants']
dist = [str(i) for i in range(1, 8)]

for city in cities:
	for ix, cat in enumerate(cats):
		file_name = 'yelp_dataset/' + city + '_' + cat + '_distance' +'.json'
		with open(file_name) as f:
			data = f.readlines()
			data = list(map(json.loads, data))

		for d in dist:
			new_data = data[0][d]
			print(type(new_data))
			new_file = 'yelp_dataset/' + city + '_' + new_cats[ix] + '_distance_' + str(d) +'.json'

			with open(new_file, 'w') as file:
				json.dump(new_data, file)