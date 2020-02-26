import os
import sqlite3
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QLineEdit, QGroupBox, QFormLayout, QLabel, QRadioButton, QButtonGroup, QHBoxLayout, QPushButton, QHeaderView, \
    QMainWindow, QFileDialog
from PyQt5.uic.Compiler.qtproxies import QtWidgets

from venue_mappings.venue_map import VenueMapper


def catch_exceptions(t, val, tb):
    QtWidgets.QMessageBox.critical(None,
                                   "An exception was raised",
                                   "Exception type: {}".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'ReWoFi - Related Work Finder'
        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 1000
        self.venue_mapper = VenueMapper()

        if (os.path.exists("../aip.db")):
            self.initUI()
        else:
            QtWidgets.QMessageBox.critical(None,
                                           "Database could not be found",
                                           "Database aip.db could not be found!")

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createFormGroupBox()
        self.table = QTableWidget()
        self.table.setSortingEnabled(True)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Title", "Abstract", "Venue", "Year", "DOI"])
        self.table.setWordWrap(True)

        # Make the table span the entire width. This code must be after setting row and columns or it won't do anything.
        view_types = [QHeaderView.Stretch, QHeaderView.Stretch, QHeaderView.ResizeToContents,
                      QHeaderView.ResizeToContents, QHeaderView.ResizeToContents]
        horizontal_header = self.table.horizontalHeader()

        for column in range(horizontal_header.count()):
            horizontal_header.setSectionResizeMode(column, view_types[column])
            width = horizontal_header.sectionSize(column)
            horizontal_header.setSectionResizeMode(column, QHeaderView.Interactive)
            horizontal_header.resizeSection(column, width)

        # Add box layout, add table to box layout and add box layout to widget
        wid = QWidget(self)
        self.setCentralWidget(wid)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.form_group_box)
        self.layout.addWidget(self.table)
        wid.setLayout(self.layout)

        # Show widget
        self.show()

    def resizeEvent(self, event):
        """ Resize all sections to content and user interactive """
        super(App, self).resizeEvent(event)
        # self.table.resizeRowsToContents()
        header = self.table.horizontalHeader()
        for column in range(header.count()):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
            width = header.sectionSize(column)
            header.setSectionResizeMode(column, QHeaderView.Interactive)
            header.resizeSection(column, width)

    def createFormGroupBox(self):
        self.form_group_box = QGroupBox("Input")
        layout = QFormLayout()

        self.keyword_input = QLineEdit()
        self.keyword_input.setReadOnly(False)
        self.keyword_input.setPlaceholderText("Comma separated keywords")
        layout.addRow(QLabel("Keywords:"), self.keyword_input)

        self.keyword_filter_options = [QRadioButton("All"), QRadioButton("Any")]
        self.keyword_filter_options[0].setChecked(True)
        button_layout = QHBoxLayout()
        self.keyword_option_button_group = QButtonGroup()
        for i in range(len(self.keyword_filter_options)):
            # Add each radio button to the button layout
            button_layout.addWidget(self.keyword_filter_options[i])
            # Add each radio button to the button group & give it an ID of i
            self.keyword_option_button_group.addButton(self.keyword_filter_options[i], i)

        filter_label = QLabel("Match keywords:")
        filter_label.setToolTip(
            "All will find articles containing ALL keywords, whereas any will match articles containing ANY of the keywords")
        layout.addRow(filter_label, button_layout)

        self.blackwords_input = QLineEdit()
        self.blackwords_input.setReadOnly(False)
        self.blackwords_input.setPlaceholderText("Comma separated filter terms")
        layout.addRow(QLabel("Exclusion filter:"), self.blackwords_input)

        self.blackword_filter_options = [QRadioButton("All"), QRadioButton("Any")]
        self.blackword_filter_options[0].setChecked(True)
        button_layout = QHBoxLayout()
        self.blackwords_option_button_group = QButtonGroup()
        for i in range(len(self.blackword_filter_options)):
            # Add each radio button to the button layout
            button_layout.addWidget(self.blackword_filter_options[i])
            # Add each radio button to the button group & give it an ID of i
            self.blackwords_option_button_group.addButton(self.blackword_filter_options[i], i)

        filter_label = QLabel("Filter option:")
        filter_label.setToolTip(
            "All will remove articles containing ALL keywords, whereas any will remove articles containing ANY keywords")
        layout.addRow(filter_label, button_layout)

        self.venues_input = QLineEdit()
        self.venues_input.setReadOnly(False)
        self.venues_input.setPlaceholderText("Comma separated venue acronyms, leave blank for all")
        layout.addRow(QLabel("Venues:"), self.venues_input)

        onlyInt = QIntValidator()
        onlyInt.setRange(1900, 2100)

        year_range_layout = QHBoxLayout()
        year_range_layout.setAlignment(Qt.AlignLeft)
        self.start_year_input = QLineEdit()
        self.start_year_input.setReadOnly(False)
        self.start_year_input.setValidator(onlyInt)
        self.start_year_input.setPlaceholderText("Start year (included)")
        self.start_year_input.setText("1980")
        self.start_year_input.setMaximumWidth(150)
        year_range_layout.addWidget(self.start_year_input)

        self.end_year_input = QLineEdit()
        self.end_year_input.setReadOnly(False)
        self.end_year_input.setPlaceholderText("End year (included)")
        self.end_year_input.setText("2019")
        self.end_year_input.setMaximumWidth(150)
        self.end_year_input.setValidator(onlyInt)

        year_range_layout.addWidget(QLabel("End year:"))
        year_range_layout.addWidget(self.end_year_input)

        year_range_layout.addStretch()  # Fill space to prevent it centering elements

        layout.addRow(QLabel("Start year:"), year_range_layout)  # Don't add the Qlabel to the QHBoxLayout, it messes
        # with the alignment of the label.

        button_box = QHBoxLayout()
        self.search_button = QPushButton('Search', self)
        self.search_button.clicked.connect(self.search)
        self.export_button = QPushButton('Export Results', self)
        self.export_button.clicked.connect(self.export_results)
        button_box.addWidget(self.search_button)
        button_box.addWidget(self.export_button)
        layout.addRow(button_box)

        self.form_group_box.setLayout(layout)

    def createTable(self):
        self.table.clearContents()
        # Set the content
        self.table.setRowCount(len(self.matching_articles))

        for i in range(len(self.matching_articles)):
            for j in range(5):
                self.table.setItem(i, j, QTableWidgetItem(str(self.matching_articles[i][j])))

        self.search_button.setDisabled(False)

    def get_keywords(self):
        return [str(k).lower().strip() for k in self.keyword_input.text().split(",") if len(k) > 0]

    def get_blackwords(self):
        return [str(k).lower().strip() for k in self.blackwords_input.text().split(",") if len(k) > 0]

    def get_venues(self):
        if len(self.venues_input.text().strip()) > 0:
            return [str(k).lower().strip() for k in self.venues_input.text().split(",")]
        else:
            return [str(k).lower() for k in self.venue_mapper.venues.keys()]

    def get_start_year(self):
        return self.start_year_input.text()

    def get_end_year(self):
        return self.end_year_input.text()

    def search(self):
        self.search_button.setDisabled(True)
        conn = sqlite3.connect('aip.db')
        conn.set_trace_callback(print)
        c = conn.cursor()

        keywords = self.get_keywords()
        if len(keywords) == 0:
            return
        match_all_keywords = self.keyword_filter_options[0].isChecked()

        blackwords = self.get_blackwords()
        venues = self.get_venues()
        start_year = self.get_start_year()
        end_year = self.get_end_year()

        seen_id_set = set()
        duplicate_keyword_set = set()
        blackword_set = set(blackwords)
        blackword_filter = all if self.blackword_filter_options[0].isChecked() else any

        self.matching_articles = []
        first_run_done = False

        grouped_keywords = []

        for keyword in keywords:
            keyword = keyword.lower()  # Use lower case so that we do not potentially miss articles
            if match_all_keywords and first_run_done and len(self.matching_articles) == 0:
                break  # If we already are out of matches, just skip the other keywords.

            if keyword in duplicate_keyword_set:
                continue

            duplicate_keyword_set.add(keyword)

            # Add variations of the keyword if it contains spaces
            aliases = ['%{}%'.format(keyword)]
            if " " in keyword:
                alias = keyword.replace(" ", "-")
                if alias not in duplicate_keyword_set:
                    aliases.append("%{}%".format(alias))
                    duplicate_keyword_set.add(alias)

                alias = keyword.replace(" ", "")
                if alias not in duplicate_keyword_set:
                    aliases.append("%{}%".format(alias))
                    duplicate_keyword_set.add(alias)

            grouped_keywords.append(aliases)

        query_parts_per_group_of_aliases = []
        keywords_for_query = []
        for group in grouped_keywords:
            query_parts_per_group_of_aliases.append("({})".format(
                " OR ".join(["(lower(title) LIKE ? OR lower(abstract) LIKE ?)"] * len(group))
            ))

            # Add all aliases twice, once to match in the title and one to match for in the abstract
            for i in group:
                keywords_for_query.append(i)
                keywords_for_query.append(i)

        query_operator = " AND " if match_all_keywords else " OR "
        query = "SELECT title, abstract, venue, year, doi, id FROM publications WHERE LOWER(venue) IN ({0}) AND {1} AND year BETWEEN ? AND ? ORDER BY year DESC".format(
            ",".join(["?"] * len(venues)),
            "{}".format(query_operator.join(query_parts_per_group_of_aliases))
        )

        # print(query)
        # print(query_parts_per_group_of_aliases)
        # print(keywords_for_query)
        query_result = c.execute(query, venues + keywords_for_query + [start_year, end_year])

        for row in query_result.fetchall():
            title = str(row[0])
            abstract = str(row[1])
            venue = row[2]
            year = row[3]
            doi = row[4]
            id = row[5]

            if len(blackword_set) > 0 \
                    and (blackword_filter(word in title.lower() for word in blackword_set) or
                         blackword_filter(word in abstract.lower() for word in blackword_set)):
                continue

            if id in seen_id_set and not match_all_keywords:
                continue
            seen_id_set.add(id)

            self.matching_articles.append([title, abstract, venue, year, doi])

        self.createTable()

    def export_results(self):
        import csv
        file_path = QFileDialog.getSaveFileName(self, "Save File", os.path.expanduser("~"), '.csv')[0]
        if len(file_path) > 0:
            with open(file_path, 'w', encoding='utf-8') as export_file:
                wr = csv.writer(export_file, quoting=csv.QUOTE_ALL)
                wr.writerows(self.matching_articles)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
