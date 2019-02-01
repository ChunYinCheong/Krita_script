'''
This script is licensed CC 0 1.0, so that you can learn from it.
------ CC 0 1.0 ---------------
The person who associated a work with this deed has dedicated the work to the public domain by waiving all of his or her rights to the work worldwide under copyright law, including all related and neighboring rights, to the extent allowed by law.
You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.
https://creativecommons.org/publicdomain/zero/1.0/legalcode
'''
from . import myexportlayersdialog
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFormLayout, QListWidget, QHBoxLayout,
                             QDialogButtonBox, QVBoxLayout, QFrame,
                             QPushButton, QAbstractScrollArea, QLineEdit,
                             QMessageBox, QFileDialog, QCheckBox, QSpinBox,
                             QComboBox)
import os
import errno
import krita


class MyUIExportLayers(object):

    def __init__(self):
        self.mainDialog = myexportlayersdialog.MyExportLayersDialog()
        self.mainLayout = QVBoxLayout(self.mainDialog)
        self.formLayout = QFormLayout()
        self.documentLayout = QVBoxLayout()
        self.directorySelectorLayout = QHBoxLayout()
        self.optionsLayout = QVBoxLayout()
        self.resolutionLayout = QHBoxLayout()

        self.refreshButton = QPushButton(i18n("Refresh"))
        self.widgetDocuments = QListWidget()
        self.directoryTextField = QLineEdit()
        self.directoryDialogButton = QPushButton(i18n("..."))
        self.exportFilterLayersCheckBox = QCheckBox(i18n("Export filter layers"))
        self.batchmodeCheckBox = QCheckBox(i18n("Export in batchmode"))
        self.ignoreInvisibleLayersCheckBox = QCheckBox(i18n("Ignore invisible layers"))
        self.xResSpinBox = QSpinBox()
        self.yResSpinBox = QSpinBox()
        self.formatsComboBox = QComboBox()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.kritaInstance = krita.Krita.instance()
        self.documentsList = []

        self.directoryTextField.setReadOnly(True)
        self.batchmodeCheckBox.setChecked(True)
        self.directoryDialogButton.clicked.connect(self._selectDir)
        self.widgetDocuments.currentRowChanged.connect(self._setResolution)
        self.refreshButton.clicked.connect(self.refreshButtonClicked)
        self.buttonBox.accepted.connect(self.confirmButton)
        self.buttonBox.rejected.connect(self.mainDialog.close)

        self.mainDialog.setWindowModality(Qt.NonModal)
        self.widgetDocuments.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def initialize(self):
        self.loadDocuments()

        #self.xResSpinBox.setRange(1, 10000)
        #self.yResSpinBox.setRange(1, 10000)

        self.formatsComboBox.addItem(i18n("JPEG"))
        self.formatsComboBox.addItem(i18n("PNG"))

        self.documentLayout.addWidget(self.widgetDocuments)
        self.documentLayout.addWidget(self.refreshButton)

        #self.directorySelectorLayout.addWidget(self.directoryTextField)
        #self.directorySelectorLayout.addWidget(self.directoryDialogButton)

        #self.optionsLayout.addWidget(self.exportFilterLayersCheckBox)
        #self.optionsLayout.addWidget(self.batchmodeCheckBox)
        #self.optionsLayout.addWidget(self.ignoreInvisibleLayersCheckBox)

        #self.resolutionLayout.addWidget(self.xResSpinBox)
        #self.resolutionLayout.addWidget(self.yResSpinBox)

        self.formLayout.addRow(i18n("Documents:"), self.documentLayout)
        #self.formLayout.addRow(i18n("Initial directory:"), self.directorySelectorLayout)
        #self.formLayout.addRow(i18n("Export options:"), self.optionsLayout)
        #self.formLayout.addRow(i18n("Resolution:"), self.resolutionLayout)
        #self.formLayout.addRow(i18n("Images extensions:"), self.formatsComboBox)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.line)
        self.mainLayout.addWidget(self.buttonBox)

        self.mainDialog.resize(500, 300)
        self.mainDialog.setWindowTitle(i18n("Export Sprite"))
        self.mainDialog.setSizeGripEnabled(True)
        #self.mainDialog.show()
        #self.mainDialog.activateWindow()
        self.confirmButton()

    def loadDocuments(self):
        self.widgetDocuments.clear()

        self.documentsList = [document for document in self.kritaInstance.documents() if document.fileName()]

        for document in self.documentsList:
            self.widgetDocuments.addItem(document.fileName())

    def refreshButtonClicked(self):
        self.loadDocuments()

    def confirmButton(self):
        selectedPaths = [item.text() for item in self.widgetDocuments.selectedItems()]
        selectedDocuments = self.kritaInstance.activeDocument()
        
        self.msgBox = QMessageBox(self.mainDialog)
        if not selectedDocuments:
            self.msgBox.setText(i18n("No active document."))
        else:
            self.export(selectedDocuments)
            #self.msgBox.setText(i18n("Done."))
        #self.msgBox.exec_()

    def mkdir(self, directory):
        target_directory = self.directoryTextField.text() + directory
        if os.path.exists(target_directory) and os.path.isdir(target_directory):
            return

        try:
            os.makedirs(target_directory)
        except OSError as e:
            raise e

    def export(self, document):
        Application.setBatchmode(True)

        d = Krita.instance().createDocument(document.width(), document.height(), "Python test document", document.colorModel(), document.colorDepth(), document.colorProfile(), document.resolution())
        Krita.instance().activeWindow().addView(d)


        self.spriteWidth = document.width()
        self.spriteCount = 0
        self._cloneNode(document.rootNode(), d.rootNode(), d)
        d.setWidth(self.spriteWidth * self.spriteCount)

    def _cloneNode(self, parentNode, targetParentNode, document):
        for node in parentNode.childNodes():
            n = document.createNode(node.name(),node.type())
            n.setPixelData(node.pixelData(0,0,800,800),0,0,800,800)
            targetParentNode.addChildNode(n,None)
            n.move(self.spriteWidth * self.spriteCount, 0)
            self.spriteCount = self.spriteCount + 1
            
            if node.childNodes():
                self._cloneNode(node,n,document)

        
    def _exportLayers(self, parentNode, fileFormat, parentDir, document):
        """ This method get all sub-nodes from the current node and export then in
            the defined format."""

        for node in parentNode.childNodes():
            newDir = ''
            if node.type() == 'grouplayer':
                newDir = os.path.join(parentDir, node.name())
                self.mkdir(newDir)
                node.setVisible(True)
            elif not self.exportFilterLayersCheckBox.isChecked() and 'filter' in node.type():
                continue
            elif self.ignoreInvisibleLayersCheckBox.isChecked() and not node.visible():
                continue
            else:
                nodeName = node.name()
                _fileFormat = self.formatsComboBox.currentText()
                if '[jpeg]' in nodeName:
                    _fileFormat = 'jpeg'
                elif '[png]' in nodeName:
                    _fileFormat = 'png'

                layerFileName = '{0}{1}/{2}.{3}'.format(self.directoryTextField.text(),
                                                        parentDir, node.name(), _fileFormat)
                #node.save(layerFileName, self.xResSpinBox.value(), self.yResSpinBox.value())
                node.setVisible(True)
                document.refreshProjection()
                document.exportImage(layerFileName, krita.InfoObject())
                node.setVisible(False)
                

            if node.childNodes():
                self._exportLayers(node, fileFormat, newDir, document)

    def _selectDir(self):
        directory = QFileDialog.getExistingDirectory(self.mainDialog, i18n("Select a Folder"), os.path.expanduser("~"), QFileDialog.ShowDirsOnly)
        self.directoryTextField.setText(directory)

    def _setResolution(self, index):
        document = self.documentsList[index]
        self.xResSpinBox.setValue(document.width())
        self.yResSpinBox.setValue(document.height())
