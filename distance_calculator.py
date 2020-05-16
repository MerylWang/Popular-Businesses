import pandas as pd

from math import radians, cos, sin, atan2, sqrt
from time import perf_counter
import csv
import sys
import pdb

def haversine_distance(row1, row2):
    radius = 3959

    lon_sr, lat_sr = row1['longitude'], row1['latitude']
    lon_tg, lat_tg = row2['longitude'], row1['latitude']

    # Convert to radians
    lon_sr, lat_sr, lon_tg, lat_tg = map(radians, [lon_sr, lat_sr, lon_tg, lat_tg])

    dlon = lon_tg - lon_sr
    dlat = lat_tg - lat_sr

    a = sin(dlat/2)**2 + cos(lat_tg) * cos(lat_sr) * sin(dlon/2)**2
    
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = radius * c

    return d

def write_csv(output_file, rows):
    print('...writing distance file')
    with open(output_file, 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=['id1', 'id2', 'dist'],
            quotechar='"',
            quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

def write_json(input_csv, output_file):
    distance = pd.read_csv(input_csv)
    distance.to_json(output_file, orient = 'records')

def calculate_distances(business, output_file = 'yelp_dataset/ph_rest_distance.csv', min_stars = 4.5, min_reviews = 20, json_write = True):
    length = business.shape[0] # Length of the dataset.

    rows = []
    # pdb.set_trace()
    cities = list(pd.unique(business.city)) # List of unique cities.

    print('...computing distances')
    for ix, city in enumerate(cities):
        print('processing: ' + city + ' ' + str(ix+1) + '/' + str(len(cities)))
        condition = (business.city == city)
        business_in_city = business[condition]
        hot = (business.stars >= min_stars) & (business.review_count >= min_reviews)
        hot_business_in_city = business_in_city[hot]
        length = business_in_city.shape[0] # Length of the dataset.
        for i in range(hot_business_in_city.shape[0]):
            t1 = perf_counter()
            for j in range(length):
                dist = haversine_distance(hot_business_in_city.iloc[i], business_in_city.iloc[j])
                if dist > 0:
                    row = {'id1': hot_business_in_city.iloc[i].business_id}
                    row['id2'] = business_in_city.iloc[j].business_id
                    row['dist'] = dist
                    rows.append(row)
            print('time for round ' + str(i+1) + '/' + str(hot_business_in_city.shape[0]) + ': ' + str(perf_counter() - t1))
    
    write_csv(output_file, rows)
    if json_write:
        write_json(output_file, 'yelp_dataset/ph_rest_distance.json')

def main():
    input_data = 'yelp_dataset/phoenix_restaurants.csv'
    min_stars, min_reviews = 4.5, 30
    calculate_distances(input_data, min_stars = min_stars, min_reviews = min_reviews)