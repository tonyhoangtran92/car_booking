import {Booking} from "./Booking";

export enum UserTypeEnum {
  CUSTOMER = "CUSTOMER",
  DRIVER = "DRIVER",
  CALL_CENTER = "CALL_CENTER",
  ADMIN = "ADMIN"
}

export enum CarTypeEnum {
  FOUR_SEAT="FOUR_SEAT",
  SEVEN_SEAT="SEVEN_SEAT",
  ANY="ANY"
}

export interface User {
  id: number | string;
  fullName: string;
  phoneNumber: string;
  dateOfBirth?: string;
  citizenIdentification?: string;
  carType?: CarTypeEnum;
  carBrand?: string;
  licensePlate?: string;
  carColor?: string;
  address?: string;
  isAvailable: boolean;
  email: string;
  userType: UserTypeEnum;
  availableBookingForDriver?: Array<Booking>;
}

export interface UserResponse {
  me: User;
}