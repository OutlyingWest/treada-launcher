import os.path
import sys
from typing import Dict, Tuple

import pandas as pd
from PySide6.QtCore import Slot, QDir, Signal, QObject
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QApplication, QMainWindow, QFileSystemModel
from PySide6 import QtCore

from wrapper.misc.collections.ww_data_collecting.ui.ui_pyside6_base.ui_collect_ww_data import Ui_MainWindow


class MainWindow(QMainWindow):
    plot_signal = Signal(dict)
    extract_signal = Signal(list)
    close_event_signal = Signal()

    def __init__(self, ww_descriptions: pd.Series, file_manager_root_path: str):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_select_distributions_combo_box(ww_descriptions)
        # Creation of file system model for treeView file manager
        self.file_system_model = QFileSystemModel()
        self.populate_file_manager(file_manager_root_path)
        self.ui.PlotButton.clicked.connect(self.plot_clicked)
        self.ui.ExtractButton.clicked.connect(self.extract_clicked)
        # self.setWindowTitle()

    def setup_select_distributions_combo_box(self, ww_descriptions: pd.Series):
        self.ui.SelectDistributionComboBox.addItems(ww_descriptions)

    def get_add_checkbox_status(self):
        return self.ui.AddToExistsCheckBox.isChecked()

    def get_log_checkbox_status(self):
        return self.ui.LogScaleCheckBox.isChecked()

    def get_selected_distribution_index(self):
        selected_index = self.ui.SelectDistributionComboBox.currentIndex()
        return selected_index + 1

    def populate_file_manager(self, root_path: str):
        self.file_system_model.setRootPath(QtCore.QDir.rootPath())
        self.file_system_model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        self.ui.treeView.setModel(self.file_system_model)
        self.ui.treeView.setRootIndex(self.file_system_model.index(root_path))
        self.ui.treeView.setSortingEnabled(True)
        self.ui.treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.ui.treeView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    @Slot()
    def plot_clicked(self):
        is_add = self.get_add_checkbox_status()
        is_log = self.get_log_checkbox_status()
        selected_index = self.get_selected_distribution_index()
        selected_ww_dir_names, _ = self._get_file_manager_selected()
        self.plot_signal.emit({
            'is_add': is_add,
            'is_log': is_log,
            'ww_number': selected_index,
            'dirs': selected_ww_dir_names,
        })

    @Slot()
    def extract_clicked(self):
        self.ui.statusbar.showMessage('Extracting...')
        # self.statusbar_message_slot('Extracting...')
        _, selected_stage_dir_paths = self._get_file_manager_selected()
        self.extract_signal.emit(selected_stage_dir_paths)

    def _get_file_manager_selected(self) -> Tuple[dict, list]:
        selected_ww_dirs = dict()
        selected_stage_dir_paths = list()
        selected_indexes = self.ui.treeView.selectedIndexes()
        if not selected_indexes:
            return selected_ww_dirs, selected_stage_dir_paths
        for index in selected_indexes:
            if index.column() == 0:
                dir_name_index = index.sibling(index.row(), 0)
                dir_item_path = self.file_system_model.filePath(dir_name_index)
                _, deeper_dir, deepest_dir = dir_item_path.rsplit('/', maxsplit=2)
                if deepest_dir.isnumeric():
                    if not selected_ww_dirs.get(deeper_dir):
                        selected_ww_dirs[deeper_dir] = list()
                    selected_ww_dirs[deeper_dir].append(int(deepest_dir))
                else:
                    selected_stage_dir_paths.append(dir_item_path)
        return selected_ww_dirs, selected_stage_dir_paths

    @Slot(str)
    def statusbar_message_slot(self, message: str):
        self.ui.statusbar.showMessage(message)

    def closeEvent(self, event):
        self.close_event_signal.emit()
        event.accept()


def run_ui_application(ww_descriptions=pd.Series()):
    app = QApplication()
    main_window = MainWindow(ww_descriptions)
    main_window.show()
    sys.exit(app.exec())


def main():
    run_ui_application()


if __name__ == '__main__':
    main()
