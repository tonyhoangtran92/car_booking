import React from "react";
import { createRoot } from "react-dom/client";
import {ApolloClient, InMemoryCache, ApolloProvider, createHttpLink, gql} from "@apollo/client";
import "antd/dist/antd.min.css";
import Routes from "./Routes";
import reportWebVitals from "./reportWebVitals";
import {setContext} from "@apollo/client/link/context";
import {SESSION_KEYS} from "./constants";
import cache from "./cache";
import "styles/main.css"

export const typeDefs = gql`
  extend type Query {
    user: User!
  }
`

const httpLink = createHttpLink({
  uri: process.env.REACT_APP_PUBLIC_URI
})

const authLink = setContext((_, { headers }) => {
  // get the authentication token from local storage if it exists
  const token = localStorage.getItem(SESSION_KEYS.ACCESS_TOKEN);
  // return the headers to the context so httpLink can read them
  return {
    headers: {
      ...headers,
      ...(token && { Authorization: `Bearer ${token}`})
    }
  }
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache,
  typeDefs
});

const container = document.getElementById("root")!;
const root = createRoot(container);

root.render(
  <React.StrictMode>
      <ApolloProvider client={client}>
        <Routes />
      </ApolloProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
