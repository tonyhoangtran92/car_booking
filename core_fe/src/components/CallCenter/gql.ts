import {gql} from "@apollo/client";

export const GET_OFTEN_LOCATIONS = gql`
  query getOftenLocations($phoneNumber: String!){
    offenLocationUser(phoneNumber: $phoneNumber) {
      location
      bookingCount
    }
  }
`