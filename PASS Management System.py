import sys, pickle, os
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.font_manager as fm
from datetime import datetime
import copy
## from collections import deque 필요시 개선

class UVMS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.main_widget = QWidget()
        self.graph_window = QMainWindow()
        self.cycle_select_widget = QWidget()
        
        # 화면 전환용 Widget 설정
        self.widget_list = QStackedWidget()
                  
        self.UVMS_contract = QGroupBox("계약관리")
        self.UVMS_management = QGroupBox("인원관리")
        self.UVMS_history = QGroupBox("내역")
        
        self.widget_list.addWidget(self.UVMS_contract)
        self.widget_list.addWidget(self.UVMS_management)
        self.widget_list.addWidget(self.UVMS_history)
        
        # 메인_버튼
        btn_contract = QPushButton("계약관리", self)
        btn_contract.resize(btn_contract.sizeHint())
        btn_contract.clicked.connect(self.btn_contractClicked)
        
        btn_management = QPushButton("인원관리", self)
        btn_management.resize(btn_management.sizeHint())
        btn_management.clicked.connect(self.btn_managementClicked)
        
        btn_history = QPushButton("내역", self)
        btn_history.resize(btn_history.sizeHint())
        btn_history.clicked.connect(self.btn_historyClicked)

        # 계약_위젯
        contract_helper_label = QLabel("도와주는 사람", self.UVMS_contract)
        contract_helped_label = QLabel("도움받는 사람", self.UVMS_contract)
        self.combo_contract_helper = QComboBox(self.UVMS_contract)
        self.combo_contract_helped = QComboBox(self.UVMS_contract)
        contract_arrow = QLabel("→", self.UVMS_contract)
        contract_arrow.setAlignment(Qt.AlignCenter)
        # contract_arrow.font().setPointSize(100)
        contract_arrow.font().setBold(True)
        contract_reason_label = QLabel("사유", self.UVMS_contract)
        self.contract_reason_text = QTextEdit(self.UVMS_contract)
 
        self.setComboBox(self.dataLoad())
            
        btn_contract_accept = QPushButton("확인", self.UVMS_contract)
        btn_contract_accept.resize(btn_contract_accept.sizeHint())
        btn_contract_accept.clicked.connect(self.btn_contract_acceptClicked)
        
        # 인적_위젯
        btn_management_add = QPushButton("추가", self.UVMS_management)
        btn_management_add.resize(btn_management_add.sizeHint())
        btn_management_add.clicked.connect(self.btn_management_addClicked)
        
        btn_management_del = QPushButton("삭제", self.UVMS_management)
        btn_management_del.resize(btn_management_del.sizeHint())
        btn_management_del.clicked.connect(self.btn_management_delClicked)
        
        btn_management_viz = QPushButton("시각화", self.UVMS_management)
        btn_management_viz.resize(btn_management_viz.sizeHint())
        btn_management_viz.clicked.connect(self.btn_management_vizClicked)
        
        # 내역 위젯
        btn_history_recover = QPushButton("되돌리기", self.UVMS_history)
        btn_history_recover.resize(btn_history_recover.sizeHint())
        btn_history_recover.clicked.connect(self.btn_history_recoverClicked)
        
        # 메인_레이아웃
        main_grid = QGridLayout(self.main_widget)
        main_grid.setSpacing(5)
        
        main_grid.addWidget(self.widget_list, 0, 0, 4, 3)
        main_grid.addWidget(btn_contract, 0, 3)
        main_grid.addWidget(btn_management, 1, 3)
        main_grid.addWidget(btn_history, 2, 3)
        
        self.setCentralWidget(self.main_widget)
        
        # 계약 레이아웃
        contract_grid = QGridLayout(self.UVMS_contract)
        contract_grid.addWidget(contract_helper_label,0,0,1,1)
        contract_grid.addWidget(contract_helped_label,0,2,1,1)
        contract_grid.addWidget(self.combo_contract_helper,1,0,1,1)
        contract_grid.addWidget(contract_arrow,1,1,1,1)
        contract_grid.addWidget(self.combo_contract_helped,1,2,1,1)
        contract_grid.addWidget(contract_reason_label,2,0,1,1)
        contract_grid.addWidget(self.contract_reason_text,3,0,1,3)
        contract_grid.addWidget(btn_contract_accept,4,1)
        
        # 인적 위젯 -> 테이블 위젯
        self.management_table = QTableWidget(self.UVMS_management)
        self.management_table.setColumnCount(5)
        self.management_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.management_table.setHorizontalHeaderLabels(["이름","→","←","→ 목록","← 목록"])
        self.management_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setTableItems()
        
        # 인적_테이블_레이아웃
        manangement_grid = QGridLayout(self.UVMS_management)
        manangement_grid.addWidget(self.management_table,0,0,3,4)
        manangement_grid.addWidget(btn_management_add, 3, 0)
        manangement_grid.addWidget(btn_management_del, 3, 1)
        manangement_grid.addWidget(btn_management_viz, 3, 3)
        
        # 내역 위젯 -> 테이블 위젯
        self.history_table = QTableWidget(self.UVMS_history)
        self.history_table.setColumnCount(3)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setHorizontalHeaderLabels(["날짜","계약내용","사유"])
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHistoryTableItems()
        
        # 내역_테이블_레이아웃
        history_grid = QGridLayout(self.UVMS_history)
        history_grid.addWidget(self.history_table,0,0,3,4)
        history_grid.addWidget(btn_history_recover, 3, 3)
        
        # 메인_상태표시줄
        self.statusBar()
        
        # 메인_창설정
        self.resize(500, 300)
        self.center(self.main_widget)
        self.setWindowTitle("근무관리프로그램")
        self.show()
        
        # 그래프_창설정
        self.graph_window.setWindowTitle("그래프 시각화")
        self.graph_window.resize(500,400)
        self.center(self.graph_window)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure) 
        self.graph_window.addToolBar(NavigationToolbar(self.canvas, self))
    
    def center(self, widget):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        widget.move(qr.topLeft())
    
    def btn_contractClicked(self):
        self.widget_list.setCurrentIndex(0)
        self.setComboBox(self.dataLoad())
        self.contract_reason_text.clear()
    
    def btn_managementClicked(self):
        self.widget_list.setCurrentIndex(1)
        self.setTableItems()
        
    def btn_historyClicked(self):
        self.widget_list.setCurrentIndex(2)
        self.setHistoryTableItems()
        
    def btn_contract_acceptClicked(self):      
        # 이름이 같은 경우
        if self.combo_contract_helped.currentText() == self.combo_contract_helper.currentText():
            QMessageBox.warning(self,'오류','이름이 같습니다.')
        # 이름이 다른 경우
        else:
            long_cycle, short_cycle = self.Exhaustive_Search()
        
            if long_cycle:
                # 사이클 있는 경우
                def btn_acceptClicked():
                    if rbtn_long_cycle.isChecked():
                        data = self.dataLoad()
                        recent_data = copy.deepcopy(data[0][0])
                        recent_data[str(self.combo_contract_helper.currentText())][str(self.combo_contract_helped.currentText())] += 1
                        
                        for i in range(len(long_cycle)-1):
                            recent_data[long_cycle[i]][long_cycle[i+1]] -= 1
                    
                        data.insert(0, [recent_data, [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(self.combo_contract_helper.currentText())+" → "+str(self.combo_contract_helped.currentText()), self.contract_reason_text.toPlainText()]])
                        self.dataSave(data)
                    else:
                        data = self.dataLoad()
                        recent_data = copy.deepcopy(data[0][0])
                        recent_data[str(self.combo_contract_helper.currentText())][str(self.combo_contract_helped.currentText())] += 1
                        
                        for i in range(len(short_cycle)-1):
                            recent_data[short_cycle[i]][short_cycle[i+1]] -= 1
                    
                        data.insert(0, [recent_data, [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(self.combo_contract_helper.currentText())+" → "+str(self.combo_contract_helped.currentText()), self.contract_reason_text.toPlainText()]])
                        self.dataSave(data)
            
                    text.deleteLater()
                    btn_accept.deleteLater()
                    btn_cancle.deleteLater()
                    cycle_select_widget_layout.deleteLater()
                    if long_cycle == short_cycle:
                        rbtn_long_cycle.deleteLater()
                    else:
                        rbtn_long_cycle.deleteLater()
                        rbtn_short_cycle.deleteLater()
                    self.cycle_select_widget.close() 
                
                def btn_cancleClicked():
                    text.deleteLater()
                    btn_accept.deleteLater()
                    btn_cancle.deleteLater()
                    cycle_select_widget_layout.deleteLater()
                    if long_cycle == short_cycle:
                        rbtn_long_cycle.deleteLater()
                    else:
                        rbtn_long_cycle.deleteLater()
                        rbtn_short_cycle.deleteLater()
                    self.cycle_select_widget.close() 
                    
                self.cycle_select_widget.setWindowTitle("순환 선택")
                self.cycle_select_widget.resize(200,100)
                self.center(self.cycle_select_widget)
                
                text = QLabel("순환을 선택하세요.")
                btn_accept = QPushButton('확인')
                btn_cancle = QPushButton('취소')
                
                cycle_select_widget_layout = QGridLayout(self.cycle_select_widget)
                cycle_select_widget_layout.setSpacing(5)
                
                if long_cycle == short_cycle:
                    rbtn_long_cycle = QRadioButton('→'.join(long_cycle))
                    rbtn_long_cycle.setChecked(True)
                    cycle_select_widget_layout.addWidget(text, 0, 0, 1, 2)
                    cycle_select_widget_layout.addWidget(rbtn_long_cycle, 1, 0, 1, 2)
                    rbtn_long_cycle.toggled.connect(lambda : rbtn_long_cycle.setChecked(True))    # 라디오 버튼 한개일 때 체크 안풀리게
                    cycle_select_widget_layout.addWidget(btn_accept, 2, 0)
                    cycle_select_widget_layout.addWidget(btn_cancle, 2, 1)
                    
                else:
                    rbtn_long_cycle = QRadioButton('→'.join(long_cycle))
                    rbtn_long_cycle.setChecked(True)
                    rbtn_short_cycle = QRadioButton('→'.join(short_cycle))
                    cycle_select_widget_layout.addWidget(text, 0, 0, 1, 2)
                    cycle_select_widget_layout.addWidget(rbtn_long_cycle, 1, 0, 1, 2)
                    cycle_select_widget_layout.addWidget(rbtn_short_cycle, 2, 0, 1, 2)
                    cycle_select_widget_layout.addWidget(btn_accept, 3, 0)
                    cycle_select_widget_layout.addWidget(btn_cancle, 3, 1)
                    
                btn_accept.clicked.connect(btn_acceptClicked)
                btn_cancle.clicked.connect(btn_cancleClicked)
                
                self.cycle_select_widget.show()        
                    
            else:
                # 사이클 없는 경우
                # 최종 확인 메세지 띄우고 확인 누르면 -> 노드 추가
                reply = QMessageBox.question(self, '최종확인', str(self.combo_contract_helper.currentText())+" → "+str(self.combo_contract_helped.currentText())+'\n계약을 진행하겠습니까?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                
                if reply == QMessageBox.Yes:
                    data = self.dataLoad()
                    recent_data = copy.deepcopy(data[0][0])
                    recent_data[str(self.combo_contract_helper.currentText())][str(self.combo_contract_helped.currentText())] += 1
                    data.insert(0, [recent_data, [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(self.combo_contract_helper.currentText())+" → "+str(self.combo_contract_helped.currentText()), self.contract_reason_text.toPlainText()]])
                    self.dataSave(data)
                else:
                    pass
                
    def btn_management_addClicked(self):
        text, ok = QInputDialog.getText(self, "인원추가", "이름입력")
        
        if ok:
            data = self.dataLoad()
            recent_data = copy.deepcopy(data[0][0])
            
            # 공백을 입력하거나 이미 있는 사람을 등록하는 경우
            if str(text) == "" or str(text) in recent_data.keys():
                pass
            else:
                recent_data[str(text)] = defaultdict(int)
                data.insert(0, [recent_data, [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "인원추가", str(text)+" 추가"]])
                self.dataSave(data)
                self.setTableItems()
        
    def btn_management_delClicked(self):
        reply = QMessageBox.question(self, '인원삭제', '선택한 인원을 삭제하시겠습니까?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            data = self.dataLoad()
            table_data = copy.deepcopy(data[0][0])
            
            del table_data[self.management_table.item(self.management_table.currentRow(), 0).text()]
            for u, v in table_data.items():
                for w, s in v.items():
                    if w == self.management_table.item(self.management_table.currentRow(), 0).text() and s > 0:
                        table_data[u][w] -= 1
                        
            data.insert(0, [table_data, [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "인원삭제", self.management_table.item(self.management_table.currentRow(), 0).text()+" 삭제"]])
                         
            self.dataSave(data)
            self.setTableItems()
    
    def btn_management_vizClicked(self):
        def btn_closeClicked():
            self.graph_window.close()
            
        plt.clf()
        btn_close = QPushButton('닫기')
        btn_close.clicked.connect(btn_closeClicked)
        
        self.graph_widget = QWidget()
        self.graph_window.setCentralWidget(self.graph_widget)
        
        graph_widget_layout = QGridLayout(self.graph_widget)
        
        graph_widget_layout.addWidget(self.canvas, 0,0,1,4)
        graph_widget_layout.addWidget(btn_close, 1,3)
        
        G = nx.DiGraph()
        G.clear()
        data = self.dataLoad()
        recent_data = data[0][0]
        
        G.add_nodes_from([ name for name in recent_data.keys()])
        for u, v in recent_data.items():
             for w, s in [(helped, num) for helped, num in v.items() if num > 0]:
                G.add_edge(u, w, weight=s)
        
        pos=nx.shell_layout(G)
        labels = nx.get_edge_attributes(G,'weight')
        
        #font_name = fm.FontProperties(fname='./NanumGothic-Bold.ttf').get_name()
        nx.draw(G, pos, with_labels = True, font_weight = "bold", width=5, node_size=1000, arrowsize=20, font_family='UnDotum')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=15, font_family='UnDotum')
        
        self.canvas.draw_idle()
        self.graph_window.show()
            
    def btn_history_recoverClicked(self):
        reply = QMessageBox.question(self, '되돌리기', "되돌리기를 진행하시겠습니까?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                
        if reply == QMessageBox.Yes:
            data = self.dataLoad()
            insert_data = copy.deepcopy(data[self.history_table.currentRow()][0])
            reason = data[self.history_table.currentRow()][1][0] + " " + data[self.history_table.currentRow()][1][1] + f'({data[self.history_table.currentRow()][1][2]})'
            data.insert(0, [insert_data, [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "되돌리기", reason]])
            self.dataSave(data)
            self.setHistoryTableItems()
        else:
            pass
        
    def Exhaustive_Search(self):
        # 순환 탐색
        cycle = []
        traced = []
        data = self.dataLoad()
        recent_data = data[0][0]
        recent_data[str(self.combo_contract_helper.currentText())][str(self.combo_contract_helped.currentText())] += 1
        
        def dfs(name):
            # 현재 순환 구조라면
            if name in traced:
                traced.append(name)
                cycle.append(traced[:])
                del traced[-1]
                return
            
            # 현재 순환 목록에 넣기
            traced.append(name)
            
            # 자식 노드 dfs
            for child_name in [ u for u, v in recent_data[name].items() if v > 0]:
                dfs(child_name)
    
            # 탐색 종료 후 순환 목록에서 삭제
            traced.remove(name)

            return
        
        dfs(str(self.combo_contract_helper.currentText()))
        
        # 순환이 있다면
        if cycle:
            long_cycle = max(cycle, key=len)
            short_cycle = min(cycle, key=len)
        
            return long_cycle, short_cycle
        
        else:
            return [], []
    
    def setTableItems(self):
        data = self.dataLoad()
        recent_data = data[0][0]
        self.management_table.setRowCount(len(recent_data.keys()))
                
        i = 0
        for name, plus_dict in recent_data.items():
            plus_dict = { u : v for u, v in plus_dict.items() if v > 0 }
            minus_dict = { u : v[name] for u, v in recent_data.items() if v[name] > 0 }
            plus_str = ', '.join([ f'{u}({v})' for u, v in plus_dict.items()])
            minus_str = ', '.join([ f'{u}({v})' for u, v in minus_dict.items()])
            self.management_table.setItem(i, 0, QTableWidgetItem(name))
            self.management_table.setItem(i, 1, QTableWidgetItem(str(sum(plus_dict.values()))))
            self.management_table.setItem(i, 2, QTableWidgetItem(str(sum(minus_dict.values()))))
            self.management_table.setItem(i, 3, QTableWidgetItem(plus_str))
            self.management_table.item(i, 3).setToolTip(plus_str)
            self.management_table.setItem(i, 4, QTableWidgetItem(minus_str))
            self.management_table.item(i, 4).setToolTip(minus_str)
            i = i + 1
            
        header = self.management_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    
    def setHistoryTableItems(self):
        table_data = self.dataLoad()
        self.history_table.setRowCount(len(table_data))
        
        i = 0
        for data in table_data:
            self.history_table.setItem(i, 0, QTableWidgetItem(data[1][0]))
            self.history_table.setItem(i, 1, QTableWidgetItem(data[1][1]))
            self.history_table.setItem(i, 2, QTableWidgetItem(data[1][2]))
            self.history_table.item(i, 2).setToolTip(data[1][2])
            i = i + 1
            
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            
    def setComboBox(self, table_data):
        table_data = table_data[0][0]
        self.combo_contract_helped.clear()
        self.combo_contract_helper.clear()
        
        for name in table_data.keys():
            self.combo_contract_helped.addItem(name)
            self.combo_contract_helper.addItem(name)
        
    def dataSave(self, table_data):
        with open("data.pickle", "wb") as f:
                pickle.dump(table_data, f)
    
    def dataLoad(self):
        # 파일이 없는 경우
        if not os.path.isfile("data.pickle"):
            with open("data.pickle", "wb") as f:
                pickle.dump([[dict(), [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "파일생성", "빈 파일 생성"]]], f)
        
        with open("data.pickle", "rb") as f:
            try:
                table_data = pickle.load(f)
            # 파일 비어있는 경우
            except EOFError:
                table_data = [[dict(), [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "파일생성", "빈 파일 생성"]]]
                self.dataSave(table_data)
        return table_data
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = UVMS()
    sys.exit(app.exec_())
    
        