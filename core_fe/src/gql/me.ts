import {gql} from "@apollo/client";

export const RETRIEVE_USER = gql`
  query {
    me {
      id
      fullName
      email
      userType
      carType
    }
  }
`;

export const READ_USER = gql`
  query {
    me @client {
      id
      fullName
      email
      userType
      carType
    }
  }
`;

export const GET_AVAILABLE_BOOKING = gql`
  query getAvailableBooking{
    me {
      id
      availableBookingForDriver {
          id
          status
          departure
          destination
          totalFee
          totalDistance
          isConfirmedByDriver
          carType
          customer {
            fullName
            email
            phoneNumber
          }
      }
    }
  }
`;
