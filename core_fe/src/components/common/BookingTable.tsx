import {Badge, Table} from "antd";
import {Booking} from "../../data/models/Booking";
import * as React from "react";
import {ReactNode} from "react";
import {decode as atob} from "base-64";
import {CAR_TYPE, STATUS_MAPPING} from "../../constants";
import type {ColumnsType} from 'antd/es/table';
import {CarTypeEnum, User, UserTypeEnum} from "../../data/models/User";
import {useQuery} from "@apollo/client";
import {READ_USER} from "../../gql/me";

interface BookingTableProps {
  data: Booking[];
  loading?: boolean;
  extra?: ReactNode;
  [key: string]: any;
}

const BookingTable: React.FC<BookingTableProps> = ({ data, onRenderBooking = () => {} }) => {
  const { data: dataUser } = useQuery<{ me: User }>(READ_USER)
  const curUser = dataUser?.me
  const columns: ColumnsType<Booking> = [
    {
      title: 'MÃ CHUYẾN ĐI:',
      dataIndex: 'id',
      key: 'id',
      render: text => atob(text).slice(8)
    },
    {
      title: 'Điểm đi',
      dataIndex: 'departure',
      key: 'departure',
    },
    {
      title: 'Điểm đến',
      dataIndex: 'destination',
      key: 'destination',
    },
    {
      title: 'Khoảng cách',
      dataIndex: 'totalDistance',
      key: 'totalDistance',
      render: (distance: number) => (distance.toFixed(2)) + ' km'
    },
    {
      title: 'Loại xe',
      dataIndex: 'carType',
      key: 'carType',
      render: (carType: CarTypeEnum) => CAR_TYPE[carType]
    },
    {
      title: 'Tình trạng',
      dataIndex: 'status',
      key: 'status',
      render(_, booking) {
        return <Badge status="processing" text={STATUS_MAPPING[booking.status]} />
      }
    },
    {
      title: 'SĐT khách hàng vãng lai',
      dataIndex: 'phoneNumber',
      key: 'phoneNumber',
      render(_, booking) {
        if (curUser?.userType !== UserTypeEnum.DRIVER) {
          return booking?.phoneNumber
        }
      }
    }
  ];

  // @ts-ignore
  if ([UserTypeEnum.ADMIN, UserTypeEnum.DRIVER].includes(curUser?.userType))
    columns.push({
      title: "Hành động",
      key: 'action',
      render(_, booking) {
        return onRenderBooking(booking)
      }
    })

  return <Table columns={columns} dataSource={data.map(e => ({...e, key: e.id}))} bordered title={() => 'Các chuyến đi hiện tại'} />;
}

export default BookingTable
