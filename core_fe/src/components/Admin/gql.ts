import {gql} from "@apollo/client";

export const FIND_BOOKINGS = gql`
  query {
    bookingsWaitForConfirmed{
        id
        customer {
            id,
            fullName
            phoneNumber
        },
        driver{
            id,
            fullName
            phoneNumber
            licensePlate
        }
        carType
        bookingTime,
        finishTime,
        departure,
        destination,
        totalDistance,
        totalFee,
        status,
        cancelCount
        phoneNumber
        isRegisteredUser
        driverConfirmBooking {
            id
            distance,
            driver {
                id,
                fullName
                email
            },
            booking {
                id
            }
        }

    }
  }
`;

export const CHOOSE_DRIVER = gql`
  mutation chooseDriver($id: ID!){
    adminChooseDriverForBooking (
            id: $id
    ) {
        errors {
            code,
            message
        }
    }
  }
`