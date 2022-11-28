import {CarTypeEnum, UserTypeEnum} from "../data/models/User";
import {BOOKING_STATUS} from "../data/models/Booking";

export const ROUTE = {
  HOME: { path: '/home/' },
  LOGIN: { path: '/login' },
  SIGNUP: { path: '/signup' },
  NOTFOUND: { path: '*' }
}

export const SUB_HOME_ROUTES = {
  CUSTOMER: { path: "customer" },
  DRIVER: { path: "driver"},
  CALL_CENTER: { path: "callcenter" },
  ADMIN: { path: "admin" }
}

export const SESSION_KEYS = {
  "ACCESS_TOKEN": "access_token"
}

export const CAR_TYPE = {
  "FOUR_SEAT": "Bốn chỗ",
  "SEVEN_SEAT": "Bảy chỗ",
  "ANY": "Bất kỳ"
}

export const USER_MAPPING = {
  [UserTypeEnum.ADMIN]: "Quản trị viên",
  [UserTypeEnum.CUSTOMER]: "Quý khách",
  [UserTypeEnum.CALL_CENTER]: "Tổng đài viên",
  [UserTypeEnum.DRIVER]: "Tài xế",
  "default": "Bạn"
}

export const STATUS_MAPPING = {
  [BOOKING_STATUS.WAIT_FOR_CONFIRMED]: "Đang tìm tài xế",
  [BOOKING_STATUS.WAIT_FOR_DRIVER]: "Đang đợi tài xế đến đón",
  [BOOKING_STATUS.ON_GOING]: "Đang diễn ra",
  [BOOKING_STATUS.COMPLETED]: "Đã hoàn thành",
  [BOOKING_STATUS.CANCELLED]: "Bị huỷ",
}

export const CAR_TYPE_MAPPING = {
  [CarTypeEnum.SEVEN_SEAT]: "Bảy chỗ",
  [CarTypeEnum.FOUR_SEAT]: "Bốn chỗ",
  [CarTypeEnum.ANY]: "Bất kỳ",
}

export const EMPTY_BOOKING_TXT = "Hiện tại chưa có chuyến mới."