import React from "react";
import { render, screen } from "@testing-library/react";
import Table from "./Table";
import mockData from "./mockData";

test("renders a table", () => {
  render(
    <Table
      data={mockData}
      sort={["id", "asc"]}
      count={10}
      pageSize={10}
      page={1}
    />
  );
  const linkElement = screen.getByText(/TU Deflt/i);
  expect(linkElement).toBeInTheDocument();
});
