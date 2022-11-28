import {Button, Checkbox, Col, Divider, Form, Input, message, Radio, Row} from "antd";
import {CAR_TYPE} from "../../constants";
import { Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {useLazyQuery, useMutation, useQuery} from "@apollo/client";
import {GET_OFTEN_LOCATIONS} from "./gql";
import {FocusEvent, useEffect, useRef, useState} from "react";
import {BookingCreate, BookingCreateInput} from "../../data/models/Booking";
import {CREATE_BOOKING} from "../Customer/gql";
import MapWrapper from "../common/Map/MapWrapper";
import EmptyMap from "../common/Map/EmptyMap";
import {CarTypeEnum} from "../../data/models/User";
import {DestinationInfo} from "../Customer/Customer";
import {FIND_BOOKINGS} from "../Admin/gql";
import {BookingWaitConfirmResponse} from "../Admin/Admin";
import BookingTable from "../common/BookingTable";

interface DataType {
  location: string;
  bookingCount: number;
}

const columns: ColumnsType<DataType> = [
  {
    title: 'Địa điểm',
    dataIndex: 'location'
  },
  {
    title: 'Số lần',
    dataIndex: 'bookingCount',
  }
];

interface OftenLocationsVariables {
  phoneNumber: string;
}

interface OftenLocationsResult {
  offenLocationUser: DataType[];
}

const CallCenter = () => {
  const [messageApi, contextHolder] = message.useMessage();
  const {loading: loadingBookings, data: bookingList, startPolling, stopPolling} = useQuery<BookingWaitConfirmResponse>(FIND_BOOKINGS)
  const [departureLocation, setDepartureLocation] = useState<google.maps.LatLngLiteral>({
    lat: 0,
    lng: 0
  })
  const [destinationInfo, setDestinationInfo] = useState<DestinationInfo>({
    location: { lat: 0, lng: 0},
    distance: undefined
  })
  const departureRef = useRef<HTMLInputElement | null>(null)
  const destinationRef = useRef<HTMLInputElement | null>(null)
  const [createBooking, { loading: creatingBooking }] = useMutation<BookingCreate, BookingCreateInput>(CREATE_BOOKING);
  const [getOftenLocations, { loading, data: oftenLocations }] = useLazyQuery<OftenLocationsResult, OftenLocationsVariables>(GET_OFTEN_LOCATIONS)

  useEffect(() => {
    startPolling(2000)
    return(() => {
      stopPolling()
    })
  }, [])

  const onFinish = (values: { phoneNumber: number | string, carType: CarTypeEnum }) => {
    console.log('Success:', {...values, departure: departureRef.current?.value});
    createBooking({
      variables: {
        input: {
          phoneNumber: values.phoneNumber,
          carType: values.carType,
          departure: departureRef.current?.value!,
          departurePosition: [departureLocation],
          destination: destinationRef.current?.value!,
          destinationPosition: [destinationInfo.location!],
          totalDistance: destinationInfo.distance
        }
      },
      onCompleted(data) {
        messageApi.open({
          type: "success",
          content: "Điều phối thành công!"
        })
      },
      onError(error) {
        messageApi.open({
          type: "error",
          content: error.message
        })
      }
    })

  };

  const onFinishFailed = (errorInfo: any) => {
    errorInfo.errorFields.push({
      departure: departureRef.current?.value
    })
    console.log('Failed:', errorInfo);
  };

  const onPhoneNumberBlur = (e: FocusEvent<HTMLInputElement, Element>) => {
    getOftenLocations({
      variables: {
        phoneNumber: e.target.value
      },
      fetchPolicy: "network-only",
      nextFetchPolicy: "network-only"
    })
  }

  return (
    <>
      <Row gutter={8}>
        <Col span={12}>
          <Form
            name="bookingFrm"
            labelCol={{ span: 4 }}
            wrapperCol={{ span: 20 }}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete="off"
          >
            <Form.Item
              label="SĐT"
              name="phoneNumber"
              rules={[{ required: true, message: 'Vui lòng nhập số điện thoại!' }]}
            >
              <Input onBlur={onPhoneNumberBlur} />
            </Form.Item>

            <div className="ant-form-item">
              <div className="ant-row ant-form-item-row">
                <div className="ant-col ant-col-4 ant-form-item-label">
                  <label htmlFor="bookingFrm_departure" className="ant-form-item-required">
                    Điểm đi
                  </label>
                </div>
                <div className="ant-col ant-col-20 ant-form-item-control">
                  <div className="ant-form-item-control-input">
                    <div className="ant-form-item-control-input-content">
                      <input type="text" className="ant-input" name="departure" id="bookingFrm_departure" ref={departureRef} required />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="ant-form-item">
              <div className="ant-row ant-form-item-row">
                <div className="ant-col ant-col-4 ant-form-item-label">
                  <label htmlFor="bookingFrm_destination" className="ant-form-item-required">
                    Điểm đến
                  </label>
                </div>
                <div className="ant-col ant-col-20 ant-form-item-control">
                  <div className="ant-form-item-control-input">
                    <div className="ant-form-item-control-input-content">
                      <input type="text" className="ant-input" name="destination" id="bookingFrm_destination" ref={destinationRef} required />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <Form.Item name="carType" label="Loại xe" rules={[{ required: true, message: 'Vui lòng chọn loại xe!' }]}>
              <Radio.Group>
                <Radio value={CarTypeEnum.FOUR_SEAT}>Bốn chỗ</Radio>
                <Radio value={CarTypeEnum.SEVEN_SEAT}>Bảy chỗ</Radio>
                <Radio value={CarTypeEnum.ANY}>Bất kỳ</Radio>
              </Radio.Group>
            </Form.Item>

            <Form.Item wrapperCol={{ offset: 8, span: 16 }}>
              <Button type="primary" htmlType="submit" loading={creatingBooking}>
                Điều phối
              </Button>
            </Form.Item>
          </Form>
          <MapWrapper>
            <EmptyMap departureRef={departureRef} destinationRef={destinationRef} setDepartureLocation={setDepartureLocation} setDestinationInfo={setDestinationInfo} />
          </MapWrapper>
        </Col>
        <Col span={12}>
          <Table
            loading={loading}
            columns={columns}
            dataSource={oftenLocations?.offenLocationUser || []}
            bordered
            title={() => 'Các địa chỉ đi nhiều nhất'}
            style={{ marginBottom: "30px" }}
          />
        </Col>
      </Row>
      <Row gutter={8}>
        <Col span={24}>
          <BookingTable data={bookingList?.bookingsWaitForConfirmed || []} loading={loadingBookings} />
        </Col>
      </Row>
      {contextHolder}
    </>
  )
}

export default CallCenter