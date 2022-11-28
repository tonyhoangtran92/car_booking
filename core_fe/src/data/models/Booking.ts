import {CarTypeEnum, User} from "./User";
import {CoordinateInput} from "../common";

export enum BOOKING_TYPE {
  ON_APP,
  BY_PHONE
}

export enum BOOKING_STATUS {
  WAIT_FOR_CONFIRMED="WAIT_FOR_CONFIRMED",
  WAIT_FOR_DRIVER="WAIT_FOR_DRIVER",
  ON_GOING="ON_GOING",
  COMPLETED="COMPLETED",
  CANCELLED="CANCELLED"
}

export interface Booking {
  id: string;
  privateMetadata?: string; 
  metadata?: string;
  customer?: User;
  isRegisteredUser: boolean;
  driver?: User;
  carType: CarTypeEnum;
  bookingTime: string;
  finishTime: string;
  bookingType: BOOKING_TYPE;
  departure: string;
  departurePosition?: string;
  destination: string;
  destinationPosition?: string;
  status: BOOKING_STATUS;
  totalDistance: number;
  totalFee: number;
  cancelCount: number;
  gpsData: string;
  isConfirmedByDriver?: boolean;
  driverConfirmBooking?: Array<{
    id: string;
    distance: number;
    driver: User;
    booking: Booking;
  }>;
  phoneNumber?: string;
}

export interface BookingCreateInput {
  input: {
    customerId?: string | number;
    carType: CarTypeEnum;
    departure: string;
    departurePosition: google.maps.LatLngLiteral[];
    destination?: string;
    destinationPosition?: CoordinateInput[];
    totalDistance?: number;
    phoneNumber?: number | string;
  }
}

export interface BookingError {
  field: string;
  message: string;
  code: string;
}

export interface BookingCreate {
  bookingCreate: {
    errors: Array<BookingError>;
    booking: Booking;
  }
}