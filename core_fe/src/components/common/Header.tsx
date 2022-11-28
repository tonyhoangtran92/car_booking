import {Button, PageHeader, Typography} from 'antd'
import {User} from "../../data/models/User";
import {gql, useQuery} from "@apollo/client";
import userLogout from "../../hooks/userLogout";
import {READ_USER} from "../../gql/me";
import {Helmet} from "react-helmet";
import {CAR_TYPE_MAPPING, USER_MAPPING} from "../../constants";

interface HeaderProps {
}

function Header({}: HeaderProps) {
  const logout = userLogout()
  const {data} = useQuery<{ me: User }>(READ_USER)
  return (
    <>
      <Helmet>
        <title>{data?.me?.userType} {data?.me?.email || ""} - Booking Taxi App</title>
      </Helmet>
      <PageHeader
        ghost={false}
        title={`${USER_MAPPING?.[data?.me?.userType || "default"]}: ${data?.me?.fullName || data?.me?.email || ""} ${data?.me?.carType ? " - " + CAR_TYPE_MAPPING[data.me.carType] : ""}`}
        extra={[
          <Button key="1" type="primary" onClick={logout}>
            Đăng xuất
          </Button>,
        ]}
      />
    </>
  )
}

export default Header
