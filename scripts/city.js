// Global attributes
var city = parent.document.URL.substring(parent.document.URL.indexOf('?')+6, parent.document.URL.length);
var category = "Restaurants";

var radiusMile = 3;
var radiusMeter = milesToMeters(radiusMile);

var map = null;
var zoom = 13; // TODO: set zoom to user-adjusted value

var circleLayer = L.featureGroup();

var hotspots = null;

var root = "./"
// var root = "../"

function milesToMeters(miles) {
  return miles * 1609.34;
}

getHotspots(city, category)
// wait 2 seconds for hotspots to finish
// setTimeout(loadData,2000)
loadData(city, category)

function readableCategory(category) {
    if (category === "Shopping") {
        return "Shopping Centers";
    } else if (category === "Home_Services") {
        return "Home Services";
    } else {
        return category;
    }
}

function changeCategory() {
    var dropdown = document.getElementById("dropdown");
    var opt = dropdown.options[dropdown.selectedIndex];
    category = opt.value;
    circleLayer.clearLayers(); // gets rid of circles on previous pages
    document.getElementById("summary").style.visibility = 'hidden'; // rehides summary
    // document.getElementById('summary_param1').innerHTML = readableCategory(category); // category for summary statement
    loadData(city, category);
}

function changeRadius() {
    var slider = document.getElementById("myRange");
    radiusMile = slider.value;
    radiusMeter = milesToMeters(radiusMile);
    console.log('radiusMile: ', radiusMile);
    console.log('radiusMeter: ', radiusMeter);
    // document.getElementById('summary_param2').innerHTML = document.getElementById("myRange").value; // radius for summary statement
}

function getHotspots(city, category) {
    // get hotspots obj
    var filename = root + 'yelp_dataset/' + city + '_' + category + '_hotspots.json';
    console.log('getting hot spots')
    $.getJSON(filename, function(data) {
      hotspots = JSON.parse(JSON.stringify(data));
      console.log('hotspots set')
    });
  }

function loadData(city, category) {
  console.log('loading data')

    var param1 = readableCategory(category);
    document.getElementById("heading_param1").innerHTML = param1;
    document.getElementById("heading_param2").innerHTML = city;

    // getHotspots(city, category);


    if (city === "Phoenix") {
        console.log("here");
        document.getElementById("home_services").hidden = true;
    } else {
        document.getElementById("home_services").hidden = false;
    }

    var data_file = root + "yelp_dataset/" + city + "_" + category + ".json";
    d3.json(data_file, function(data) {

        if (map != undefined && map != null) {
            map.remove();
        }

        // default lat and long based on city
        var defaultView;
        if (city === "Phoenix") {
            defaultView = [33.460863, -112.070160];
        } else if (city === "Pittsburgh") {
            defaultView = [40.439709, -79.993892];
        } else if (city === "Charlotte") {
            defaultView = [35.225508, -80.842045];
        }

        map = L.map('map').setView(defaultView, zoom);
        map._initPathRoot();
        map._updatePathViewport();
        map.addLayer(circleLayer);

        var mapLink =
                '<a href="http://openstreetmap.org">OpenStreetMap</a>';
            L.tileLayer.grayscale(
                'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; ' + mapLink + ' Contributors',
                maxZoom: 18,
                }).addTo(map);

        // var businesses = L.layerGroup();
        console.log('using data')
        for (n in data) {
            long = data[n]['longitude'];
            lat = data[n]['latitude'];
            name = data[n]['name'];
            rating = data[n]['stars'];
            business_id = data[n]['business_id'];
            var ratingColor = '#d23837';
            if (rating <= 1.5) {
                ratingColor = '#d23837';
            } else if (rating <= 2.5) {
                ratingColor = '#e17a3c';
            } else if (rating <= 3.5) {
                ratingColor = '#f0ce4b';
            } else if (rating <= 4.5) {
                ratingColor = '#80af54';
            } else if (rating <= 5.0) {
                ratingColor = '#387e53';
            }
            var markerHtmlStyles = null;
            if (!(business_id in hotspots)) { // regular
              markerHtmlStyles = `background-color: ${ratingColor};
                                      width: 1rem;
                                      height: 1rem;
                                      display: block;
                                      left: -.25rem;
                                      top: -.25rem;
                                      position: relative;
                                      border-radius: 1rem 1rem 0;
                                      transform: rotate(45deg);
                                      border: 1px solid #FFFFFF;
                                      opacity: 0.9`;
            } else { // hotspot
              markerHtmlStyles = `background-color: ${ratingColor};
                                      width: 1.1rem;
                                      height: 1.1rem;
                                      display: block;
                                      left: -.25rem;
                                      top: -.25rem;
                                      position: relative;
                                      border-radius: 1rem 1rem 0;
                                      transform: rotate(45deg);
                                      border: 1px solid #000000;
                                      border-width: thick`;
            }
            var bussiness_icon = L.divIcon({html: `<span style="${markerHtmlStyles}" />`});
            var marker = L.marker([lat, long], {icon: bussiness_icon, alt: business_id}).addTo(map).bindPopup(name);

            // hovering over marker adds business name popup
            marker.on('mouseover',function(e) {
                e.target.openPopup();
            });

            console.log('using hotspots')
            if (business_id in hotspots) { // hotspots are clickable
              marker.on('click', function(e) {
                console.log('clicked')
                  var marker_lat = e.latlng.lat;
                  var marker_long = e.latlng.lng;
                  var marker_business_id = e.target.options.alt;
                  var marker_name = e.target["_popup"]["_content"];
                  map.setView(e.target.getLatLng(), map.getZoom());

                  //  On click, draw circle, centered at marker, with radius
                  drawCircle(marker_lat, marker_long);
                  updateAvg(city, category, marker_business_id, radiusMile);

                  // generate summary statement
                  document.getElementById("summary").style.visibility = 'visible';
                  document.getElementById('summary_param1').innerHTML = param1; // category for summary statement
                  document.getElementById('summary_param3').innerHTML = marker_name; // name of business for summary statement
              });
            }
        }
    });
}


function drawCircle(marker_lat, marker_long) {
  circleLayer.clearLayers();

  var circle = L.circle([marker_lat, marker_long], radiusMeter,
    { color : 'black', opacity : 1, fillColor : 'yellow', fillOpacity : .2} ).addTo(circleLayer);
}

function updateAvg(city, category, business_id, radiusMile) {
    var filename = root + "yelp_dataset/" + city + "_" + category + "_Avg_Rating.json";
    var rating;
    console.log(filename);
    $.getJSON(filename, function(data, error) {
        if (error) console.log(error);

        console.log(data);
        var json_data = JSON.parse(JSON.stringify(data));
        var r = radiusMile.toString();
        rating = json_data[r][business_id];
        console.log(rating);
        if (rating === undefined) {
            document.getElementById('summary_param4').innerHTML = "n/a";
        } else {
            document.getElementById('summary_param4').innerHTML = rating.toFixed(2); // rating for summary statement
        }
        document.getElementById('summary_param2').innerHTML = radiusMile;
    });

}
