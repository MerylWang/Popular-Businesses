from distance_calculator import calculate_distances
import json
import ijson
import pandas as pd

def main():
	categories = 'Restaurants, Shopping, Home Services'.split(', ')
	cities = 'Phoenix, Las Vegas, Charlotte, Pittsburgh'.split(', ')
	states = ['AZ', 'NV', 'NC', 'PA']
	thresholds = {'Phoenix':18.0, 'Las Vegas': 77.0, 'Charlotte': 11.0, 'Cleveland': 13.0, 'Pittsburgh': 13.0}

	us_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
	          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
	          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
	          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
	          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

	print('---opening business dataset')
	with open('yelp_dataset/yelp_academic_dataset_business.json', encoding = 'utf-8') as json_file:
	    data = json_file.readlines()
	    data = list(map(json.loads, data))

	business = pd.io.json.json_normalize(data)

	replace_data(business)

	print('---filter non-US/non-categorized data')
	business = business[~business.categories.isna()]
	business = business[business.state.isin(us_states)]

	# Test
	for ix, city in enumerate(cities):
		for category in categories:
			gen_data(business, city, states[ix], category, thresholds)


def gen_data(data, city, state, category, thresholds):
	print('---generate data for {city}\'s {category}'.format(city = city, category = category))
	columns_to_keep = ['business_id', 'name', 'latitude', 'longitude', 'address', 'city', 'state', 'stars', 'review_count', 'is_open']
	filters = (data.city == city) & (data.state == state) & (data.categories.str.contains(category))

	new_data = data[filters]
	new_data = new_data[columns_to_keep]

	new_data.set_index('business_id')

	filename = 'yelp_dataset/' + '_'.join([city, category]) + '.json'

	new_data.to_json(filename, orient = 'records')
	gen_dist_data(new_data, city, state, category, thresholds)

def gen_dist_data(data, city, state, category, thresholds):
	print('---generate distance data for {city}\'s {category}'.format(city = city, category = category))
	filename = 'yelp_dataset/' + city + '_' + category + '_distance.csv'
	calculate_distances(data, filename, min_reviews = thresholds[city], json_write = False)

	print('---process/write distance data')
	dist = pd.read_csv(filename)
	hotspots = pd.unique(dist.id1)

	dist_to_write = {}

	for d in range(1, 8):
		dist_to_write[d] = {}
		for hotspot in hotspots:
			new_dist = dist[(dist.id1 == hotspot) & (dist.dist <= d)]
			filtered_list = list(pd.unique(new_dist.id2))
			dist_to_write[d][hotspot] = filtered_list

	with open('yelp_dataset/' + city + '_' + category + '_distance.json', 'w') as f:
		json.dump(dist_to_write, f)

def replace_data(business):
	business.city.str.replace('Phenoix', 'Phoenix')
	business.city.str.replace('Phenoix AZ', 'Phoenix')
	business.city.str.replace('Phoeniix', 'Phoenix')
	business.city.str.replace('Phoenix ', 'Phoenix')
	business.city.str.replace('Phoenix AZ', 'Phoenix')
	business.city.str.replace('Phoenix Metro Area', 'Phoenix')
	business.city.str.replace('Phoenix,', 'Phoenix')
	business.city.str.replace('Phoenix, AZ', 'Phoenix')
	business.city.str.replace('Phoneix', 'Phoenix')
	business.city.str.replace('Phonenix', 'Phoenix')
	business.city.str.replace('Phoniex', 'Phoenix')

def main_phase_2():
	cities = ["Phoenix", "Las Vegas"]
	states = ["AZ", "NV"]
	categories = 'Restaurants, Shopping, Home Services'.split(', ')

	for ix, city in enumerate(cities):
		for cat in categories:
			print('---generate distance data for {city}\'s {category}'.format(city = city, category = cat))
			process_dist(city, states[ix], cat)
			

def process_dist(city, state, category):
	filename = 'yelp_dataset/' + city + '_' + category + '_distance.csv'
	dist = pd.read_csv(filename)

	hotspots = pd.unique(dist.id1)
	dist_to_write = {}

	for d in range(1, 8):
		print('-processing {d} miles'.format(d = d))
		dist_to_write[d] = {}
		for hotspot in hotspots:
			new_dist = dist[(dist.id1 == hotspot) & (dist.dist <= d)]
			filtered_list = list(pd.unique(new_dist.id2))
			dist_to_write[d][hotspot] = filtered_list

		with open('yelp_dataset/' + city + '_' + category + '_distance_' + str(d) +'.json', 'w') as f:
			json.dump(dist_to_write[d], f)

main_phase_2()