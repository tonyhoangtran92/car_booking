import {useMutation, useQuery} from "@apollo/client";
import {CHOOSE_DRIVER, FIND_BOOKINGS} from "./gql";
import {Booking} from "../../data/models/Booking";
import {Button, Col, Empty, message, Row} from "antd";
import {decode as atob, encode as btoa} from 'base-64'
import {useEffect} from "react";
import {CAR_TYPE} from "../../constants";
import Card from "../common/Card";
import BookingTable from "../common/BookingTable";


export interface BookingWaitConfirmResponse {
  bookingsWaitForConfirmed: Array<Booking>;
}

interface ChooseDriverVariables {
  id: string;
}


export default () => {
  const [messageApi, contextHolder] = message.useMessage();
  const {loading, error, data, startPolling, stopPolling} = useQuery<BookingWaitConfirmResponse>(FIND_BOOKINGS)
  const [chooseDriver] = useMutation<any, ChooseDriverVariables>(CHOOSE_DRIVER)

  useEffect(() => {
    startPolling(2000)
    return () => {
      stopPolling()
    }
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  const onChooseDriver = (bookId: string) => {
    chooseDriver({
      variables: {
        id: atob(bookId).slice(25)
      },
      onCompleted() {
        messageApi.open({
          type: "success",
          content: "Chọn tài xế thành công!"
        })
      },
      onError(error) {
        messageApi.open({
          type: "error",
          content: error.message
        })
      }
    })
  }

  const onRenderBooking = (booking: Booking) => (
    <ol>
      {booking.driverConfirmBooking?.map(({ distance, driver, id: driverConfirmId }) => (
        <li>
          <h4>
            <div key={driver.id}>
              <p>{driver.fullName}: {distance.toFixed(2)} m <Button type="link" onClick={() => onChooseDriver(driverConfirmId)}>Book</Button></p>
            </div>
          </h4>
        </li>
      ))}
    </ol>
  )

  return (
    <>
      <Row gutter={8}>
        <Col span={24}>
          <BookingTable data={data?.bookingsWaitForConfirmed || []} loading={loading} onRenderBooking={onRenderBooking} />
        </Col>
      </Row>
      {contextHolder}
    </>
  )
}
