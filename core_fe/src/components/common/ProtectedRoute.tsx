import {Redirect, Route, RouteComponentProps, RouteProps} from 'react-router-dom'
import {SESSION_KEYS, ROUTE} from 'constants/index'
import {ReactComponentElement, ReactNode} from "react";
import React from 'react';

function ProtectedRoute({ children }: React.PropsWithChildren<{}>) {
  if (!localStorage.getItem(SESSION_KEYS.ACCESS_TOKEN)) {
    return <Redirect to={ROUTE.LOGIN.path} />
  }

  return children as JSX.Element
}

function withProtection<T extends RouteComponentProps>(WrappedComponent: React.ComponentType<T>) {
  return React.memo<Pick<T, Exclude < keyof T, keyof RouteComponentProps>>>(p =>
    <ProtectedRoute>
      <WrappedComponent {...(p as T)} />
    </ProtectedRoute>
  )
}

export default withProtection