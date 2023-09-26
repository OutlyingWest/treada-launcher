import sys

import pandas as pd
from PySide6.QtCore import Slot, QDir
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QApplication, QMainWindow, QFileSystemModel
from PySide6 import QtCore

from wrapper.misc.collections.ww_data_collecting.ui.ui_pyside6_base.ui_collect_ww_data import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, ww_descriptions: pd.Series, file_manager_root_path: str):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_select_distributions_combo_box(ww_descriptions)
        # Creation of file system model for treeView file manager
        self.file_system_model = QFileSystemModel()
        self.populate_file_manager(file_manager_root_path)
        self.ui.statusbar.showMessage('Statusbar!')

        self.ui.PlotButton.clicked.connect(self.plot)
        self.ui.ExtractButton.clicked.connect(self.extract)

    def setup_select_distributions_combo_box(self, ww_descriptions: pd.Series):
        self.ui.SelectDistributionComboBox.addItems(ww_descriptions)

    def get_selected_distribution_index(self):
        selected_index = self.ui.SelectDistributionComboBox.currentIndex()
        print(f'{selected_index=}')

    def populate_file_manager(self, root_path: str):
        self.file_system_model.setRootPath(QtCore.QDir.rootPath())
        self.file_system_model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        self.ui.treeView.setModel(self.file_system_model)
        self.ui.treeView.setRootIndex(self.file_system_model.index(root_path))
        self.ui.treeView.setSortingEnabled(True)
        self.ui.treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.ui.treeView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    @Slot()
    def plot(self):
        selected_dir_names = self._get_file_manager_selected()
        self.get_selected_distribution_index()
        print(f'{selected_dir_names=}')

    @Slot()
    def extract(self):
        selected_dir_names = self._get_file_manager_selected()
        print(f'{selected_dir_names=}')

    def _get_file_manager_selected(self) -> list:
        selected_indexes = self.ui.treeView.selectedIndexes()
        selected_dir_names = list()
        for index in selected_indexes:
            if index.column() == 0:
                dir_name_index = index.sibling(index.row(), 0)
                selected_dir_names.append(self.file_system_model.fileName(dir_name_index))
        return selected_dir_names


def run_ui_application(ww_descriptions=pd.Series()):
    app = QApplication()
    main_window = MainWindow(ww_descriptions)
    main_window.show()
    sys.exit(app.exec())


def main():
    run_ui_application()


if __name__ == '__main__':
    main()
