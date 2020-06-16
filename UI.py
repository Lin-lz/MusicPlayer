# -*- coding: utf-8 -*-
import re
import sys
import time
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
import ico      # 图标文件

class WinForm(QWidget):
    def __init__(self,parent=None):
        super(WinForm,self).__init__(parent)
        self.resize(640,480)
        self.setWindowTitle("MusicPlayer")
    
        # 获取系统当前路径
        self.cur_path = QFileInfo(__file__).absolutePath()     
        # 创建字典保存音乐名和路径
        self.music_list = {}
        # 初始当前系统音量
        self.sys_volume = 30 
        # 是否静音
        self.isVolume = True
        # 是否暂停
        self.isPause = True
        # 是否第一次运行
        self.isFirst = True
        # 音乐时间
        self.music_time = 0
        # 音频时间
        self.playtime = 0
        # 音乐索引
        self.current_index = -1
        # ListWidget是否为空
        self.isEmpty = True
        # 是否循环模式
        self.isCircle = True    # 默认循环
        # 是否循环播放
        self.isOrder = False
        # 正则匹配规则
        self.pattern = re.compile(r"!(.*?).mp3$")
        
        # 无关变量(测试)
        self.unknow = -1

        # 设置背景图片
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap(':/picturess/background.jpg')))  
        self.setPalette(palette)
    
        # 设置图标
        self.setWindowIcon(QIcon(":/picturess/Music.ico"))

        self.initUI()
    
    def initUI(self):
        self.layout = QVBoxLayout()                     # 总体布局
        self.btn_layout = QHBoxLayout()                 # 按钮布局
        self.music_slider_layout = QHBoxLayout()        # 音乐滑动条布局
        self.volume_slider_layout = QHBoxLayout()       # 音量滑动条布局

        # 设置控件间距
        #self.music_slider_layout.setSpacing(50)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.statusBar.showMessage("Starting.....",2000)
        

        # 信息
        self.logo_label = QLabel("CopyRight©1701-林亮钊-171100009")
        self.logo_label.setAlignment(Qt.AlignHCenter)
        self.logo_label.setStyleSheet("color:black")

        # 音乐开始时间
        self.start_time_label = QLabel("00:00")
        self.start_time_label.setStyleSheet("color:white")

        # 音乐结束时间
        self.end_time_label = QLabel("00:00")
        self.end_time_label.setStyleSheet("color:white")

        # 音量标志
        self.volume_label = QLabel()
        self.volume_label.setFixedSize(32,32)
        self.volume_label.setStyleSheet("QLabel{border-image: url(:/picturess/volume_up.png)}")

        # 定时器
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.time_handle) 

        # 音乐播放器
        self.player = QMediaPlayer()
        self.player.setVolume(self.sys_volume)
        self.player.durationChanged.connect(self.setTime)

        # 选择音乐按钮
        self.open_btn = QPushButton()
        self.open_btn.setFixedSize(64,64)
        self.btn_layout.addWidget(self.open_btn)
        self.open_btn.clicked.connect(self.choose_musics)
        self.open_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Disc.png)}")

        # 上一首按钮
        self.pre_btn = QPushButton()
        self.pre_btn.setFixedSize(64,64)
        self.btn_layout.addWidget(self.pre_btn)
        self.pre_btn.clicked.connect(self.pre_play)
        self.pre_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Previous.png)}")

        # 播放暂停按钮
        self.start_btn = QPushButton()
        self.start_btn.setFixedSize(64,64)
        self.btn_layout.addWidget(self.start_btn)
        self.start_btn.clicked.connect(self.start_play)
        self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Play.png)}")

        # 下一首按钮
        self.next_btn = QPushButton()
        self.next_btn.setFixedSize(64,64)
        self.btn_layout.addWidget(self.next_btn)
        self.next_btn.clicked.connect(self.next_play)
        self.next_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Next.png)}")

        # 静音按钮
        self.clear_volume_btn = QPushButton()
        self.clear_volume_btn.setFixedSize(32,32)
        self.clear_volume_btn.clicked.connect(self.clear_volume)
        self.clear_volume_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/volume.png)}")

        # 显示列表，用以显示音乐信息
        self.listWidget = QListWidget()
        #self.listWidget.itemClicked.connect(self.listWidget_clicked)       # 单击
        self.listWidget.itemDoubleClicked.connect(self.listWidget_clicked)  # 双击播放
        self.listWidget.setStyleSheet("background-color:transparent")       # 背景透明
        self.listWidget.setFrameShape(QListWidget.NoFrame)                  # 无边框
        
        # 右键菜单
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)          # 允许右键产生菜单
        self.listWidget.customContextMenuRequested.connect(self.mouse_right_clicked)    # 连接槽函数


        # 水平音量滑动条
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider_layout.addWidget(self.clear_volume_btn)
        self.volume_slider_layout.addWidget(self.volume_slider,0,Qt.AlignVCenter)
        self.volume_slider_layout.addWidget(self.volume_label)
        self.volume_slider.setValue(self.sys_volume)        # 设置当前值为初始系统音量值
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setMaximumWidth(200)
        self.volume_slider.valueChanged.connect(self.setVolume)
    
        # 水平音乐进度条
        self.music_slider = QSlider(Qt.Horizontal)
        self.music_slider_layout.addWidget(self.start_time_label,0,Qt.AlignRight)
        self.music_slider_layout.addWidget(self.music_slider,0,Qt.AlignVCenter)
        self.music_slider_layout.addWidget(self.end_time_label)
        self.music_slider.setMinimum(0)
        self.music_slider.setMaximumWidth(400)
        self.music_slider.sliderMoved.connect(self.music_moved)
        self.music_slider.sliderReleased.connect(self.slider_moved)
        self.music_slider.valueChanged.connect(self.circle_play)

        # 布局
        self.layout.addWidget(self.statusBar)           # 状态栏
        self.layout.addWidget(self.listWidget)
        self.layout.addLayout(self.music_slider_layout)
        self.layout.addLayout(self.btn_layout)
        self.layout.addLayout(self.volume_slider_layout)
        self.layout.addWidget(self.logo_label)

        self.setLayout(self.layout)
    
    # 双击击音乐列表
    def listWidget_clicked(self,item):
        
        # ubuntu 要
        self.music_time = 0
        self.music_slider.setValue(0)
        self.start_time_label.setText("00:00")
        self.end_time_label.setText("00:00")
        
        self.timer.start()
        
        #self.start_btn.setText("Pause")
        self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Pause.png)}")

        url = QUrl.fromLocalFile((self.music_list[item.text()]) )
        #url = QUrl(self.songlist[1])
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()

        self.isFirst = False    # 如果有音乐点击，则不为第一次

        self.current_index = self.listWidget.currentRow()   # 测试顺序播放

        self.statusBar.showMessage(("当前播放:" + item.text()),2000)

    # 时间处理
    def time_handle(self):
        if self.music_time < self.playtime:
            self.music_time += 1000
            self.music_slider.setValue(self.music_time)
            self.start_time_label.setText(time.strftime('%M:%S', time.localtime(self.player.position()/1000))) 
            #print("moved")
        else:
             self.music_time = 0

    # 获取音频总时长 
    def setTime(self):
        self.playtime = self.player.duration()
        self.music_slider.setMaximum(self.playtime)
        self.end_time_label.setText(time.strftime('%M:%S', time.localtime(self.player.duration()/1000)))
        #print(self.playtime)
      
    # 选择音乐
    def choose_musics(self):
        # 返回： fanme 为路径; _ 为文件类型
        fname,_ = QFileDialog.getOpenFileName(self,'请选择音乐文件',self.cur_path,'Music(*.mp3 *.wav *.ogg *.flac)')

        # 未选择音乐，弹出对话框
        if fname == '':
            QMessageBox.about(self,"Tips","您未添加音乐！")
            return
        
        # 正则表达获取音乐名
        music_path = (fname)
        songs_names = str(self.pattern.findall(fname)).strip("[]").strip("'")
        print(songs_names)

        # 如添加同一首音乐，弹出对话框
        if songs_names in self.music_list:
            QMessageBox.about(self,"Tips","音乐已在播放列表中！")
            return


        self.isEmpty = False    # 如果有音乐添加，则不为空

        
        self.music_list[songs_names] = music_path
        self.listWidget.addItem(songs_names)
      

    # 下一首
    def next_play(self):
        if self.isEmpty == True:
                QMessageBox.about(self,"Tips","当前列表无音乐！")
                return

        if self.isPause == False:
            #self.start_btn.setText("Pause") 
            self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Pause.png)}")
            self.isPause = True
         
        next_index = self.listWidget.currentRow() + 1
        self.current_index = next_index
        #print(self.current_index)
        
        if (self.current_index + 1) > self.listWidget.count():
            QMessageBox.about(self,"Tips","当前已是最后一首！")
            return

        self.music_time = 0
        self.music_slider.setValue(0)
        self.timer.start()      # 测试
        
        self.listWidget.setCurrentRow(self.current_index)
        url = QUrl.fromLocalFile((self.music_list[self.listWidget.item(self.current_index).text()]) )
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()

        self.statusBar.showMessage(("当前播放:" + self.listWidget.item(self.current_index).text()),2000)
    
    # 上一首
    def pre_play(self):
        if self.isEmpty == True:
            QMessageBox.about(self,"Tips","当前列表无音乐！")
            return
              
        if self.isPause == False:
            #self.start_btn.setText("Pause")
            self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Pause.png)}")
            self.isPause = True

        pre_index = self.listWidget.currentRow() - 1
        self.current_index = pre_index
        #print(self.current_index)

        
        if self.current_index < 0:
            QMessageBox.about(self,"Tips","当前已是第一首！")
            return

        self.music_time = 0
        self.music_slider.setValue(0)
        self.timer.start()          # 测试

        self.listWidget.setCurrentRow(self.current_index)
        url = QUrl.fromLocalFile((self.music_list[self.listWidget.item(self.current_index).text()]) )
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()
        
        self.statusBar.showMessage(("当前播放:" + self.listWidget.item(self.current_index).text()),2000)
        
    # 播放暂停
    def start_play(self):
        # 第一次运行
        if self.isFirst:
            
            if self.isEmpty == True:
                QMessageBox.about(self,"Tips","当前列表无音乐！")
                return
            
            else:
                
                # 测试
                self.timer.start()  
                  
                self.isFirst = False
                self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Pause.png)}")
                self.current_index = 0
                self.listWidget.setCurrentRow(self.current_index)
                url = QUrl.fromLocalFile((self.music_list[self.listWidget.item(self.current_index).text()]) )
                content = QMediaContent(url)
                self.player.setMedia(content)
                self.player.play()

                self.statusBar.showMessage(("当前播放:" + self.listWidget.item(self.current_index).text()),2000)
                #pass
                
        # 不是第一次运行
        else:
            if self.isPause:
                self.timer.stop()
                #self.start_btn.setText("Play")
                self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Play.png)}")
                self.isPause = False
                self.player.pause()
                
                self.statusBar.showMessage("已暂停！",2000)
            else:
                self.timer.start()
                #self.start_btn.setText("Pause")
                self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Pause.png)}")
                self.isPause = True
                self.player.play()

                self.statusBar.showMessage(("当前播放:" + self.listWidget.currentItem().text()),2000)
            
            
    # 设置音量
    def setVolume(self,Volume_value):
        self.player.setVolume(Volume_value)
        self.statusBar.showMessage(("当前音量：%d" % Volume_value),2000)

    # 静音
    def clear_volume(self):
        if self.isVolume == True:
            self.statusBar.showMessage("已静音！",2000)
            self.player.setVolume(0)
            self.clear_volume_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/volume_mute.png)}")
            self.isVolume = False
        else:
            self.statusBar.showMessage(("当前音量：%d" % self.volume_slider.value()),2000)
            self.player.setVolume(self.volume_slider.value())
            self.clear_volume_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/volume.png)}")
            self.isVolume = True
    
    # 拖动音乐进度条
    def music_moved(self):
        self.music_time = self.music_slider.value()
        self.player.setPosition(self.music_time)

    # 释放音乐进度条
    def slider_moved(self):
        self.music_slider.setValue(self.music_time)


    # 顺序播放
    def order_play(self):
        if self.player.position() == self.player.duration() and self.isCircle == False and self.isOrder == True and self.music_slider.value() != 0:        
            print("Order Mode")
            
            next_index = self.listWidget.currentRow() + 1
            self.current_index = next_index

            # 最后一首播放完成后暂停播放
            if (self.current_index + 1) > self.listWidget.count():                
                self.player.stop()
                self.timer.stop()

                self.isPause = False
                self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Play.png)}")
                return

            self.music_time = 0
            self.music_slider.setValue(0)
            self.timer.start()      
        
            self.listWidget.setCurrentRow(self.current_index)
            url = QUrl.fromLocalFile((self.music_list[self.listWidget.item(self.current_index).text()]) )
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()

                      
    # 单曲循环
    def circle_play(self):  
        if self.player.position() == self.player.duration() and self.isCircle == True and self.isOrder == False and self.music_slider.value() != 0: 
            print("Cicle Mode")
            
            self.music_time = 0
            self.music_slider.setValue(0)
            self.timer.start()
            
            next_index = self.listWidget.currentRow() 
            self.current_index = next_index
            self.listWidget.setCurrentRow(self.current_index)
            
            url = QUrl.fromLocalFile((self.music_list[self.listWidget.item(self.current_index).text()])) 
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()    
            self.statusBar.showMessage(("当前播放:" + self.listWidget.item(self.current_index).text()),2000)
            
            
    
    # 鼠标右键
    def mouse_right_clicked(self,pos):
        menu = QMenu()
        item1 = menu.addAction(u"删除选中音乐")
        item2 = menu.addAction(u"清空播放列表")
        item3 = menu.addAction(u"单曲循环")
        item4 = menu.addAction(u"顺序播放")
        action = menu.exec_(self.listWidget.mapToGlobal(pos))
        
        # 删除音乐
        if action == item1:
            del self.music_list[self.listWidget.currentItem().text()]   # 删除字典
            self.listWidget.takeItem(self.listWidget.currentRow())      # 删除播放列表 

            self.music_time = 0           
            self.music_slider.setValue(0)
            self.start_time_label.setText("00:00")
            self.end_time_label.setText("00:00")

            self.statusBar.showMessage("音乐已删除",2000)

            # 播放列表无音乐
            if self.listWidget.currentRow() < 0:
                self.timer.stop()
                self.player.stop()

                self.isEmpty = True
                self.isFirst = True
                
                self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Play.png)}")
                self.statusBar.showMessage("音乐已删除",2000)
                QMessageBox.about(self,"Tips","当前无音乐！")
                return 
            
            # 播放列表存在音乐
            else:
                # 播放状态，自动跳转下一首
                if self.player.state() == QMediaPlayer.PlayingState:
                    self.timer.start()
                    
                    self.current_index = self.listWidget.currentRow()      
                    self.listWidget.setCurrentRow(self.current_index)
                    
                    url = QUrl.fromLocalFile((self.music_list[self.listWidget.item(self.current_index).text()])) 
                    content = QMediaContent(url)
                    self.player.setMedia(content)
                    self.player.play()
                
                else:
                    self.timer.stop()

                    self.current_index = self.listWidget.currentRow()      
                    self.listWidget.setCurrentRow(self.current_index)

                    url = QUrl.fromLocalFile((self.music_list[self.listWidget.item(self.current_index).text()])) 
                    content = QMediaContent(url)
                    self.player.setMedia(content)
                    self.player.stop()

        
        # 清空播放列表    (True)
        elif action == item2:
            self.player.stop()
            self.timer.stop()

            self.listWidget.clear()     # 清空播放列表
            self.music_list.clear()     # 清空字典

            self.music_time = 0
            self.music_slider.setValue(0)
            self.start_time_label.setText("00:00")
            self.end_time_label.setText("00:00")
            
            self.isEmpty = True
            self.isFirst = True
                     
            self.start_btn.setStyleSheet("QPushButton{border-image: url(:/picturess/Play.png)}")
            QMessageBox.about(self,"Tips","当前无音乐！")
            return

        # 单曲循环            
        elif action == item3:
            self.isCircle = True        # 循环
            self.isOrder = False
            self.music_slider.valueChanged.connect(self.circle_play)
            print("单曲循环模式")
        
        # 顺序播放
        elif action == item4:
            self.isCircle = False       # 不循环
            self.isOrder = True
            self.music_slider.valueChanged.connect(self.order_play)
            print("顺序播放模式")
        else:
            return

                             
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WinForm()
    win.show()
    sys.exit(app.exec_())