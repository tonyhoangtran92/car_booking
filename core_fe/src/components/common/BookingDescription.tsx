import {FC, ReactNode} from "react";
import {Booking} from "../../data/models/Booking";
import {Badge, Descriptions} from "antd";
import * as React from "react";
import {decode as atob} from "base-64";
import {CAR_TYPE, STATUS_MAPPING} from "../../constants";

interface BookingDescriptionProps {
  data: Booking;
  children?: ReactNode;
}

const BookingDescription: FC<BookingDescriptionProps> = ({ data, children }) => {
  return (
    <Descriptions title="Thông tin chuyến đi" layout="horizontal" bordered column={2} extra={children}>
      <Descriptions.Item label="MÃ CHUYẾN ĐI" span={2}>{atob(data.id).slice(8)}</Descriptions.Item>
      <Descriptions.Item label="Điểm đi:">{data.departure}</Descriptions.Item>
      <Descriptions.Item label="Điểm đến:">{data.destination}</Descriptions.Item>
      <Descriptions.Item label="Khoảng cách:">{data.totalDistance.toFixed(0)} km</Descriptions.Item>
      <Descriptions.Item label="Loại xe:">
        {CAR_TYPE[data.carType]}
      </Descriptions.Item>
      <Descriptions.Item label="Giá cước:">
        {(data.totalFee).toLocaleString('en-US')} vnđ
      </Descriptions.Item>
      <Descriptions.Item label="Tình trạng:">
        <Badge status="processing" text={STATUS_MAPPING[data.status]} />
      </Descriptions.Item>
      <Descriptions.Item label="Contact">
        {data?.customer && (
          <ul>
            <li>Tên khách hàng: {data?.customer.fullName}</li>
            <li>SĐT khách hàng: <a>{data?.customer?.phoneNumber}</a></li>
          </ul>
        )}
        {data?.driver && (
          <ul>
            <li>Tên tài xế: {data?.driver.fullName}</li>
            <li>SĐT tài xế: <a>{data?.driver.phoneNumber}</a></li>
            <li>Hãng xe: {data?.driver.carBrand}</li>
            <li>Biển số xe: {data?.driver.licensePlate}</li>
          </ul>
        )}
      </Descriptions.Item>
    </Descriptions>
  )
}

export default BookingDescription
