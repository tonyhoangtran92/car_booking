import {
  FC,
  ReactNode,
  useEffect,
  useRef,
  useState,
  MutableRefObject, Dispatch, SetStateAction
} from "react";
import useDeepCompareEffect from 'use-deep-compare-effect'
import calculateAndDisplayRoute from "../../../utils/calculateAndDisplayRoute";
import {DestinationInfo} from "../../Customer/Customer";

interface MapProps extends google.maps.MapOptions {
  departureRef: MutableRefObject<HTMLInputElement | null>;
  destinationRef: MutableRefObject<HTMLInputElement | null>;
  children?: ReactNode;
  setDepartureLocation: Dispatch<SetStateAction<google.maps.LatLngLiteral>>;
  setDestinationInfo: Dispatch<SetStateAction<DestinationInfo>>;
}

const EmptyMap: FC<MapProps> = ({
                                  departureRef,
                                  destinationRef,
                                  setDepartureLocation,
                                  setDestinationInfo,
                                  ...options}) => {
  const ref = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<google.maps.Map>();

  useDeepCompareEffect(() => {
    if (map) {
      map.setOptions(options);
    }
  }, [map, options]);

  useEffect(() => {
    if (ref.current && !map) {
      setMap(new window.google.maps.Map(ref.current, {}));
    }
  }, [ref, map]);

  useEffect(() => {
    if (map && departureRef.current) {
      // Create the search box and link it to the UI element.
      const departureBox = new google.maps.places.SearchBox(departureRef.current!);
      const destinationBox = new google.maps.places.SearchBox(destinationRef.current!);

      const directionsService = new google.maps.DirectionsService();
      const directionsRenderer = new google.maps.DirectionsRenderer();

      directionsRenderer.setMap(map);

      // Listen for the event fired when the user selects a prediction and retrieve
      // more details for that place.
      departureBox.addListener("places_changed", () => {
        const places = departureBox.getPlaces();

        if (places?.length == 0) {
          return;
        }

        const location = departureBox.getPlaces()?.[0].geometry?.location

        setDepartureLocation((state) => ({
          lat: location?.lat()!,
          lng: location?.lng()!
        }))
      });

      destinationBox.addListener("places_changed", () => {
        const places = destinationBox.getPlaces();

        if (places?.length == 0) {
          return;
        }

        const location = destinationBox.getPlaces()?.[0].geometry?.location

        setDestinationInfo((state) => ({
          ...state,
          location: {
            lat: location?.lat()!,
            lng: location?.lng()!
          }
        }))

        calculateAndDisplayRoute(directionsService, directionsRenderer, departureRef.current!, destinationRef.current!, setDestinationInfo)
      });
    }
  }, [map])

  return <div ref={ref} style={{ width: 0, height: 0 }} />
};

export default EmptyMap
