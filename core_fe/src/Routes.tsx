import { ROUTE } from "./constants"
import Login from "./components/Auth/Login"
import SignUp from "./components/Auth/SignUp"
import {
  BrowserRouter as Router, Redirect,
  Route,
  RouteProps,
  Switch,
} from "react-router-dom"

import {Component} from "react";
import Home from "./components/Home/Home";
import withProtection from "./components/common/ProtectedRoute";
import withLayout from "./components/common/Layout/Layout";
import NotFound from "./components/common/NotFound";

const Routes = (): JSX.Element => {
  const routes: RouteProps[] = [
    { path: ROUTE.HOME.path, component: withProtection(Home)},
    { path: ROUTE.LOGIN.path, component: Login },
    { path: ROUTE.SIGNUP.path, component: SignUp },
    { component: NotFound },
  ]
  return (
    <Router>
      <Switch>
        {routes.map((route, index) => (
          <Route
            {...route}
            key={typeof route.path !== "string" ? index : route.path + index}
          />
        ))}
      </Switch>
    </Router>
  )
}

export default Routes
