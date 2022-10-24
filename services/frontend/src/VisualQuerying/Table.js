import React from "react";
import {
  TableContainer,
  Table,
  TableCell,
  TableHead,
  TableRow,
  TableBody,
  TablePagination,
  TableSortLabel,
  Button,
  useTheme,
} from "@mui/material";
import columns from "./columns";

const CustomTable = ({
  data,
  rawQueryExecuted,
  sort,
  setSort,
  page,
  setPage,
  pageSize,
  setPageSize,
  count,
  setCurrentArticle,
  setShowAbstract,
  setShowAuthors,
}) => {
  const theme = useTheme();

  return <>
    <TableContainer>
      <Table>
        <TableHead>
          {!rawQueryExecuted ? (
            <TableRow>
              {columns.map((column) => (
                <TableCell key={column.id}>
                  {!rawQueryExecuted ? (
                    <TableSortLabel
                      active={sort[0] === column.id}
                      direction={sort[0] === column.id ? sort[1] : "asc"}
                      onClick={() => {
                        if (sort[0] !== column.id)
                          return setSort([column.id, "asc"]);
                        if (sort[0] === column.id && sort[1] === "asc")
                          return setSort([column.id, "desc"]);
                        return setSort([column.id, "asc"]);
                      }}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
              <TableCell key="authors">Authors</TableCell>
              <TableCell key="abstract">Abstract</TableCell>
            </TableRow>
          ) : (
            <TableRow>
              {Object.keys(data[0]).map((key) => (
                <TableCell key={key}>{key}</TableCell>
              ))}
            </TableRow>
          )}
        </TableHead>
        {!rawQueryExecuted ? (
          <TableBody>
            {data.map((row, rowId) => (
              <TableRow hover key={rowId}>
                {columns
                  .filter((c) => c.id !== "doi")
                  .map((column) => (
                    <TableCell key={column.id + "-" + rowId}>
                      {row[column.id] ? row[column.id] : "-"}
                    </TableCell>
                  ))}
                <TableCell>
                  {row.doi ? (
                    <a
                      href={"https://www.doi.org/" + row.doi}
                      target="__blank"
                    >
                      {row.doi}
                    </a>
                  ) : (
                    "-"
                  )}
                </TableCell>
                <TableCell key={"authors-" + rowId}>
                  {row["authors"] && row["authors"].length > 0 ? (
                    <Button
                      variant="contained"
                      color={
                        theme.palette.mode === "light" ? "primary" : "default"
                      }
                      onClick={() => {
                        setCurrentArticle(row);
                        setShowAuthors(true);
                      }}
                    >
                      Show Authors
                    </Button>
                  ) : (
                    "Not provided"
                  )}
                </TableCell>
                <TableCell key={"abstract-" + rowId}>
                  {row["abstract"] ? (
                    <Button
                      variant="contained"
                      color={
                        theme.palette.mode === "light" ? "primary" : "default"
                      }
                      onClick={() => {
                        setCurrentArticle(row);
                        setShowAbstract(true);
                      }}
                    >
                      Show Abstract
                    </Button>
                  ) : (
                    "Not provided"
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        ) : (
          <TableBody>
            {data.map((row, rowId) => (
              <TableRow hover key={rowId}>
                {Object.keys(data[0]).map((key) => (
                  <TableCell key={rowId + "-" + key}>
                    {row[key] ? row[key] : "-"}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        )}
      </Table>
    </TableContainer>
    {!rawQueryExecuted && (
      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50, 100, 500]}
        component="div"
        count={count}
        rowsPerPage={pageSize}
        page={page - 1}
        onPageChange={(_, d) => setPage(d + 1)}
        onRowsPerPageChange={(e) => {
          setPageSize(e.target.value);
          setPage(1);
        }}
      />
    )}
  </>;
};

export default CustomTable;
