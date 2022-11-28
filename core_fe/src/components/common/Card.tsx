import {Card, Divider} from "antd";
import {Booking, BOOKING_STATUS} from "../../data/models/Booking";
import {ReactNode} from "react";
import {decode as atob} from "base-64";
import {CAR_TYPE} from "../../constants";
import * as React from "react";
import {User} from "../../data/models/User";

interface CardProps {
  data: Booking;
  children?: ReactNode;
}

const ModifiedCard: React.FC<CardProps> = ({ data, children }) => {
  return (
    <Card title="Thông tin chuyến đi" style={{ width: '100%' }}>
      <h4>MÃ CHUYẾN ĐI: {atob(data.id).slice(8)}</h4>
      <h4>Điểm đi: {data.departure}</h4>
      <h4>Điểm đến: {data.destination}</h4>
      <h4>Khoảng cách: {data.totalDistance}km</h4>
      <h4>Loại xe: {CAR_TYPE[data.carType]}</h4>
      <h4>Giá cước: {(data.totalFee).toLocaleString('en-US')}đ</h4>
      <h4>Tình trạng: {data.status}</h4>
      {data?.customer && (
        <div>
          <h4>Tên khách hàng: {data?.customer.fullName}</h4>
          <h4>SĐT khách hàng: {data?.customer?.phoneNumber}</h4>
        </div>
      )}
      {data?.driver && (
        <div>
          <h4>Tên tài xế: {data?.driver.fullName}</h4>
          <h4>SĐT tài xế: {data?.driver.phoneNumber}</h4>
          <h4>Hãng xe: {data?.driver.carBrand}</h4>
          <h4>Biển số xe: {data?.driver.licensePlate}</h4>
        </div>
      )}
      {children && (
        <Divider className="card-actions">
          {children}
        </Divider>
      )}
    </Card>
  )
}

export default ModifiedCard
