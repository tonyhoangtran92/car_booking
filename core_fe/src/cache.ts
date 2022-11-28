import {InMemoryCache, makeVar} from '@apollo/client';
import {CarTypeEnum, User, UserTypeEnum} from "./data/models/User";

const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        user: {
          read() {
            return userVar();
          }
        }
      }
    }
  }
})

const initialUser: User = {
  fullName: "",
  id: "",
  address: "",
  carBrand: "",
  carType: CarTypeEnum.ANY,
  carColor: "",
  dateOfBirth: "",
  email: "",
  isAvailable: false,
  citizenIdentification: "",
  licensePlate: "",
  phoneNumber: "",
  userType: UserTypeEnum.CUSTOMER,
}


export const userVar = makeVar<User>(initialUser)

export default cache
