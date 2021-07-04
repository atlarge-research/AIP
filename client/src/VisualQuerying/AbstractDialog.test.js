import React from "react";
import { render, screen } from "@testing-library/react";
import AbstractDialog from "./AbstractDialog";

test("renders an abstract dialog", () => {
  render(
    <AbstractDialog
      showAbstract={true}
      setShowAbstract={() => {}}
      currentArticle={{
        title: "test_title",
        name: "test_name",
        year: 2021,
        abstract: "test_abstract",
      }}
    />
  );
  const titleElement = screen.getByText(/test_title/i);
  const nameElement = screen.getByText(/test_name/i);
  const yearElement = screen.getByText(/(2021)/i);
  const abstractElement = screen.getByText(/test_abstract/i);
  expect(titleElement).toBeInTheDocument();
  expect(nameElement).toBeInTheDocument();
  expect(yearElement).toBeInTheDocument();
  expect(abstractElement).toBeInTheDocument();
});
