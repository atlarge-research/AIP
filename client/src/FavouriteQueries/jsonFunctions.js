import fileDownload from "js-file-download";
import moment from "moment";

export const exportToJson = (queries) => {
  fileDownload(JSON.stringify({ queries }), "AIP-FQ-" + moment() + ".json");
};
