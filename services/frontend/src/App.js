import React, { useState, useEffect } from "react";

import { makeStyles } from "@mui/styles";

import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";

import Typography from "@mui/material/Typography";

import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Divider from "@mui/material/Divider";

import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import SearchOutlinedIcon from "@mui/icons-material/SearchOutlined";
import StarBorderOutlinedIcon from "@mui/icons-material/StarBorderOutlined";
import WhatshotOutlinedIcon from "@mui/icons-material/WhatshotOutlined";
import FavoriteBorderOutlinedIcon from "@mui/icons-material/FavoriteBorderOutlined";
import PeopleIcon from "@mui/icons-material/People";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import GitHubIcon from "@mui/icons-material/GitHub";

import useMediaQuery from "@mui/material/useMediaQuery";
import { createTheme, ThemeProvider, StyledEngineProvider, adaptV4Theme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

import Box from "@mui/material/Box";
import Container from "@mui/material/Container";

import {
  BrowserRouter as Router,
  Switch,
  Route,
  NavLink,
  Redirect,
} from "react-router-dom";
import routes from "./routes";

import Home from "./Home";
import VisualQuerying from "./VisualQuerying";
import AuthorsExploration from "./AuthorsExploration";
import RisingStars from "./RisingStars";
import HotKeywords from "./HotKeywords";
import FavouriteQueries from "./FavouriteQueries";

const useStyles = makeStyles({
  list: {
    width: 250,
  },
  link: {
    textDecoration: "none",
    color: "inherit",
  },
});

const App = () => {
  const [drawerOpened, setDrawerOpened] = useState(false);

  const classes = useStyles();

  const [darkMode, setDarkMode] = useState(
    useMediaQuery("(prefers-color-scheme: dark)")
  );
  const theme = React.useMemo(
    () =>
      createTheme({
        palette: {
          mode: darkMode ? "dark" : "light",
        },
      }),
    [darkMode]
  );

  useEffect(() => {
    const themeLS = localStorage.getItem("theme");

    if (themeLS === "dark") setDarkMode(true);
    if (!theme) localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, []);

  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Drawer
            anchor="left"
            open={drawerOpened}
            onClose={() => setDrawerOpened(false)}
          >
            <div
              onClick={() => setDrawerOpened(false)}
              onKeyDown={() => setDrawerOpened(false)}
              className={classes.list}
            >
              <List>
                <ListItem
                  button
                  component={NavLink}
                  to={routes.home}
                  className={classes.link}
                  activeClassName="Mui-selected"
                  exact
                >
                  <ListItemIcon>
                    <HomeOutlinedIcon />
                  </ListItemIcon>
                  <ListItemText primary="Home"></ListItemText>
                </ListItem>
                <Divider />
                <ListItem
                  button
                  component={NavLink}
                  to={routes.visualQuerying}
                  className={classes.link}
                  activeClassName="Mui-selected"
                >
                  <ListItemIcon>
                    <SearchOutlinedIcon />
                  </ListItemIcon>
                  <ListItemText primary="Visual Quering"></ListItemText>
                </ListItem>
                <ListItem
                  button
                  component={NavLink}
                  to={routes.favouriteQueries}
                  className={classes.link}
                  activeClassName="Mui-selected"
                >
                  <ListItemIcon>
                    <FavoriteBorderOutlinedIcon />
                  </ListItemIcon>
                  <ListItemText primary="Favourite Queries"></ListItemText>
                </ListItem>
                <ListItem
                  button
                  component={NavLink}
                  to={routes.risingStars}
                  className={classes.link}
                  activeClassName="Mui-selected"
                >
                  <ListItemIcon>
                    <StarBorderOutlinedIcon />
                  </ListItemIcon>
                  <ListItemText primary="Rising Stars"></ListItemText>
                </ListItem>
                <ListItem
                  button
                  component={NavLink}
                  to={routes.authorsExploration}
                  className={classes.link}
                  activeClassName="Mui-selected"
                >
                  <ListItemIcon>
                    <PeopleIcon />
                  </ListItemIcon>
                  <ListItemText primary="Authors Exploration"></ListItemText>
                </ListItem>

                <ListItem
                  button
                  component={NavLink}
                  to={routes.hotKeywords}
                  className={classes.link}
                  activeClassName="Mui-selected"
                >
                  <ListItemIcon>
                    <WhatshotOutlinedIcon />
                  </ListItemIcon>
                  <ListItemText primary="Hot Keywords"></ListItemText>
                </ListItem>
              </List>
            </div>
          </Drawer>
          <AppBar position="fixed" color={darkMode ? "default" : "primary"}>
            <Toolbar>
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                style={{ width: "100%" }}
              >
                <Box display="flex" justifyContent="center" alignItems="center">
                  <IconButton
                    edge="start"
                    color="inherit"
                    aria-label="open drawer"
                    onClick={() => setDrawerOpened(true)}
                    size="large">
                    <MenuIcon />
                  </IconButton>
                  <Typography variant="h6" noWrap>
                    Article Information Parser
                  </Typography>
                </Box>
                <Box>
                  <a
                    href="https://github.com/atlarge-research/AIP"
                    target="__blank"
                  >
                    <IconButton size="large">
                      <GitHubIcon style={{ color: "white" }} />
                    </IconButton>
                  </a>
                  <IconButton
                    edge="start"
                    color="inherit"
                    aria-label="open drawer"
                    onClick={() => {
                      localStorage.setItem("theme", !darkMode ? "dark" : "light");
                      setDarkMode(!darkMode);
                    }}
                    style={{ marginLeft: "6px" }}
                    size="large">
                    {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
                  </IconButton>
                </Box>
              </Box>
            </Toolbar>
          </AppBar>
          <Box height={64} />
          <Container maxWidth="xl">
            <Switch>
              <Route path={routes.home} component={Home} exact />
              <Route
                path={routes.authorsExploration}
                component={AuthorsExploration}
              />
              <Route path={routes.visualQuerying} component={VisualQuerying} />
              <Route path={routes.risingStars} component={RisingStars} />
              <Route path={routes.hotKeywords} component={HotKeywords} />
              <Route
                path={routes.favouriteQueries}
                component={FavouriteQueries}
              />

              <Route
                path={routes.home}
                component={() => <Redirect to={routes.home} />}
              />
            </Switch>
          </Container>
        </Router>
      </ThemeProvider>
    </StyledEngineProvider>
  );
};

export default App;
