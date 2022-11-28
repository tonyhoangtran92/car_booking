import {Dispatch, SetStateAction} from "react";
import {DestinationInfo} from "../components/Customer/Customer";

function calculateAndDisplayRoute(
  directionsService: google.maps.DirectionsService,
  directionsRenderer: google.maps.DirectionsRenderer,
  startInput: HTMLInputElement,
  endInput: HTMLInputElement,
  setDestinationInfo: Dispatch<SetStateAction<DestinationInfo>>
) {
  directionsService
    .route({
      origin: {
        query: startInput.value,
      },
      destination: {
        query: endInput.value,
      },
      travelMode: google.maps.TravelMode.DRIVING,
    })
    .then((response) => {
      setDestinationInfo(state => ({
        ...state,
        distance: response.routes?.[0]?.legs[0]?.distance?.value! / 1000
      }))
      directionsRenderer.setDirections(response);
    })
    .catch((e) => window.alert("Directions request failed due to " + e.status));
}

export default calculateAndDisplayRoute

