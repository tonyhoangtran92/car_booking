import {gql} from "@apollo/client";

export const UPDATE_LOCATION = gql`
  mutation updateLocation($pos: PositionInput!) {
    userUpdateLocation (input: $pos) {
      errors {
          field,
          code,
          message
      }
    }
  }
`;

export const CANCEL_BOOKING = gql`
  mutation cancelBooking($id: ID!) {
    bookingCancel (
            id: $id
    ) {
        errors {
            code,
            message
        }
    }
  }
`

export const CONFIRM_BOOKING = gql`
  mutation confirmBooking($id: ID!) {
    driverConfirmBooking (
            id: $id
    ) {
        errors {
            code,
            message
        }
    }
  }
`

export const FINISH_BOOKING = gql`
  mutation finishBooking($id: ID!){
    driverFinishBooking (
            id: $id
    ) {
        errors {
            code,
            message
        }
    }
  }
`

export const GET_UNREAD_NOTI = gql`
  query {
    myUnreadNotification{
        id,
        targetObjectId,
        description,
        timestamp,
    }
  }
`

export const GET_CURRENT_RIDE = gql`
  query {
    myCurrentRide {
        id
        customer {
            id,
            fullName
            email
            phoneNumber
        },
        driver{
            id,
            fullName
            email
            carBrand
            licensePlate
            phoneNumber
        },
        carType
        bookingTime
        finishTime
        departure
        destination
        totalDistance
        totalFee
        status
        cancelCount
    }
}
`

export const READ_BOOKING = gql`
  query readBooking($id: ID!){
    bookingRead (id: $id) {
        id
        customer {
            id
            fullName
            email
        }
        driver{
            id
            fullName
            email
        }
        bookingTime
        finishTime
        departure
        destination
        totalDistance
        totalFee
        status
        cancelCount
    }
  }
`

export const CHANGE_BOOKING_STATUS = gql`
  mutation changeBookingStatus($id: ID!, $status: StatusTypeEnum!){
    bookingChangeStatus (
            id: $id,
            status: $status
    ) {
        errors {
            code,
            message
        }
    }
  }
`
