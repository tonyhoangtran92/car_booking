import {ComponentType, PropsWithChildren} from "react";
import {Breadcrumb, Col, Layout, Menu, Row, Space, Spin} from 'antd';
import Header from "../Header";
import {useQuery} from "@apollo/client";
import {User} from "../../../data/models/User";
import {userVar} from "../../../cache";
import theme from "../../../theme";
import {RETRIEVE_USER} from "../../../gql/me";
import {SESSION_KEYS} from "../../../constants";

const { default: { containerPadding, containerWidth } } = theme

const { Content, Footer } = Layout

function LayoutApp({ children }: PropsWithChildren) {
  return (
    <Layout style={{ minHeight: "100vh", background: "white" }}>
      <Header />
      <Content style={{ padding: containerPadding }}>
        {children}
      </Content>
      <Footer style={{ textAlign: "center", background: "white" }}>
        Booking Taxi App ©2022
      </Footer>
    </Layout>
  )
}

export default function withLayout<T extends PropsWithChildren<{}>>(WrappedComponent: ComponentType<T>) {
  return (props: T) => (
    <LayoutApp>
      <WrappedComponent {...props} />
    </LayoutApp>
  )
}
