from geopy.geocoders import Nominatim
import folium

geolocator = Nominatim(user_agent="https://odisee.be")
city_country = "Leuven, Belgium"
location = geolocator.geocode(city_country)
print(location.address)
devnet_lat = location.latitude
devnet_lon = location.longitude
print((devnet_lat, devnet_lon))
# Coördinaten bundelen en interactieve kaart centreren
coordinates = [devnet_lat, devnet_lon]
map = folium.Map(location=coordinates, tiles="OpenStreetMap", zoom_start=12)
map

# De save-methode van het Map-object maakt de kaart aan
# Opgeslagen in Downloads (of werkmap)
map.save("geopy_location.html")
map