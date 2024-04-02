# coding: utf8
import sys
from PySide6 import QtWidgets, QtCore, QtGui
from iqh_func import *

import idquery_rc


version = [1, 3, 0, 20240402]


def accept_warning(widget: QtWidgets.QWidget, condition: bool,
                   caption: str = "警告", text: str = "确定要继续吗？") -> bool:
    if condition:
        b = QtWidgets.QMessageBox.question(widget, caption, text)
        if b == QtWidgets.QMessageBox.StandardButton.No:
            return True
    return False


class UiMainWindow(object):

    def __init__(self, window: QtWidgets.QMainWindow):
        self.sb = window.statusBar()
        self.mb = window.menuBar()
        window.setWindowTitle("ID 查询库")
        window.setWindowIcon(QtGui.QIcon(":/idquery_16.png"))
        window.resize(600, 700)
        self.cw = QtWidgets.QWidget(window)
        window.setCentralWidget(self.cw)
        self.vly_cw = QtWidgets.QVBoxLayout()
        self.cw.setLayout(self.vly_cw)

        self.hly_buttons = QtWidgets.QHBoxLayout()
        self.pbn_insert = QtWidgets.QPushButton("插入", self.cw)
        self.pbn_select_id2group = QtWidgets.QPushButton("ID查小组", self.cw)
        self.pbn_select_group2id = QtWidgets.QPushButton("小组查ID", self.cw)
        self.hly_buttons.addWidget(self.pbn_insert)
        self.hly_buttons.addWidget(self.pbn_select_id2group)
        self.hly_buttons.addWidget(self.pbn_select_group2id)
        self.hly_buttons.addStretch(1)
        self.pbn_clear = QtWidgets.QPushButton("清空两栏", self.cw)
        self.hly_buttons.addWidget(self.pbn_clear)

        self.hly_quantity = QtWidgets.QHBoxLayout()
        self.lne_id_qu = QtWidgets.QLineEdit(self.cw)
        self.lne_group_qu = QtWidgets.QLineEdit(self.cw)
        self.lne_id_qu.setDisabled(True)
        self.lne_group_qu.setDisabled(True)
        self.hly_quantity.addWidget(self.lne_id_qu)
        self.hly_quantity.addWidget(self.lne_group_qu)

        self.hly_body = QtWidgets.QHBoxLayout()
        self.pte_ids = QtWidgets.QPlainTextEdit(self.cw)
        self.pte_groups = QtWidgets.QPlainTextEdit(self.cw)
        self.hly_body.addWidget(self.pte_ids)
        self.hly_body.addWidget(self.pte_groups)

        self.vly_cw.addLayout(self.hly_buttons)
        self.vly_cw.addLayout(self.hly_quantity)
        self.vly_cw.addLayout(self.hly_body)

        self.menu_file = self.mb.addMenu("文件")
        self.act_read_csv = QtGui.QAction("读取 CSV 文件", self.cw)
        self.menu_file.addAction(self.act_read_csv)

        self.menu_about = self.mb.addMenu("关于")
        self.act_about = QtGui.QAction("关于 ID 查询库", self.cw)
        self.menu_about.addAction(self.act_about)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiMainWindow(self)

        self.base_path = iqh_init()
        self.db_name = "idquery.db"
        self.db_conn = iqh_create_conn(self.base_path, self.db_name)
        iqh_create_table(self.db_conn)

        self.ui.pte_ids.textChanged.connect(self.on_pte_ids_text_changed)
        self.ui.pte_groups.textChanged.connect(self.on_pte_groups_text_changed)
        self.ui.pbn_clear.clicked.connect(self.on_pbn_clear_clicked)
        self.ui.act_about.triggered.connect(self.on_act_about_triggered)

        self.ui.pbn_select_id2group.clicked.connect(self.on_pbn_select_id2group_clicked)
        self.ui.pbn_select_group2id.clicked.connect(self.on_pbn_select_group2id_clicked)
        self.ui.pbn_insert.clicked.connect(self.on_pbn_insert_clicked)
        self.ui.act_read_csv.triggered.connect(self.on_act_read_csv_triggered)

    def __del__(self):
        iqh_close_conn(self.db_conn)

    def on_pte_ids_text_changed(self):
        ids = self.ui.pte_ids.toPlainText().strip()
        id_ls = [i.strip() for i in ids.split("\n") if len(i.strip()) != 0]
        self.ui.lne_id_qu.setText(f"ID 数量：{len(id_ls)}")

    def on_pte_groups_text_changed(self):
        groups = self.ui.pte_groups.toPlainText().strip()
        group_ls = [g.strip() for g in groups.split("\n") if len(g.strip()) != 0]
        self.ui.lne_group_qu.setText(f"小组数量：{len(group_ls)}")

    def on_pbn_clear_clicked(self):
        self.ui.pte_ids.clear()
        self.ui.pte_groups.clear()

    def on_act_about_triggered(self):
        ver = f"{version[0]}.{version[1]}.{version[2]}，于 {version[-1]}"
        QtWidgets.QMessageBox.about(
            self, "关于",
            f"版本：{ver}\n数据库路径：\n{str(self.base_path / self.db_name)}"
        )

    def on_pbn_select_id2group_clicked(self):
        raw_ids = self.ui.pte_ids.toPlainText().strip()
        if len(raw_ids) == 0:
            msg = "没有找到有效的 ID"
            self.ui.sb.showMessage(msg)
            QtWidgets.QMessageBox.critical(self, "错误", msg)
            return
        raw_groups = self.ui.pte_groups.toPlainText().strip()
        if accept_warning(self, len(raw_groups) != 0, text="小组栏不为空，确定要覆盖吗？"):
            self.ui.sb.showMessage("请先清空小组栏。")
            return

        id_list = raw_ids.split("\n")
        q_ids = [int(x.strip()) for x in id_list if len(x) != 0 and x.strip().isdigit()]
        result = iqh_select_id2group(self.db_conn, q_ids)
        result_d = {str(id_num): group_name for id_num, group_name in result}
        res_groups = []
        for r in id_list:
            r = r.strip()
            if r in result_d:
                res_groups.append(result_d[r])
            else:
                res_groups.append("")

        self.ui.pte_groups.setPlainText("\n".join(res_groups))

        msg = f"共找到 {len(result)} 条记录。"
        self.ui.sb.showMessage(msg)

    def on_pbn_select_group2id_clicked(self):
        raw_groups = self.ui.pte_groups.toPlainText().strip()
        if len(raw_groups) == 0:
            msg = "没有找到有效的小组"
            self.ui.sb.showMessage(msg)
            QtWidgets.QMessageBox.critical(self, "错误", msg)
            return
        raw_ids = self.ui.pte_ids.toPlainText().strip()
        if accept_warning(self, len(raw_ids) != 0, text="ID 栏不为空，确定要覆盖吗？"):
            self.ui.sb.showMessage("请先清空 ID 栏。")
            return

        group_list = raw_groups.split("\n")
        group = group_list[0].strip()  # 只找第一个小组，后面的忽略
        result = iqh_select_group2id(self.db_conn, group)
        res_ids = [str(id_num) for id_num, _ in result]

        self.ui.pte_ids.setPlainText("\n".join(res_ids))

        msg = f"共找到 {len(result)} 条记录。"
        self.ui.sb.showMessage(msg)

    def on_pbn_insert_clicked(self):
        raw_ids = self.ui.pte_ids.toPlainText().strip()
        raw_groups = self.ui.pte_groups.toPlainText().strip()
        id_list = raw_ids.split("\n")
        group_list = raw_groups.split("\n")
        if accept_warning(self, len(id_list) != len(group_list), text="ID 数量和小组数量不一致，要自动填充小组吗？"):
            self.ui.sb.showMessage("ID 数量和小组数量不一致，未进行自动填充。")
            return

        # 填充并制作数据
        last_group = ""
        len_group_list = len(group_list)
        data = []
        new_ids = []
        for i in range(len(id_list)):
            ids = id_list[i].strip()
            if not (len(ids) != 0 and ids.isdigit()):
                continue
            idi = int(ids)
            if i < len_group_list:
                group = group_list[i]
                last_group = group
            else:
                group = last_group

            data.append((idi, group))
            new_ids.append(idi)

        # 排重
        result = iqh_select_id2group(self.db_conn, new_ids)
        res_ids = [i for i, _ in result]
        new_data = [(i, g) for i, g in data if i not in res_ids]

        self.ui.pte_ids.setPlainText("\n".join([str(i) for i, _ in new_data]))
        self.ui.pte_groups.setPlainText("\n".join([g for _, g in new_data]))

        if len(new_data) != 0:
            iqh_insert_data(self.db_conn, new_data)

        msg = f"一共找到 {len(data)} 个 ID，成功插入 {len(new_data)} 个。"
        self.ui.sb.showMessage(msg)
        QtWidgets.QMessageBox.information(self, "信息", msg)

    def on_act_read_csv_triggered(self):
        if accept_warning(self, len(self.ui.pte_ids.toPlainText().strip()) != 0, text="ID 栏还有内容，确定继续覆盖吗？"):
            self.ui.sb.showMessage("请先清空 ID 栏。")
            return

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开 CSV 文件", "..",
                                                            filter="CSV 文件 (*.csv);;所有文件(*)")
        if len(filename) == 0:
            return

        with open(filename, "r", encoding="utf8") as f:
            lines = f.read()

        id_lines = []
        group_lines = []
        for line in lines.strip().split("\n"):
            ids, group = line.split(",", 1)  # type: str, str
            ids = ids.strip()
            if not (len(ids) != 0 and ids.isdigit()):
                continue
            id_lines.append(ids)
            group_lines.append(group)

        self.ui.pte_ids.setPlainText("\n".join(id_lines))
        self.ui.pte_groups.setPlainText("\n".join(group_lines))


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
