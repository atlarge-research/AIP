import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
} from "@mui/material";

const ImportDialog = ({ showInfo, setShowInfo }) => {
  return (
    <Dialog open={showInfo} onClose={() => setShowInfo(false)}>
      <DialogTitle>Hot Keywords Algorithm</DialogTitle>
      <DialogContent>
        <Typography>
          The aim of the Emerging Keywords feature is to predict what keywords
          will become popular in the close feature. By simply putting the year
          in the "year" field you can see the results of the algorithm run with
          pre-set parameters. However, if you want to experiment with this
          features yourself, there are plenty of options you can configure by
          modifying the parameters in the "advanced options" tab.
        </Typography>
        <Box mb={2} />
        <Typography>
          The algorithm consists of the following steps:
          <ol>
            <li>
              All publications in the database are clustered using the Leiden
              algorithm with the maximal community size of 100.
            </li>
            <li>
              Each cluster is assigned with 25 more suitable features based on
              the contents of the abstracts and the titles of articles
              comprising them.
            </li>
            <li>
              Keywords are aggregated. Each keyword is assigned to a list of
              publications characterized by it.
            </li>
            <li>
              Keywords are filtered out based on 3 criteria- number of
              publications containing them, number of citations received in a
              specific period, and the relative growth of the publication count
              over the years.
            </li>
          </ol>
        </Typography>
        <Box mb={2} />
        <Typography>
          As a user, you can modify the parameters of the 4th step. The meaning
          of those parameters is as follows:
          <ul>
            <li>
              year - Year the emerging keywords are calculated for. Even though
              our functionality is mostly focused on predicting the modern
              keywords, we strongly encourgae you to try out other years and see
              if our predictions are accurate.
            </li>
            <li>
              p_rate - Maximal part of the total number of publications released
              in a given year, that the keywords can be assigned to, in order to
              be declared emerging. In other words, p_max = p_rate * p_total and
              number of publications assigned to a keyword cannot be higher than
              p_max if it is to be declared 'hot'. It is a number between 0 and
              1. The greater the number, the number of keywords is greater and
              the more popular the chosen keywords are.
            </li>
            <li>
              c_rate - Let c_total be the total number of citations received by
              all the publications published in the past dt years from the
              publications released in the past dt years. Let c_min be the
              minimum number of times that articles assigned to a keyword
              released in the past dt years need to be cited by other articles
              released in that period. Then, c_min = c_rate * c_total. It is a
              number between 0 and 1. The greater the number, the number of
              keywords is smaller and the chosen keywords are cited more
              frequently.
            </li>
            <li>
              r_min - Minimal value of the growth factor r, which is calculated
              by dividing the number of keyword-associated publications released
              in the selected 'year' by the number of those released in
              'year'-dt. It can be any positive number. The greater the number,
              the algorithm is more selective and the growth in popularity of
              the chosen keywords is more evident.
            </li>
            <li>
              r_adjustment - If true, the algorithm will be iterated lowering
              r_min at each itteration until a certain number of hot keywords is
              found or the r_min drops below 1.{" "}
            </li>
            <li>
              number_of_features - Number of features that need to be found if
              r_adjustment is set to true. Otherwise, it is ignored.
            </li>
            <li>dt - Time interval to consider during calculations.</li>
          </ul>
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button color="primary" onClick={() => setShowInfo(false)}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ImportDialog;
