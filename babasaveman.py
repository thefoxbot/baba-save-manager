import copy
import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox, QLabel, QLineEdit, QPushButton, QListWidget,
                             QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QGroupBox,
                             QHBoxLayout, QVBoxLayout, QGridLayout, QMessageBox)
from PyQt5 import QtGui


class MainWindow(QWidget):
    def __init__(self, parent=None):
        # this is just placing all the elements in place
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle('Baba Save Manager')

        save_list = QComboBox()
        save_list.currentIndexChanged.connect(self.load_file)
        save_list.setMinimumWidth(150)
        save_label = QLabel('&Save file:')
        save_label.setBuddy(save_list)
        self.save_list = save_list
        data_save = QPushButton('Save changes')
        data_save.clicked.connect(self.data_save)
        data_revert = QPushButton('Revert changes')
        data_revert.clicked.connect(self.revert_data)
        self.save_btn = data_save
        self.revert_btn = data_revert

        top_bar = QHBoxLayout()
        top_bar.addWidget(save_label)
        top_bar.addWidget(save_list)
        top_bar.addWidget(data_save)
        top_bar.addWidget(data_revert)
        top_bar.addStretch(1)

        world_list = QListWidget()
        world_list.setMaximumWidth(150)
        world_list.setHorizontalScrollBarPolicy(1)  # always off
        world_list.currentItemChanged.connect(self.load_world_data)
        world_label = QLabel('&World list:')
        world_label.setBuddy(world_list)
        self.world_list = world_list

        mid_left = QVBoxLayout()
        mid_left.addWidget(world_label)
        mid_left.addWidget(world_list)

        prop_list = QTreeWidget()
        prop_list.setMaximumWidth(170)
        prop_list.setColumnCount(1)
        prop_list.setHeaderHidden(1)
        prop_list.currentItemChanged.connect(self.load_properties)
        prop_label = QLabel('World &data:')
        prop_label.setBuddy(prop_list)
        self.prop_list = prop_list

        mid_center = QVBoxLayout()
        mid_center.addWidget(prop_label)
        mid_center.addWidget(prop_list)

        wname_text = QLineEdit()
        wname_text.setMaximumWidth(180)
        wname_text.textEdited.connect(self.modify_world_name)
        wname_label = QLabel('World &name:')
        wname_label.setBuddy(wname_text)
        world_del = QPushButton('Delete world data')
        world_del.setEnabled(0)
        world_del.clicked.connect(self.delete_world_data)
        self.wname_text = wname_text
        self.del_world_btn = world_del

        world_detail = QHBoxLayout()
        world_detail.addWidget(wname_label)
        world_detail.addWidget(wname_text)
        world_detail.addSpacing(5)
        world_detail.addWidget(world_del)

        pname_text = QLineEdit()
        pname_text.setMaximumWidth(180)
        pname_text.textEdited.connect(self.modify_prop_name)
        pname_label = QLabel('&Property name:')
        pname_label.setBuddy(pname_text)
        prop_del = QPushButton('Delete property')
        prop_del.setEnabled(0)
        prop_del.clicked.connect(self.edit_prop_data)
        self.pname_text = pname_text
        self.prop_btn = prop_del

        prop_detail = QHBoxLayout()
        prop_detail.addWidget(pname_label)
        prop_detail.addWidget(pname_text)
        prop_detail.addSpacing(5)
        prop_detail.addWidget(prop_del)

        props_data = QTableWidget()
        props_data.horizontalHeader().setSectionResizeMode(3)
        props_data.horizontalHeader().hide()
        props_data.verticalHeader().setSectionResizeMode(3)
        props_data.verticalHeader().hide()
        props_data.cellChanged.connect(self.modify_table)
        self.prop_table = props_data

        mid_right = QVBoxLayout()
        mid_right.addItem(world_detail)
        mid_right.addItem(prop_detail)
        mid_right.addWidget(props_data)

        info = QHBoxLayout()
        info.addLayout(mid_left)
        info.addLayout(mid_center)
        info.addLayout(mid_right)

        group = QGroupBox('')
        group.setLayout(info)

        layout = QGridLayout()
        layout.addLayout(top_bar, 0, 0, 1, 1)
        layout.addWidget(group, 1, 0, 1, 1)

        self.setLayout(layout)
        self.show()
        self.setFixedSize(self.size())
        self.setMaximumSize(self.size())

        self.save_data = None
        self.working_copy = None
        self.populating_table = False

    def load_file(self, index):
        self.world_list.clear()
        self.save_btn.setEnabled(0)
        self.revert_btn.setEnabled(0)

        fname = self.save_list.itemText(index)

        data = {}
        key = None
        with open(os.path.join(self.base_path, fname), 'r') as f:
            for line in f:
                line = line.strip()
                if line and line[0] == '[':
                    if key is not None:
                        data[key] = value
                    key = line[1:-1]
                    value = {}
                elif line:
                    k, v = line.split('=')
                    value[k] = v
        data[key] = value

        # restructuring the data to be in a better shape
        world_names = [key for key in data.keys() if not key.endswith('convert') and not key.endswith('converts')
                       and not key.endswith('clears') and not key.endswith('prize') and not key.endswith('complete')
                       and not key.endswith('bonus')]
        world_names.sort()
        save_dict = {}
        for wname in world_names:
            self.world_list.addItem(wname)
            save_dict[wname] = {}
            for key in data:
                trimmed_key = key[len(wname)+1:]
                if not key.startswith(wname):
                    continue
                if not (key == wname or trimmed_key in ['converts', 'clears', 'prize', 'complete', 'bonus']
                        or key.endswith('convert')):
                    continue
                if len(key) < len(wname) or (len(key) > len(wname) and key[len(wname)] != '_'):
                    continue
                save_dict[wname][trimmed_key] = data[key]

        self.save_data = save_dict
        self.working_copy = copy.deepcopy(save_dict)

    def load_world_data(self, cur, prev):
        self.prop_list.clear()
        self.wname_text.setText('')
        self.del_world_btn.setEnabled(0)

        if cur is not None:
            properties = QTreeWidgetItem()
            properties.setText(0, 'Properties')
            converts = QTreeWidgetItem()
            converts.setText(0, 'Level converts')
            self.prop_list.addTopLevelItem(properties)
            self.prop_list.addTopLevelItem(converts)

            world_name = cur.text()
            self.wname_text.setText(world_name)
            self.del_world_btn.setEnabled(1)
            props = []
            convs = []
            for key in self.working_copy[world_name]:
                if key in ['', 'clears', 'prize', 'complete', 'bonus', 'converts']:
                    props.append(key if key else '<main>')
                elif key.endswith('convert'):
                    convs.append(key)
            props.sort()
            convs.sort()

            for k in props:
                child = QTreeWidgetItem()
                child.setText(0, k)
                properties.addChild(child)
            for k in convs:
                child = QTreeWidgetItem()
                child.setText(0, k)
                converts.addChild(child)

            properties.setExpanded(1)
            converts.setExpanded(1)

    def load_properties(self, cur, prev):
        self.populating_table = True
        self.pname_text.setText('')
        self.prop_btn.setEnabled(0)
        self.prop_table.clear()
        self.prop_table.setRowCount(0)
        self.prop_table.setColumnCount(0)

        if cur is not None:
            wname = self.world_list.currentItem().text()
            specifier = cur.text(0)
            if specifier != 'Properties' and specifier != 'Level converts':
                if specifier == '<main>':
                    specifier = ''
                self.pname_text.setText(specifier)
                self.prop_btn.setText('Delete property')
                self.prop_btn.setEnabled(1)
                data = self.working_copy[wname][specifier]
                self.prop_table.setColumnCount(2)
                self.prop_table.setRowCount(len(data)+1)

                row = 0
                data_list = sorted(data.items())
                for k, v in data_list:
                    key = QTableWidgetItem()
                    key.setText(k)
                    val = QTableWidgetItem()
                    val.setText(v)
                    self.prop_table.setItem(row, 0, key)
                    self.prop_table.setItem(row, 1, val)
                    row += 1
            else:
                self.prop_btn.setText('Add property')
                self.prop_btn.setEnabled(1)

        self.populating_table = False

    def modify_world_name(self, new_name):
        old_name = self.world_list.currentItem().text()
        self.world_list.currentItem().setText(new_name)
        self.working_copy[new_name] = self.working_copy[old_name]
        del self.working_copy[old_name]

        self.modification_check()

    def delete_world_data(self):
        wname = self.world_list.currentItem().text()
        self.world_list.takeItem(self.world_list.currentRow())
        del self.working_copy[wname]
        self.load_world_data(self.world_list.currentItem(), None)

        self.modification_check()

    def modify_prop_name(self, new_name):
        if self.prop_btn.text() == 'Delete property':
            wname = self.world_list.currentItem().text()
            old_name = self.prop_list.currentItem().text(0)
            self.prop_list.currentItem().setText(0, new_name)
            self.working_copy[wname][new_name] = self.working_copy[wname][old_name]
            del self.working_copy[wname][old_name]

        self.modification_check()

    def edit_prop_data(self):
        wname = self.world_list.currentItem().text()
        if self.prop_btn.text() == 'Delete property':
            pname = self.prop_list.currentItem().text(0)
            self.prop_list.currentItem().parent().removeChild(self.prop_list.currentItem())
            del self.working_copy[wname][pname]
            self.load_properties(self.prop_list.currentItem(), None)
        elif self.prop_btn.text() == 'Add property':
            prop_name = self.pname_text.text()
            new_child = QTreeWidgetItem()
            new_child.setText(0, prop_name)
            self.prop_list.currentItem().addChild(new_child)
            self.working_copy[wname][prop_name] = {}

        self.modification_check()

    def modify_table(self, r, c):
        if self.populating_table:
            return

        # add new row if last row gets filled
        if r == self.prop_table.rowCount() - 1:
            self.prop_table.setRowCount(self.prop_table.rowCount() + 1)

        # delete row if it's empty
        if ((self.prop_table.item(r, 0) is None or self.prop_table.item(r, 0).text() == '')
                and (self.prop_table.item(r, 1) is None or self.prop_table.item(r, 1).text() == '')
                and r != self.prop_table.rowCount() - 1):
            self.prop_table.removeRow(r)

        # update data dictionary
        wname = self.world_list.currentItem().text()
        cat = self.prop_list.currentItem().text(0)
        cat = cat if cat != '<main>' else ''
        self.working_copy[wname][cat] = {}
        for i in range(self.prop_table.rowCount()):
            key = self.prop_table.item(i, 0)
            val = self.prop_table.item(i, 1)
            key = '' if key is None else key.text()
            val = '' if val is None else val.text()
            if key or val:
                self.working_copy[wname][cat][key] = val

        self.modification_check()

    def data_save(self):
        msgbox = QMessageBox()
        msgbox.setWindowTitle('Baba Save Manager')
        msgbox.setText('Do you want to overwrite the save data?')
        msgbox.setIcon(QMessageBox.Question)
        msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.No)
        rval = msgbox.exec_()
        if rval == QMessageBox.Yes:
            self.save_data = copy.deepcopy(self.working_copy)

            fname = self.save_list.currentText()
            with open(os.path.join(self.base_path, fname), 'w') as f:
                for wname in self.save_data:
                    for section in self.save_data[wname]:
                        if section:
                            f.write('[{}_{}]\n'.format(wname, section))
                        else:
                            f.write('[{}]\n'.format(wname))

                        for key, val in self.save_data[wname][section].items():
                            f.write('{}={}\n'.format(key, val))
                        f.write('\n')

        self.modification_check()
        return rval

    def revert_data(self):
        self.working_copy = copy.deepcopy(self.save_data)
        self.load_file(self.save_list.currentIndex())
        self.modification_check()

    def modification_check(self):
        check = self.working_copy != self.save_data
        self.save_btn.setEnabled(check)
        self.revert_btn.setEnabled(check)

    def closeEvent(self, QCloseEvent):
        if self.working_copy != self.save_data:
            msgbox = QMessageBox()
            msgbox.setWindowTitle('Baba Save Manager')
            msgbox.setText('You have unsaved changes.')
            msgbox.setInformativeText('Do you want to save?')
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            msgbox.setDefaultButton(QMessageBox.Cancel)
            rval = msgbox.exec_()
            if rval == QMessageBox.Yes:
                save_res = self.data_save()
                if save_res == QMessageBox.Yes:
                    QCloseEvent.accept()
                else:
                    QCloseEvent.ignore()
            elif rval == QMessageBox.No:
                QCloseEvent.accept()
            else:
                QCloseEvent.ignore()


if __name__ == '__main__':
    # get OS this app is running on and the save path
    path = ''
    if sys.platform.startswith('linux'):
        path = os.path.expanduser('~/.local/share/Baba_Is_You')
    elif sys.platform.startswith('win32'):
        path = os.path.expandvars('%APPDATA%')
        path = os.path.join(path, 'Baba_Is_You')
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'silverhawke.baba.saveman')
    elif sys.platform.startswith('darwin'):
        path = os.path.expanduser('~/Library/Application Support/Baba_Is_You')
    else:
        alert = QMessageBox()
        alert.setText('OS unsupported.')
        alert.exec_()
        sys.exit(1)

    # get the directory contents
    fns = []
    for _, _, fns in os.walk(path):
        break

    # initialize all the app stuff
    app = QApplication([])
    app.setStyle('Fusion')

    window = MainWindow()
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        icon_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        icon_path = os.path.join(icon_path, 'icon.png')
    else:
        icon_path = 'icon.png'
    window.setWindowIcon(QtGui.QIcon(icon_path))
    window.base_path = path
    window.save_list.addItems([fn for fn in fns if fn.endswith('.ba')])

    app.exec_()
