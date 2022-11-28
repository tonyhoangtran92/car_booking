import { Button, Result } from 'antd';
import React from 'react';
import {useHistory} from "react-router-dom";
import {ROUTE} from "../../constants";

const NotFound: React.FC = () => {
  const { push } = useHistory()
  return (
    <Result
      status="404"
      title="404"
      subTitle="Sorry, the page you visited does not exist."
      extra={<Button type="primary" onClick={() => push(ROUTE.HOME.path)}>Back Home</Button>}
    />
  )
};

export default NotFound;