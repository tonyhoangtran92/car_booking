import {gql} from "@apollo/client";

export const LOGIN = gql`
  mutation login($email: String!, $password: String!) {
    userLogin(
        email: $email,
        password: $password
    ) {
        token
        errors {
            field,
            code,
            message
        }
    }
  }
`;