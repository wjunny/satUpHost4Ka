# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_form.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QFrame, QGroupBox, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1080, 904)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(500, 500))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(400, 400))
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QFrame.Shape.Box)
        self.frame_2.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")

        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.horizontalLayout.addWidget(self.frame_2)

        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy1)
        self.scrollArea.setMinimumSize(QSize(310, 0))
        self.scrollArea.setFrameShape(QFrame.Shape.Box)
        self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(False)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 312, 833))
        self.groupBox4 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox4.setObjectName(u"groupBox4")
        self.groupBox4.setGeometry(QRect(10, 420, 291, 241))
        self.groupBox4.setFlat(False)
        self.groupBox4.setCheckable(False)
        self.verticalLayout = QVBoxLayout(self.groupBox4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(2, 6, 2, 6)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setContentsMargins(5, 5, 5, 5)
        self.label_4 = QLabel(self.groupBox4)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.AzEdit = QLineEdit(self.groupBox4)
        self.AzEdit.setObjectName(u"AzEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.AzEdit)

        self.label_5 = QLabel(self.groupBox4)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.EleEdit = QLineEdit(self.groupBox4)
        self.EleEdit.setObjectName(u"EleEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.EleEdit)

        self.label_9 = QLabel(self.groupBox4)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.PolarComboBox = QComboBox(self.groupBox4)
        self.PolarComboBox.addItem("")
        self.PolarComboBox.addItem("")
        self.PolarComboBox.setObjectName(u"PolarComboBox")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.PolarComboBox)

        self.label_10 = QLabel(self.groupBox4)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.CompEdit = QLineEdit(self.groupBox4)
        self.CompEdit.setObjectName(u"CompEdit")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.CompEdit)

        self.label_17 = QLabel(self.groupBox4)
        self.label_17.setObjectName(u"label_17")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_17)

        self.UseCalibCheckBox = QCheckBox(self.groupBox4)
        self.UseCalibCheckBox.setObjectName(u"UseCalibCheckBox")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.UseCalibCheckBox)

        self.CalibFileLineEdit = QLineEdit(self.groupBox4)
        self.CalibFileLineEdit.setObjectName(u"CalibFileLineEdit")
        self.CalibFileLineEdit.setReadOnly(True)

        self.formLayout.setWidget(5, QFormLayout.ItemRole.SpanningRole, self.CalibFileLineEdit)

        self.OpenCalibFileButton = QPushButton(self.groupBox4)
        self.OpenCalibFileButton.setObjectName(u"OpenCalibFileButton")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.OpenCalibFileButton)


        self.verticalLayout.addLayout(self.formLayout)

        self.StartButton = QPushButton(self.scrollAreaWidgetContents)
        self.StartButton.setObjectName(u"StartButton")
        self.StartButton.setGeometry(QRect(10, 700, 89, 25))
        self.StopButton = QPushButton(self.scrollAreaWidgetContents)
        self.StopButton.setObjectName(u"StopButton")
        self.StopButton.setGeometry(QRect(130, 700, 89, 25))
        self.groupBox1 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox1.setObjectName(u"groupBox1")
        self.groupBox1.setGeometry(QRect(10, 20, 291, 91))
        self.horizontalLayout_6 = QHBoxLayout(self.groupBox1)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(2, 6, 2, 6)
        self.formLayout_4 = QFormLayout()
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.formLayout_4.setVerticalSpacing(10)
        self.formLayout_4.setContentsMargins(5, 5, 5, 5)
        self.label = QLabel(self.groupBox1)
        self.label.setObjectName(u"label")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.PAAPortComboBox = QComboBox(self.groupBox1)
        self.PAAPortComboBox.setObjectName(u"PAAPortComboBox")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.PAAPortComboBox)

        self.AntTypeComboBox = QComboBox(self.groupBox1)
        self.AntTypeComboBox.addItem("")
        self.AntTypeComboBox.addItem("")
        self.AntTypeComboBox.setObjectName(u"AntTypeComboBox")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.AntTypeComboBox)

        self.label_7 = QLabel(self.groupBox1)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_7)


        self.horizontalLayout_6.addLayout(self.formLayout_4)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.scrollArea)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Signal Analyzer (VNA)", None))
        self.groupBox4.setTitle(QCoreApplication.translate("MainWindow", u"Test Param", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Beam Azimuth (Degree)", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Beam Elevation (Degree)", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Polarization", None))
        self.PolarComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Left", None))
        self.PolarComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Right", None))

        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Compensation (db)", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Use Calibration", None))
        self.UseCalibCheckBox.setText("")
        self.OpenCalibFileButton.setText(QCoreApplication.translate("MainWindow", u"Calibration File", None))
        self.StartButton.setText(QCoreApplication.translate("MainWindow", u"Start Test", None))
        self.StopButton.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.groupBox1.setTitle(QCoreApplication.translate("MainWindow", u"Antenna", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"PAA Serial Port", None))
        self.AntTypeComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Receiving", None))
        self.AntTypeComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Transmitting", None))

        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Type", None))
    # retranslateUi

