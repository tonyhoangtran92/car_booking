import {
  Children,
  FC,
  isValidElement,
  ReactNode,
  useEffect,
  useRef,
  useState,
  cloneElement,
  MutableRefObject, RefObject, Ref, Dispatch, SetStateAction
} from "react";
import useDeepCompareEffect from 'use-deep-compare-effect'
import {BaseSelectRef} from "rc-select";
import geocodeLatLng from "../../../utils/geocodeLatLng";
import calculateAndDisplayRoute from "../../../utils/calculateAndDisplayRoute";
import {DestinationInfo} from "../../Customer/Customer";

interface MapProps extends google.maps.MapOptions {
  geolocationRef: MutableRefObject<google.maps.LatLngLiteral | null>;
  startRef: MutableRefObject<HTMLInputElement | null>;
  endRef: MutableRefObject<HTMLInputElement | null>;
  style: { [key: string]: string };
  onClick?: (e: google.maps.MapMouseEvent) => void;
  onIdle?: (map: google.maps.Map) => void;
  children: ReactNode;
  setDestinationInfo: Dispatch<SetStateAction<DestinationInfo>>;
}

const Map: FC<MapProps> = ({
                             onClick,
                             onIdle,
                             children, style,
                             geolocationRef,
                             startRef,
                             endRef,
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
    if (map && startRef.current && endRef.current) {
      // Create the search box and link it to the UI element.
      const searchBox = new google.maps.places.SearchBox(startRef.current!);
      const endSearchBox = new google.maps.places.SearchBox(endRef.current!);

      const directionsService = new google.maps.DirectionsService();
      const directionsRenderer = new google.maps.DirectionsRenderer();

      directionsRenderer.setMap(map);

      // Bias the SearchBox results towards current map's viewport.
      map.addListener("bounds_changed", () => {
        searchBox.setBounds(map.getBounds() as google.maps.LatLngBounds);
        endSearchBox.setBounds(map.getBounds() as google.maps.LatLngBounds);
      });

      let markers: google.maps.Marker[] = [];

      // Listen for the event fired when the user selects a prediction and retrieve
      // more details for that place.
      searchBox.addListener("places_changed", () => {
        const places = searchBox.getPlaces();

        if (places?.length == 0) {
          return;
        }

        // Clear out the old markers.
        markers.forEach((marker) => {
          marker.setMap(null);
        });
        markers = [];

        // For each place, get the icon, name and location.
        const bounds = new google.maps.LatLngBounds();

        places?.forEach((place) => {
          if (!place.geometry || !place.geometry.location) {
            console.log("Returned place contains no geometry");
            return;
          }

          const icon = {
            url: place.icon as string,
            size: new google.maps.Size(71, 71),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(17, 34),
            scaledSize: new google.maps.Size(25, 25),
          };

          // Create a marker for each place.
          markers.push(
            new google.maps.Marker({
              map,
              icon,
              title: place.name,
              position: place.geometry.location,
            })
          );


          if (place.geometry.viewport) {
            // Only geocodes have viewport.
            bounds.union(place.geometry.viewport);
          } else {
            bounds.extend(place.geometry.location);
          }
        });
        map.fitBounds(bounds);
      });

      endSearchBox.addListener("places_changed", () => {
        const places = searchBox.getPlaces();

        if (places?.length == 0) {
          return;
        }

        const bounds = new google.maps.LatLngBounds();

        places?.forEach((place) => {
          if (!place.geometry || !place.geometry.location) {
            console.log("Returned place contains no geometry");
            return;
          }

          if (place.geometry.viewport) {
            // Only geocodes have viewport.
            bounds.union(place.geometry.viewport);
          } else {
            bounds.extend(place.geometry.location);
          }
        });

        const location = endSearchBox.getPlaces()?.[0].geometry?.location
        // console.log(places?.[0].geometry?.location?.lat())
        setDestinationInfo((state) => ({
          ...state,
          location: {
            lat: location?.lat()!,
            lng: location?.lng()!
          }
        }))

        calculateAndDisplayRoute(directionsService, directionsRenderer, startRef.current!, endRef.current!, setDestinationInfo)
      });
    }
  }, [map])

  useEffect(() => {
    if (map && geolocationRef.current && startRef.current) {
      const geocoder = new google.maps.Geocoder();
      const infowindow = new google.maps.InfoWindow();

      geocodeLatLng(geocoder, map, infowindow, geolocationRef.current, startRef.current)
    }
  }, [map, geolocationRef.current])

  useEffect(() => {
    if (map) {
      ["click", "idle"].forEach((eventName) =>
        google.maps.event.clearListeners(map, eventName)
      );

      if (onClick) {
        map.addListener("click", onClick);
      }

      if (onIdle) {
        map.addListener("idle", () => onIdle(map));
      }
    }
  }, [map, onClick, onIdle]);

  return (
    <>
      <div ref={ref} style={style} />
      {Children.map(children, (child) => {
        if (isValidElement(child)) {
          // set the map prop on the child component
          // @ts-ignore
          return cloneElement(child, { map });
        }
      })}
    </>
  )
};

export default Map
