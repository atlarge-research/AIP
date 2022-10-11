import React from "react";
import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders application", () => {
  render(<App />);
  const linkElement = screen.getByText(/Article Information Parser/i);
  expect(linkElement).toBeInTheDocument();
});
