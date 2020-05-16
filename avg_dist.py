import json
import ijson
import pandas as pd

dists = ['1', '2', '3', '4', '5', '6', '7']

def avg_dist(dist_data, bus_data, city, category):
    new_dict = {}
    for d in dists:
        new_dict[d] = {}
        for key in dist_data[0][d]:
            l = dist_data[0][d][key]
            new_rest = bus_data[bus_data.business_id.isin(l)]
            avg = new_rest.stars.mean()
            new_dict[d][key] = avg

    with open('yelp_dataset/' + city + '_' + category + '_Avg_Rating.json', 'w') as f:
        json.dump(new_dict, f)

def main():
    cats = ['Home Services', 'Restaurants', 'Shopping']
    cities = ['Charlotte', 'Pittsburgh', 'Phoenix']

    for city in cities:
        for cat in cats:
            print('---processing {city}\'s {cat}'.format(city = city, cat = cat))
            bus_file = 'yelp_dataset/' + city + '_' + cat + '.json'
            bus_data = pd.read_json(bus_file, orient = 'records')
            if city == 'Phoenix':
                dist_data = [{}]
                for dist in dists:
                    dist_file ='yelp_dataset/' + city + '_' + cat + '_distance_' + dist + '.json'
                    with open(dist_file) as f:
                        data = f.readlines()
                        data = list(map(json.loads, data))
                        data[0] = {dist: data[0]}
                        dist_data[0].update(data[0])
                print(len(dist_data[0]))
            else:
                dist_file ='yelp_dataset/' + city + '_' + cat + '_distance.json'
                with open(dist_file) as f:
                    dist_data = f.readlines()
                    dist_data = list(map(json.loads, dist_data))

            avg_dist(dist_data, bus_data, city, cat)

main()