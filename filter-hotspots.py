# hotspots := 10% businesses in each city
# rating >= rating_threshold && review_count >= review_count_thresholds
import json

# global constants
CHARLOTTE = "Charlotte"
PHOENIX = "Phoenix"
PITTSBURGH = "Pittsburgh"

cities = [CHARLOTTE, PHOENIX, PITTSBURGH]
categories = ['Restaurants', 'Shopping', 'Home_Services']

rating_threshold = 4.5
review_count_thresholds = {
    CHARLOTTE: 11,
    PHOENIX: 18,
    PITTSBURGH: 13
}

def main():
    for city in cities:
        for category in categories:
            getHotspots(city, category)


def getHotspots(city, category):
    ''' city-category.json but only hotspots '''

    data_file = "./yelp_dataset/" + city + "_" + category + ".json"

    with open(data_file, 'r') as f:
        parsed_json = json.load(f)

    hotspots_array = filter(isHotspot, parsed_json)
    hotspots_obj = {}

    for business in hotspots_array:
        key = business['business_id']
        value = {
            'name': business['name'],
            'latitude': business['latitude'],
            'longitude': business['longitude'],
            'address': business['address'],
            'city': business['city'],
            'state': business['state'],
            'stars': business['stars'],
            'review_count': business['review_count'],
            'is_open': business['is_open']}
        hotspots_obj[key] = value

        with open('./yelp_dataset/' + city + '_' + category + '_hotspots.json', 'w') as f:
            json.dump(hotspots_obj, f)


def isHotspot(city, business):
    '''
    business =   { 'business_id': 'vjTVxnsQEZ34XjYNS-XUpA', ... }
    '''
    rating = business['stars']
    review_count = business['review_count']

    if rating >= rating_threshold and review_count <= review_count_thresholds[city]:
        return True
    else:
        return False
