import {RefObject} from "react";

function geocodeLatLng(
  geocoder: google.maps.Geocoder,
  map: google.maps.Map,
  infowindow: google.maps.InfoWindow,
  center: google.maps.LatLngLiteral,
  startInput: HTMLInputElement
) {
  geocoder
    .geocode({ location: center })
    .then((response) => {
      if (response.results[0]) {
        map.setZoom(11);

        const marker = new google.maps.Marker({
          position: center,
          map: map,
        });

        infowindow.setContent(response.results[0].formatted_address);
        infowindow.open(map, marker);

        startInput.value = response.results[0].formatted_address
      } else {
        window.alert("No results found");
      }
    })
    .catch((e) => window.alert("Geocoder failed due to: " + e));
}

export default geocodeLatLng
