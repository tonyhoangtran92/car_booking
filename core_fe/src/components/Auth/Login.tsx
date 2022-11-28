import { Button, Checkbox, Form, Input, Typography } from "antd";
import {useQuery, gql, useMutation} from "@apollo/client";
import {useState} from "react";
import {SESSION_KEYS, ROUTE} from "../../constants";
import {useHistory} from "react-router-dom";
import {LOGIN} from "./gql";
import {Helmet} from "react-helmet";

const { Title } = Typography;

interface LoginVariables {
  email: string;
  password: string;
}

const Login = (): JSX.Element => {
  const [login, { loading }]= useMutation<any, LoginVariables>(LOGIN)
  const history = useHistory()
  const onFinish = async (values: any) => {
    try {
      login({
        variables: {
          email: values.email,
          password: values.password
        },
        onCompleted(data) {
          localStorage.setItem(SESSION_KEYS.ACCESS_TOKEN, data.userLogin.token)
          history.push(ROUTE.HOME.path)
        }
      })
    } catch (e) {
      console.log(e)
    }
  };

  const onFinishFailed = (errorInfo: any) => {
    console.log("Failed:", errorInfo);
  };
  return (
    <div style={{ width: 400, margin: "100px auto" }}>
      <Helmet>
        <title>Login - Booking Taxi App</title>
      </Helmet>
      <Title style={{ textAlign: "center" }}>Đăng nhập</Title>
      <Form
        name="basic"
        labelCol={{ span: 8 }}
        wrapperCol={{ span: 16 }}
        initialValues={{ remember: true }}
        onFinish={onFinish}
        onFinishFailed={onFinishFailed}
        autoComplete="off"
      >
        <Form.Item
          label="Email"
          name="email"
          rules={[{ required: true, message: "Vui lòng nhập email!" }]}
        >
          <Input type="email" />
        </Form.Item>

        <Form.Item
          label="Password"
          name="password"
          rules={[{ required: true, message: "Vui lòng nhập mật khẩu!" }]}
        >
          <Input.Password />
        </Form.Item>

        <Form.Item wrapperCol={{ offset: 8, span: 16 }}>
          <Button type="primary" htmlType="submit" loading={loading}>
            Đăng nhập
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default Login;
