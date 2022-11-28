import {useQuery} from "@apollo/client";
import {User, UserResponse, UserTypeEnum} from "../../data/models/User";
import {Route, RouteProps, Switch, Link, useRouteMatch, useHistory} from "react-router-dom";
import Customer from "../Customer/Customer";
import Driver from "../Driver/Driver";
import CallCenter from "../CallCenter/CallCenter";
import Admin from "../Admin/Admin";
import NotFound from "../common/NotFound";
import {useEffect} from "react";
import {ROUTE, SESSION_KEYS, SUB_HOME_ROUTES} from "../../constants";
import userLogout from "../../hooks/userLogout";
import {RETRIEVE_USER} from "../../gql/me";
import withLayout from "../common/Layout/Layout";
import {Button, Layout, Result, Space, Spin} from "antd";

interface HomeProps {}

const Home = ({}: HomeProps): JSX.Element => {
  const { push } = useHistory()
  const { path } = useRouteMatch()
  const { data, loading, error } = useQuery<UserResponse>(RETRIEVE_USER, {
    fetchPolicy: "network-only",
    nextFetchPolicy: "network-only"
  });

  const user = data?.me

  useEffect(() => {
    if (user) {
      ({
        [UserTypeEnum.CUSTOMER]: () => push(`${path}${SUB_HOME_ROUTES.CUSTOMER.path}`),
        [UserTypeEnum.DRIVER]: () => push(`${path}${SUB_HOME_ROUTES.DRIVER.path}`),
        [UserTypeEnum.CALL_CENTER]: () => push(`${path}${SUB_HOME_ROUTES.CALL_CENTER.path}`),
        [UserTypeEnum.ADMIN]: () => push(`${path}${SUB_HOME_ROUTES.ADMIN.path}`)
      }[user.userType])()
    }
  }, [user])

  const routes: RouteProps[] = [
    { path: `${path}${SUB_HOME_ROUTES.CUSTOMER.path}`, exact: true, component: withLayout(Customer)},
    { path: `${path}${SUB_HOME_ROUTES.DRIVER.path}`, exact: true, component: withLayout(Driver) },
    { path: `${path}${SUB_HOME_ROUTES.CALL_CENTER.path}`, exact: true, component: withLayout(CallCenter) },
    { path: `${path}${SUB_HOME_ROUTES.ADMIN.path}`, exact: true, component: withLayout(Admin) },
    { component: NotFound }
  ]

  if (loading) {
    return (
      <Layout style={{ minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center", background: "white" }}>
        <Space size="middle">
          <Spin size="large" />
        </Space>
      </Layout>
    )
  }

  if (error) {
    localStorage.removeItem(SESSION_KEYS.ACCESS_TOKEN)
    return (
      <Result
        status="warning"
        title="Đăng nhập không thành công. Vui lòng đăng nhập lại."
        extra={
          <Button type="primary" key="console" onClick={() => push(ROUTE.LOGIN.path)}>
            Đăng nhập
          </Button>
        }
      />
    )
  }

  return (
    <Switch>
      {routes.map((route, index) => (
        <Route
          {...route}
          key={typeof route.path !== "string" ? index : route.path + index}
        />
      ))}
    </Switch>
  )
}

export default Home
