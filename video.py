import sys
import time
from functools import partial
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

import requests
# from PyQt5.QtCore import QMutex, QObject, QStringListModel, QThread, pyqtSignal
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from video_class import *
from video_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.save_path = os.getcwd()
        self.ui.open_path.clicked.connect(self.open_path)

    def open_path(self):
        os.startfile(self.save_path)

    def set_save_path(self):
        dirname = QFileDialog.getExistingDirectory(self, "请选择保存文件夹", '.')
        if dirname:
            self.save_path = dirname

    def search_test(self):
        mov_name = self.ui.mov_name.text()
        self.ui.show_mov.clear()
        if len(mov_name) != 0:
            # gather = self. _mov(mov_name)
            s_thread = SearchMov(search_mov,mov_name)
            s_thread.show_mov_items.connect(self.set_item)
            s_thread.show_mov_click.connect(self.set_mov)
            s_thread.error_ms.connect(self.Warning_msbox)
            s_thread.start()
            s_thread.exec()
        else:
            QMessageBox.information(self, 'Warning','请输入电影名')

    def Warning_msbox(self, information):
        QMessageBox.information(self, 'Warnings', information, QMessageBox.Ok)  

    def set_item(self, movlist):
        self.ui.show_mov.addItems(movlist)
    
    def set_mov(self, movlink):
        self.ui.show_mov.clicked.connect(partial(self.mov_choose, movlink))

    def mov_choose(self, movlink, item):
        print(movlink, sys._getframe().f_lineno)
        choose = movlink[item.row()]  
        print(choose, sys._getframe().f_lineno)
        downgather = select_dl(choose)
        print(downgather, sys._getframe().f_lineno)
        mov_epi = []
        for mov in downgather:
            slist = mov.split("/")[-1]
            mov_epi.append(slist)
        self.ui.show_mov.clear()
        self.ui.show_mov.disconnect()
        boxes = []
        for i in mov_epi:
            ches = QCheckBox(i)
            boxes.append(ches)
            item = QListWidgetItem()
            self.ui.show_mov.addItem(item)
            self.ui.show_mov.setItemWidget(item,ches)
        self.ui.checkBox.stateChanged[int].connect(partial(self.select_all,boxes))
        self.ui.download.clicked.connect(partial(self.ch_select,boxes,downgather))

    def ch_select(self, boxes, downgather, state):
        count = self.ui.show_mov.count()
        cb_list = [self.ui.show_mov.itemWidget(self.ui.show_mov.item(i))
            for i in range(count) ]    
        # print(cb_list, sys._getframe().f_lineno)
        # print(downgather, sys._getframe().f_lineno)
        group = dict(zip(cb_list,downgather))
        print(group, sys._getframe().f_lineno)
        for cb in group.keys():
            if cb.isChecked():
                self.start_dl(group[cb])

    def select_all(self, args, state):
        if state == 2:
            for ch in args:
                ch.setCheckState(2)
        if state == 0:
            for ch in args:
                ch.setCheckState(0)

    def start_dl(self, choose):
        movies = []
        # print(type(choose))
        if type(choose) == str:
            movies.append(choose)
        else:
            movies = choose
        print(movies)
        pool = QThreadPool.globalInstance()
        pool.setMaxThreadCount(1)

        for mov in movies:
            filename = mov.split('/')[-1]
            file_pname = os.path.join(self.save_path,filename)
            args = [file_pname,mov,filename]
            self.dl = Downloader(args)
            self.dl.signal.progressBarValue.connect(self.set_progress)
            self.dl.signal.labelValue.connect(self.set_dlmov)
            pool.start(self.dl)
        # pool.waitForDone()

    def set_dlmov(self,filename):
        self.ui.dl_mov.setText("正在下载：" + filename)

    def set_progress(self, progress):
        self.ui.progressBar.setValue(progress)

class SearchMov(QThread):
    show_mov_items = pyqtSignal(list)
    show_mov_click = pyqtSignal(list)
    error_ms = pyqtSignal(str)

    def __init__(self, func, args):
        super(SearchMov,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(self.args)
        movlist = []
        movlink = []
        if len(self.args) != 0:
            gather = self.result
            print(gather)
            for item in gather:
                a = item['title']
                b = item['link']
                movlist.append(a)
                movlink.append(b)
        print(movlist, sys._getframe().f_lineno)
        if not movlist:
            self.error_ms.emit('没有搜索到该电影')
            print('hello', sys._getframe().f_lineno)
        else:
            self.show_mov_items.emit(movlist)
            self.show_mov_click.emit(movlink)

# 需要注意的是，QRunnable不是一个QObject，因此也就没有内建的与其它组件交互的机制。为了与其它组件进行交互，
# 你必须自己编写低级线程原语，例如使用 mutex 守护来获取结果等。
class Signal(QObject):
    progressBarValue = pyqtSignal(int)  # 更新进度条
    labelValue =pyqtSignal(str)      #更新下载名

class Downloader(QRunnable):
    def __init__(self, args):
        super(Downloader,self).__init__()
        self.args = args
        self.file_pname = args[0]
        self.url = args[1]
        self.filename = args[2]
        self.signal = Signal()

    def run(self):
        savedSize = 0
        print(self.args, sys._getframe().f_lineno)
        print(self.url, sys._getframe().f_lineno)
        self.signal.labelValue.emit(self.filename)
        r = requests.get(self.url,stream=True)
        fileSize = int(r.headers["Content-Length"])
        # print(fileSize)   
        # print (r.status_code)
        if r.status_code == 200:
            with open(self.file_pname, "wb") as code:
                for chunk in r.iter_content(chunk_size=1024): #边下载边存硬盘
                    if chunk:
                        code.write(chunk)
                        savedSize+=len(chunk)
                        progress = int(savedSize / fileSize * 100)
                        self.signal.progressBarValue.emit(progress)
        # self.exit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.ui.mov_name.setPlaceholderText("请输入要下载的电影")
    win.ui.search.clicked.connect(win.search_test)
    win.ui.save_path.clicked.connect(win.set_save_path)
    win.ui.mov_name.setFocus()
    win.ui.mov_name.returnPressed.connect(win.search_test)
    sys.exit(app.exec_())
