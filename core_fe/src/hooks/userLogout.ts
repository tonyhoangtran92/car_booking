import {ROUTE, SESSION_KEYS} from "../constants";
import {useHistory} from "react-router-dom";

export default () => {
  const { push } = useHistory()

  return () => {
    push(ROUTE.LOGIN.path)
    localStorage.removeItem(SESSION_KEYS.ACCESS_TOKEN)
  }
}