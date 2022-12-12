import React, { useState, useEffect } from "react";
import {
  Typography,
  Box,
  LinearProgress,
  Card,
  CardContent,
  Paper,
  List,
  ListItem,
  ListItemText,
  Tooltip,
  IconButton,
  Button,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import moment from "moment";
// import RefreshIcon from "@mui/icons-material/Refresh";
import { apiCall } from "./apiCalls";
// import pdf from "./update_instructions.pdf";

const useStyles = makeStyles({
  cards: {
    gap: "10px",
    flexWrap: "wrap",
  },
  card: {
    flex: "1 1 250px",
  },
  rotate: {
    animation: "$rotation 700ms linear infinite",
  },
  descs: {
    padding: "0 10px !important",
    textAlign: "center",
  },
  "@keyframes rotation": {
    "0%": {
      transform: "rotate(0deg)",
    },
    "100%": {
      transform: "rotate(360deg)",
    },
  },
});

const Home = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [info, setInfo] = useState(null);

  const classes = useStyles();

  useEffect(() => {
    apiCall()
      .then((res) => res.json())
      .then((res) => {
        localStorage.setItem("db_version", res.version);
        setInfo(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(
          "Error has occured while connecting to the server: " + String(err)
        );
      });
  }, []);

  const generateCard = (title, content) => (
    <Card className={classes.card}>
      <CardContent>
        <Typography color="textSecondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h5" component="h2">
          {content}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <div>
      <Box my={3} display="flex" justifyContent="space-between">
        <Typography variant="h4">Home</Typography>
      </Box>
      <Box display="flex" justifyContent="center" className={classes.cards}>
        {loading && !error && <LinearProgress />}
        {error && <Typography color="error">{error}</Typography>}
        {info && (
          <>
            {generateCard(
              "Number of the publications in the database",
              info.publications_count
            )}
            {generateCard(
              "Number of the authors in the database",
              info.authors_count
            )}
            {generateCard(
              "Date of last database update",
              moment(info.last_modified).format("DD.MM.YYYY HH:mm")
            )}
            {generateCard(
              "Version of the database schema",
              info.db_schema_version
            )}
            {generateCard("Version of the database content", info.version)}
            {generateCard("DBLP version release date", info.dblp_version)}
            {generateCard(
              "Semantic Scholar version release date",
              info.semantic_scholar_version
            )}
            {generateCard(
              "AMiner/MAG version release date",
              info.aminer_mag_version
            )}
          </>
        )}
      </Box>
      <Box my={2}>
        <Box mb={2}>
          <Typography variant="h5">Credits</Typography>
        </Box>
        <Paper>
          <Box mx={2} pt={2}>
            <Typography variant="h6">
              This application is being maintained and improved by
            </Typography>
          </Box>
          <List>
            <ListItem>
              <ListItemText
                primary="Gilles Magalhães Ribeiro"
                secondary="VU Amsterdam student"
              />
            </ListItem>
          </List>
          <Box mx={2} pt={2}>
            <Typography variant="h6">
              This application was initially created by
            </Typography>
          </Box>
          <List>
            <ListItem>
              <ListItemText
                primary="Bianca-Maria Cosma"
                secondary="TU Delft"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Przemysław Kowalewski"
                secondary="TU Delft"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Oskar Lorek"
                secondary="TU Delft"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Michał Okoń"
                secondary="TU Delft"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Jakub Tokarz"
                secondary="TU Delft"
              />
            </ListItem>
          </List>
          <Box mx={2}>
            <Typography variant="h6">Supervised by</Typography>
          </Box>
          <ListItem>
            <ListItemText
              primary="prof.dr.ir Alexandru Iosup"
              secondary="@Large Research"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="ir. Laurens Versluis"
              secondary="@Large Research"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Dan Andreescu"
              secondary="Teaching Assistant at TU Delft"
            />
          </ListItem>
        </Paper>
      </Box>
    </div>
  );
};

export default Home;
