import {FC, useEffect, useState} from "react";
import {useMutation, useQuery} from "@apollo/client";
import {
  CANCEL_BOOKING,
  CHANGE_BOOKING_STATUS,
  CONFIRM_BOOKING,
  FINISH_BOOKING,
  GET_CURRENT_RIDE,
  UPDATE_LOCATION
} from "./gql";
import {User} from "../../data/models/User";
import {GET_AVAILABLE_BOOKING} from "../../gql/me";
import {Button, Col, Empty, message, Modal, Row, Space, Table} from "antd";
import {decode as atob} from 'base-64'
import {Booking, BOOKING_STATUS} from "../../data/models/Booking";
import Card from 'components/common/Card'
import BookingDescription from "../common/BookingDescription";
import {EMPTY_BOOKING_TXT} from "../../constants";
import BookingTable from "../common/BookingTable";
import * as React from "react";

type PositionInput = { currentPosition: Array<{ lat: number; lng: number }> }

interface PosVariable {
  pos: PositionInput;
}

export interface BookingVariable {
  id: string;
}

interface ChangeBookingStatusVariable extends BookingVariable{
  status: BOOKING_STATUS;
}

interface MyCurrentRide {
  myCurrentRide: Booking
}

export interface ReadBookingResponse {
  bookingRead: Booking;
}

const Driver: FC = () => {
  const [messageApi, contextHolder] = message.useMessage();
  const [curBooking, setCurBooking] = useState<Booking>()
  const { data: availableBookings, loading, startPolling: startGetBookings, stopPolling: stopGetBookings } = useQuery<{ me: User }>(GET_AVAILABLE_BOOKING, { fetchPolicy: "network-only" })
  const { data: currentRide, startPolling: startGetCurRide, stopPolling: stopGetCurRide } = useQuery<MyCurrentRide>(GET_CURRENT_RIDE, { fetchPolicy: "network-only" })
  const [updateLocation, { error }] = useMutation<any, PosVariable>(UPDATE_LOCATION)
  const [cancelBooking] = useMutation<any, BookingVariable>(CANCEL_BOOKING)
  const [confirmBooking] = useMutation<any, BookingVariable>(CONFIRM_BOOKING)
  const [finishBooking] = useMutation<any, BookingVariable>(FINISH_BOOKING)
  const [changeBookingStatus] = useMutation<any, ChangeBookingStatusVariable>(CHANGE_BOOKING_STATUS)

  useEffect(() => {
    if (currentRide?.myCurrentRide) {
      setCurBooking(currentRide.myCurrentRide)
    }
  }, [currentRide])

  useEffect(() => {
    let id: NodeJS.Timer
    if (navigator.geolocation) {
      id = setInterval(() => {
        navigator.geolocation.getCurrentPosition(({ coords: { latitude:       lat, longitude: lng } }) => {
          updateLocation({ variables: {
              pos: {
                currentPosition: [{
                  lat,
                  lng
                }]
              }
            }})
        })
      }, 5000)
    }
    return () => {
      clearInterval(id)
    }
  }, [])

  useEffect(() => {
    startGetBookings(2000)
    startGetCurRide(2000)
    return () => {
      stopGetBookings()
      stopGetCurRide()
    }
  }, [])

  const onConfirmBooking = (cur: Booking) => {
    confirmBooking({
      variables: {
        id: atob(cur.id).slice(8)
      },
      onCompleted(data) {
        messageApi.open({
          type: "success",
          content: "Nhận chuyến thành công!"
        })
      },
      onError(e) {
        messageApi.open({
          type: "success",
          content: e.message
        })
      }
    })
  }

  const onCancelBooking = (id: string) => {
    cancelBooking({
      variables: {
        id: atob(id).slice(8)
      },
      onCompleted() {
        messageApi.open({
          type: "success",
          content: "Huỷ chuyến thành công!"
        })
        setCurBooking(undefined)
        startGetBookings(2000)
      }
    })
  }

  const onGoingBooking = (id: string) => {
    changeBookingStatus({
      variables: {
        id: atob(id).slice(8),
        status: BOOKING_STATUS.ON_GOING
      },
      onCompleted() {
        messageApi.open({
          type: "success",
          content: "Bắt đầu chuyến đi thành công!"
        })
      }
    })
  }

  const onFinishBooking = (id: string) => finishBooking({
    variables: {
      id:  atob(id).slice(8)
    },
    onCompleted() {
      setCurBooking(undefined)
      Modal.success({
        content: `Chuyến đi đã hoàn thành! Số tiền bạn nhận được là ${Number(curBooking?.totalFee.toFixed(2)).toLocaleString('en-US')} đ`
      });
    },
    onError(error) {
      messageApi.open({
        type: "error",
        content: error.message
      })
    }
  })

  const onRenderBooking = (booking: Booking) => (
    <Space>
      {booking.isConfirmedByDriver && <b>Đang đợi admin duyệt...</b>}
      {!booking.isConfirmedByDriver && (
        <Button type="primary" onClick={() => onConfirmBooking(booking)}>Nhận chuyến</Button>
      )}
    </Space>
  )

  if (!curBooking) {
    return (
      <Row gutter={8}>
        <Col span={24}>
          <BookingTable data={availableBookings?.me.availableBookingForDriver || []} loading={loading} onRenderBooking={onRenderBooking} />
        </Col>
        {contextHolder}
      </Row>
    )
  }

  return (
    <BookingDescription data={curBooking}>
      {contextHolder}
      <Space>
        <Button type="link" danger disabled={currentRide?.myCurrentRide?.status === BOOKING_STATUS.ON_GOING} onClick={() => onCancelBooking(curBooking.id)}>Huỷ chuyến</Button>
        <Button type="primary" disabled={currentRide?.myCurrentRide?.status === BOOKING_STATUS.ON_GOING} onClick={() => onGoingBooking(curBooking.id)}>Bắt đầu chuyến đi</Button>
        <Button type="primary" disabled={currentRide?.myCurrentRide?.status !== BOOKING_STATUS.ON_GOING} onClick={() => onFinishBooking(curBooking.id)}>Hoàn thành</Button>
      </Space>
    </BookingDescription>
  )
}



export default Driver
