import React from "react";
import ReactDOM from "react-dom/client";

import { ThemeProvider } from "./contexts/ThemeContext";

import App from "./App";

import { BrowserRouter } from "react-router-dom";

import { AuthProvider } from "./contexts/AuthContext";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  </React.StrictMode>
);