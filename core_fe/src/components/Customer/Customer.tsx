import * as React from "react";
import {FC, useEffect, useRef, useState} from "react";
import {Button, Col, message, Row, Space, Spin} from "antd";
import {CarTypeEnum, User} from "../../data/models/User";
import MapWrapper from "../common/Map/MapWrapper";
import Map from "../common/Map/Map";
import Marker from "../common/Map/Marker";
import {CREATE_BOOKING, GET_CURRENT_BOOKING} from "./gql";
import {useLazyQuery, useMutation, useQuery} from "@apollo/client";
import {Booking, BOOKING_STATUS, BookingCreate, BookingCreateInput} from "../../data/models/Booking";
import {READ_USER} from "../../gql/me";
import {decode as atob} from 'base-64'
import Card from 'components/common/Card'
import {CoordinateInput} from "../../data/common";
import BookingDescription from "../common/BookingDescription";

interface GetCurrentBooking {
  myCurrentBooking: Booking;
}

export interface DestinationInfo {
  location?: CoordinateInput,
  distance?: number;
}

const Customer: FC = () => {
  const [messageApi, contextHolder] = message.useMessage();
  const [isBooked, setIsBooked] = useState<boolean>(false)
  const { data: curBooking, startPolling, stopPolling, loading: isGettingCurBooking } = useQuery<GetCurrentBooking>(GET_CURRENT_BOOKING)
  const [ getCurrentBooking, { loading: isGettingLzCurBooking } ] = useLazyQuery(GET_CURRENT_BOOKING, {
    fetchPolicy: "network-only"
  })
  const { data: user } = useQuery<{ me: User }>(READ_USER)
  const [createBooking] = useMutation<BookingCreate, BookingCreateInput>(CREATE_BOOKING);
  const [destinationInfo, setDestinationInfo] = useState<DestinationInfo>({
    location: { lat: 0, lng: 0},
    distance: 0
  })
  const [clicks, setClicks] = useState<google.maps.LatLng[]>([]);
  const [zoom, setZoom] = useState(18); // initial zoom
  const [center, setCenter] = useState<google.maps.LatLngLiteral>({
    lat: 0,
    lng: 0,
  });
  const startRef = useRef(null)
  const endRef = useRef(null)
  const geolocationRef = useRef<google.maps.LatLngLiteral | null>(null)

  useEffect(() => {
    if (curBooking?.myCurrentBooking) {
      setIsBooked(true)
    }
  }, [curBooking])

  useEffect(() => {
    if (isBooked) {
      startPolling(2000)
    }
    return () => {
      stopPolling()
    }
  }, [isBooked])

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(({ coords: { latitude: lat, longitude: lng } }) => {
        setCenter({
          lat,
          lng
        })
        geolocationRef.current = { lat, lng }
      })
    }
  }, [])

  const onClick = (e: google.maps.MapMouseEvent) => {
    // avoid directly mutating state
    setClicks([...clicks, e.latLng!]);
  };

  const onIdle = (m: google.maps.Map) => {
    console.log("onIdle");
    setZoom(m.getZoom()!);
    setCenter(m.getCenter()!.toJSON());
  };

  const onSubmit = (e: React.SyntheticEvent) => {
    e.preventDefault()
    const target = e.target as typeof e.target & {
      departure: { value: string };
      destination: { value: string };
      carType: { value: CarTypeEnum };
    };

    const departure = target.departure.value
    const destination = target.destination.value
    const carType = target.carType.value

    createBooking({
      variables: {
        input: {
          customerId: atob((user!).me.id as string).slice(5),
          departure: departure,
          departurePosition: [geolocationRef.current!],
          destination: destination,
          destinationPosition: [destinationInfo.location!],
          carType: carType,
          totalDistance: destinationInfo.distance!
        }
      },
      onCompleted(data) {
        messageApi.open({
          type: "success",
          content: "Đặt chuyến thành công!"
        })
        setIsBooked(true)
        getCurrentBooking()
      },
      onError(error) {
        messageApi.open({
          type: "error",
          content: error.message
        })
      }
    })
  };

  if (isGettingCurBooking || isGettingLzCurBooking) return (
    <Space size="large" align="center" direction="vertical" style={{ display: "flex" }}>
      <Spin size="large" />
    </Space>
  )

  if (curBooking?.myCurrentBooking)
    return (
      <>
        {contextHolder}
        <BookingDescription data={curBooking.myCurrentBooking} />
      </>
    )

  return (
    <>
      {contextHolder}
      <form onSubmit={onSubmit} style={{ marginBottom: "30px" }}>
        <Row gutter={8}>
          <Col span={12}>
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
                      <input
                        type="text"
                        name="departure"
                        placeholder="Nhập điểm đi"
                        className="ant-input"
                        ref={startRef}
                        required
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="ant-form-item">
              <div className="ant-row ant-form-item-row">
                <div className="ant-col ant-col-4 ant-form-item-label">
                  <label htmlFor="bookingFrm_departure" className="ant-form-item-required">
                    Điểm đến
                  </label>
                </div>
                <div className="ant-col ant-col-20 ant-form-item-control">
                  <div className="ant-form-item-control-input">
                    <div className="ant-form-item-control-input-content">
                      <input
                        type="text"
                        name="destination"
                        placeholder="Nhập điểm đến"
                        className="ant-input"
                        ref={endRef}
                        required
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="ant-form-item">
              <div className="ant-row ant-form-item-row">
                <div className="ant-col ant-col-4 ant-form-item-label">
                  <label htmlFor="bookingFrm_departure" className="ant-form-item-required">
                    Loại xe
                  </label>
                </div>

                <div className="ant-col ant-col-20 ant-form-item-control">
                  <div className="ant-form-item-control-input">
                    <div className="ant-form-item-control-input-content">
                      <div className="ant-radio-group ant-radio-group-outline">
                        <label htmlFor="ct1" className="ant-radio-wrapper ant-radio-wrapper-in-form-item">
                          <span className="ant-radio">
                            <input id="ct1" type="radio" name="carType" value={CarTypeEnum.FOUR_SEAT} required />
                          </span>
                          <span>Bốn chỗ</span>
                        </label>
                        <label htmlFor="ct2" className="ant-radio-wrapper ant-radio-wrapper-in-form-item">
                          <span className="ant-radio">
                            <input id="ct2" type="radio" name="carType" value={CarTypeEnum.SEVEN_SEAT} required />
                          </span>
                          <span>Bảy chỗ</span>
                        </label>
                        <label htmlFor="ct3" className="ant-radio-wrapper ant-radio-wrapper-in-form-item">
                          <span className="ant-radio">
                            <input id="ct3" type="radio" name="carType" value={CarTypeEnum.ANY} required />
                          </span>
                          <span>Bất kỳ</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="ant-form-item">
              <Row>
                <Col span={16} offset={8}>
                  <Button type="primary" htmlType="submit">Đặt chuyến</Button>
                </Col>
              </Row>
            </div>
          </Col>
          <Col span={12}>
            {!!geolocationRef.current && (
              <MapWrapper>
                <Map center={center} zoom={zoom} style={{ height: "600px" }} onClick={onClick} onIdle={onIdle} geolocationRef={geolocationRef} startRef={startRef} endRef={endRef} setDestinationInfo={setDestinationInfo}>
                  {clicks.map((latLng, i) => (<Marker key={i} position={latLng} draggable={true}  />))}
                </Map>
              </MapWrapper>
            )}
          </Col>
        </Row>
      </form>


    </>
  );
}

export default Customer
