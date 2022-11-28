import {PropsWithChildren} from "react";
import {Wrapper} from "@googlemaps/react-wrapper";

const MapWrapper = ({ children }: PropsWithChildren) => (
  <Wrapper apiKey={"AIzaSyCfjOZ1LulXdlUhNtRGyMyn9aV2U-f-bgU"} libraries={["places"]}>
    {children}
  </Wrapper>
)

export default MapWrapper
