import columns from "./columns";
import moment from "moment";
import fileDownload from "js-file-download";
const { parse } = require("json2csv");

const exportToCsv = (data, rawQueryExecuted) => {
  const db_version = localStorage.getItem("db_version");
  let csvData = [];
  data.forEach((row) => {
    const csvRow = {};

    if (!rawQueryExecuted) {
      columns.forEach((column) => {
        csvRow[column.id] = row[column.id] ? row[column.id] : "";
      });
    } else {
      Object.keys(data[0]).forEach((key) => {
        csvRow[key] = row[key] ? row[key] : "";
      });
    }

    if (!rawQueryExecuted) {
      csvRow.abstract = row.abstract ? row.abstract : null;
      csvRow.authors = row.authors
        ? row.authors
            .map(
              (author) =>
                `(${author.name || ""};${author.orcid || ""};${
                  author.first_publication_year || ""
                })`
            )
            .join(";")
        : null;
    }

    csvData.push(csvRow);
  });

  let fields;
  if (!rawQueryExecuted) {
    fields = [...columns.map((column) => column.id), "abstract", "authors"];
  } else {
    fields = Object.keys(data[0]);
  }

  const csv = parse(csvData, { fields });
  const v = db_version ? "__v" + db_version : "";
  fileDownload(csv, "AIP-VQ-" + moment() + v + ".csv");
};

export default exportToCsv;
