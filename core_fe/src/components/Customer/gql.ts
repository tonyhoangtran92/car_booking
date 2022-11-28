import {gql} from "@apollo/client";

export const CREATE_BOOKING = gql`
  mutation createBooking($input: BookingCreateInput!) {
    bookingCreate(
        input: $input
    ) {
        booking {
            id
            customer {
                id,
                fullName
            },
            departure,
            departurePosition,
            destination,
            destinationPosition
        },
        errors {
            code,
            message
        }
    }
}
`;

export const GET_CURRENT_BOOKING = gql`
  query {
    myCurrentBooking {
        id
        bookingTime
        finishTime
        departure
        departurePosition
        destination
        destinationPosition
        status
        totalFee
        totalDistance
        carType
        driver {
          id
          fullName
          phoneNumber
          licensePlate
          email
          carBrand
        }
    }
  }
`