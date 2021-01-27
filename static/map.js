
// initialize Leaflet
var map = L.map('map').setView({ lon: 25.72088, lat: 62.24147 }, 15.5);

// add the OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
}).addTo(map);

// show the scale bar on the lower left corner
L.control.scale().addTo(map);

// popup to marker
var pop = L.popup({});
pop.setContent('<form method="POST" action="/save">\
{{ form.csrf_token }}\
{{ form.firstname.label}} {{ form.firstname(size=20) }}<br/>\
{{ form.surname.label}} {{ form.surname(size=20) }}<br/>\
{{form.email.label}} {{form.email}}\
{{form.file}}\
<input type="submit" value="Go">\
</form>');

 //show a marker on the map
{% for item in hive_locations %}
  L.marker({{item | tojson}}).bindPopup(pop).addTo(map);
{% endfor %}

//Array of all the markers that we create
var allMarkers = [];

// Function saves beehive's location to database and to local map
function savePopup() {
  //Data that we want to send to server and save as a beehive location
  var data = document.getElementById("edit").value;

  //HTTP request to server
  var request = new XMLHttpRequest();
  request.open('POST', '/save', true);
  request.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  request.send(data);
  alert(data + ' was saved to database!')
  saveValue()
}

function saveValue() {
  document.getElementById("loc").innerHTML = document.getElementById("edit").value

}

//Create GeoJSON layer for user generated data
var drawnItems = new L.geoJson();
//Add GeoJSON layer to map
map.addLayer(drawnItems);

// Leaflet draw event
map.on('dblclick', function (e) {
  var marker = L.marker(e.latlng).addTo(map);
  var markerpopup = L.popup({});
  //Set popup lat lng where clicked
  markerpopup.setLatLng(e.latlng);
  //lat lng where clicked to string
  var placement = e.latlng.toString()
  //Set popup content
  markerpopup.setContent('<form method="POST" action="/save">\
{{ form.csrf_token }}\
{{ form.firstname.label}} {{ form.firstname(size=20) }}<br/>\
{{ form.surname.label}} {{ form.surname(size=20) }}<br/>\
{{form.email.label}} {{form.email}}\<br/>\
{{form.comment.label}} {{form.comment}}\
{{form.file}}\<br/>\
<input type="submit" value="Go" onClick="console.log("hello")"><br/>\
<a class="twitter-timeline" href="https://twitter.com/twitterapi" ><img src="https://logos-world.net/wp-content/uploads/2020/04/Twitter-Logo.png" class="twt" alt="Twitter" style="width:62px;height:42px;"</a>\
<iframe class="tweet" id=tweet_493851197649207296 border=0 frameborder=0 height=250 width=550 src=https://twitframe.com/show?url=https://twitter.com/gideontailleur/status/493851197649207296></iframe>\
</form>');
  //Bind marker popup
  marker.bindPopup(markerpopup,{
maxWidth : 560,
maxHeight: 560
});
  //Add marker to geojson layer
  drawnItems.addLayer(marker);

  allMarkers.push(marker)
});

// Functin to delete a beehive in the map
/* function deletePopup() {
  map.removeLayer(drawnItems)

  var request = new XMLHttpRequest();
  request.open('DELETE', '/delete', true);
  request.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  request.send(data);
  alert('Marker was saved to database!')
} */
