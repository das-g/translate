#!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module is working on the main windows of Editor

import os
import sys
from PyQt4 import QtCore, QtGui
from ui.Ui_MainEditor import Ui_MainWindow
from modules.TUview import TUview
from modules.Overview import OverviewDock
from modules.Comment import CommentDock
from modules.Header import Header
from modules.Operator import Operator
from modules.FileAction import FileAction
from modules.Find import Find
from modules.Preference import Preference
from modules.AboutEditor import AboutEditor
import modules.World as World

class MainWindow(QtGui.QMainWindow):
    """
    The main window which holds the toolviews.
    """
    windowList = []

    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.recentaction = []
        self.setWindowTitle(World.settingOrg + ' ' + World.settingApp + ' ' + World.settingVer)
        self.createRecentAction()
        
        app = QtGui.QApplication.instance()
        self.connect(app, QtCore.SIGNAL("focusChanged(QWidget *,QWidget *)"), self.focusChanged)    
        
        # get the last geometry
        geometry = World.settings.value("lastGeometry")
        if (geometry.isValid()):
            self.setGeometry(geometry.toRect())

        sepAction = self.ui.menuWindow.actions()[0]
        #plug in overview widget
        self.dockOverview = OverviewDock(self)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dockOverview)
        self.ui.menuWindow.insertAction(sepAction, self.dockOverview.toggleViewAction())
        
        #plug in TUview widget
        self.dockTUview = TUview(self)
        self.setCentralWidget(self.dockTUview)
        self.ui.menuWindow.insertAction(sepAction, self.dockTUview.toggleViewAction())
        
        #plug in comment widget
        self.dockComment = CommentDock(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockComment)
        self.ui.menuWindow.insertAction(sepAction, self.dockComment.toggleViewAction())
         
        #add widgets to statusbar
        self.statuslabel = QtGui.QLabel()
        self.statuslabel.setFrameStyle(QtGui.QFrame.NoFrame)
        self.statuslabel.setMargin(1)
        self.ui.statusbar.addWidget(self.statuslabel)
        self.ui.statusbar.setWhatsThis("<h3>Status Bar</h3>Shows the progress of the translation in the file and messages about the current state of the application.")

        #add action from each toolbar toggleviewaction to toolbars submenu of view menu
        self.ui.menuToolbars.addAction(self.ui.toolStandard.toggleViewAction())
        self.ui.menuToolbars.addAction(self.ui.toolNavigation.toggleViewAction())
        self.ui.menuToolbars.addAction(self.ui.toolFilter.toggleViewAction())

        #create operator
        self.operator = Operator()
        
        #Help menu of aboutQt
        self.ui.menuHelp.addSeparator()
        action = QtGui.QWhatsThis.createAction(self)
        self.ui.menuHelp.addAction(action)
        self.aboutDialog = AboutEditor(self)
        self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"), self.aboutDialog.showDialog)
        self.connect(self.ui.actionAboutQT, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("aboutQt()"))
        
        # create file action object and file action menu related signals
        self.fileaction = FileAction(self)
        self.connect(self.ui.actionOpen, QtCore.SIGNAL("triggered()"), self.fileaction.openFile)
        self.connect(self.ui.actionOpenInNewWindow, QtCore.SIGNAL("triggered()"), self.startInNewWindow)
        self.connect(self.ui.actionSave, QtCore.SIGNAL("triggered()"), self.fileaction.save)
        self.connect(self.ui.actionSaveas, QtCore.SIGNAL("triggered()"), self.fileaction.saveAs)
        self.connect(self.ui.actionExit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("close()"))
        
        # create Find widget and connect signals related to it
        self.findBar = Find(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.findBar)
        self.connect(self.ui.actionFind, QtCore.SIGNAL("triggered()"), self.findBar.showFind)
        self.connect(self.ui.actionReplace, QtCore.SIGNAL("triggered()"), self.findBar.showReplace)
        self.connect(self.findBar, QtCore.SIGNAL("initSearch"), self.operator.initSearch)
        self.connect(self.findBar, QtCore.SIGNAL("searchNext"), self.operator.searchNext)
        self.connect(self.findBar, QtCore.SIGNAL("searchPrevious"), self.operator.searchPrevious)
        
        self.connect(self.findBar, QtCore.SIGNAL("replace"), self.operator.replace)
        self.connect(self.findBar, QtCore.SIGNAL("replaceAll"), self.operator.replaceAll)
        
        # "searchFound" sends container and location to be highlighted.
        self.connect(self.operator, QtCore.SIGNAL("searchResult"), self.dockTUview.highlightSearch)
        self.connect(self.operator, QtCore.SIGNAL("searchResult"), self.dockComment.highlightSearch)
        self.connect(self.operator, QtCore.SIGNAL("generalInfo"), self.showTemporaryMessage)
        # "replaceText" sends text field, start, length, and text to replace.
        self.connect(self.operator, QtCore.SIGNAL("replaceText"), self.dockTUview.replaceText)
        self.connect(self.operator, QtCore.SIGNAL("replaceText"), self.dockComment.replaceText)
        
        # Edit menu action
        self.connect(self.ui.actionComment, QtCore.SIGNAL("triggered()"), self.dockComment.show)
       
        # action Preferences menu 
        self.preference = Preference(self)
        self.connect(self.ui.actionPreferences, QtCore.SIGNAL("triggered()"), self.preference.showDialog)
        self.connect(self.preference, QtCore.SIGNAL("settingsChanged"), self.dockComment.applySettings)
        self.connect(self.preference, QtCore.SIGNAL("settingsChanged"), self.dockOverview.applySettings)
        self.connect(self.preference, QtCore.SIGNAL("settingsChanged"), self.dockTUview.applySettings)

        # Edit Header
        self.headerDialog = Header(self, self.operator)
        self.connect(self.ui.actionEdit_Header, QtCore.SIGNAL("triggered()"), self.headerDialog.showDialog)

        # Other actions
        self.connect(self.ui.actionFirst, QtCore.SIGNAL("triggered()"), self.dockOverview.scrollFirst)
        self.connect(self.ui.actionPrevious, QtCore.SIGNAL("triggered()"), self.dockOverview.scrollPrevious)
        self.connect(self.ui.actionNext, QtCore.SIGNAL("triggered()"), self.dockOverview.scrollNext)
        self.connect(self.ui.actionLast, QtCore.SIGNAL("triggered()"), self.dockOverview.scrollLast)
        self.connect(self.ui.actionCopySource2Target, QtCore.SIGNAL("triggered()"), self.dockTUview.source2target)

        # action filter menu
        self.connect(self.ui.actionFilterFuzzy, QtCore.SIGNAL("toggled(bool)"), self.operator.filterFuzzy)
        self.connect(self.ui.actionFilterTranslated, QtCore.SIGNAL("toggled(bool)"), self.operator.filterTranslated)
        self.connect(self.ui.actionFilterUntranslated, QtCore.SIGNAL("toggled(bool)"), self.operator.filterUntranslated)
        self.connect(self.ui.actionToggleFuzzy, QtCore.SIGNAL("triggered()"), self.operator.toggleFuzzy)

        # add open recent to the toolbar
        action = self.ui.menuOpen_Recent.menuAction()
        action.setToolTip(self.tr("Open"))
        self.connect(action, QtCore.SIGNAL("triggered()"), self.fileaction.openFile)

        self.ui.toolStandard.insertAction(self.ui.actionSave, action)

        # "currentUnit" sends currentUnit, currentIndex
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockOverview.updateView)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockTUview.updateView)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockComment.updateView)
        self.connect(self.dockTUview, QtCore.SIGNAL("filteredIndex"), self.operator.indexToUnit)
        self.connect(self.dockOverview, QtCore.SIGNAL("currentIndex"), self.operator.setCurrentUnit)

        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockTUview.checkModified)
        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockComment.checkModified)
        self.connect(self.dockOverview, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.dockOverview, QtCore.SIGNAL("targetChanged"), self.dockTUview.setTarget)

        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.dockOverview.updateTarget)
        self.connect(self.dockComment, QtCore.SIGNAL("commentChanged"), self.operator.setComment)
        self.connect(self.dockComment, QtCore.SIGNAL("commentChanged"), self.dockOverview.updateComment)
        self.connect(self.fileaction, QtCore.SIGNAL("fileSaved"), self.operator.saveStoreToFile)
        self.connect(self.operator, QtCore.SIGNAL("savedAlready"), self.ui.actionSave.setEnabled)
        self.connect(self.dockTUview, QtCore.SIGNAL("readyForSave"), self.ui.actionSave.setEnabled)
        self.connect(self.dockComment, QtCore.SIGNAL("readyForSave"), self.ui.actionSave.setEnabled)
        self.connect(self.headerDialog, QtCore.SIGNAL("readyForSave"), self.ui.actionSave.setEnabled)

        self.connect(self.fileaction, QtCore.SIGNAL("fileSaved"), self.setTitle)
        self.connect(self.dockOverview, QtCore.SIGNAL("toggleFirstLastUnit"), self.toggleFirstLastUnit)

        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockOverview.slotNewUnits)
        # "filterChanged" sends filter and number of filtered items.
        self.connect(self.operator, QtCore.SIGNAL("filterChanged"), self.dockOverview.filterChanged)
        self.connect(self.operator, QtCore.SIGNAL("filterChanged"), self.dockTUview.filterChanged)
##        self.connect(self.operator, QtCore.SIGNAL("filteredList"), self.dockOverview.filteredList)
##        self.connect(self.operator, QtCore.SIGNAL("filteredList"), self.dockTUview.filteredList)

        # set file status information to text label of status bar.
        self.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.statuslabel.setText)
        self.connect(self.fileaction, QtCore.SIGNAL("fileOpened"), self.setOpening)
        self.connect(self.fileaction, QtCore.SIGNAL("fileOpened"), self.operator.getUnits)
        
        # get the last state of mainwindows's toolbars and dockwidgets
        state = World.settings.value("MainWindowState")
        # check if the last state is valid it will restore
        if (state.isValid()):
            self.restoreState(state.toByteArray(), 1)
        
        tuViewHidden = World.settings.value("TuViewHidden", QtCore.QVariant(False))
        self.dockTUview.setHidden(tuViewHidden.toBool())
        self.findBar.setHidden(True)
        
    def enableCopyCut(self, bool):
        self.ui.actionCopy.setEnabled(bool)
        self.ui.actionCut.setEnabled(bool)        

    def enableUndo(self, bool):
        self.ui.actionUndo.setEnabled(bool)

    def enableRedo(self, bool):
        self.ui.actionRedo.setEnabled(bool)   

    def setOpening(self, fileName): 
        """
        set status after open a file
        @param fileName string, the filename to open
        """

        self.setTitle(fileName)
        self.ui.actionSave.setEnabled(False)  
        self.ui.actionSaveas.setEnabled(True)
        self.ui.actionPaste.setEnabled(True)
        self.ui.actionSelectAll.setEnabled(True)
        self.ui.actionFind.setEnabled(True)
        self.ui.actionReplace.setEnabled(True)
        self.ui.actionCopySource2Target.setEnabled(True)
        self.ui.actionEdit_Header.setEnabled(True)
        files = World.settings.value("recentFileList").toStringList()
        files.removeAll(fileName)
        files.prepend(fileName)
        while files.count() > World.MaxRecentFiles:
            files.removeAt(files.count() - 1)
        World.settings.setValue("recentFileList", QtCore.QVariant(files))
        self.updateRecentAction() 

        self.ui.actionToggleFuzzy.setEnabled(True)
        self.ui.actionFilterFuzzy.setEnabled(True)
        self.ui.actionFilterTranslated.setEnabled(True)
        self.ui.actionFilterUntranslated.setEnabled(True)
        self.ui.actionFilterFuzzy.setChecked(True)
        self.ui.actionFilterTranslated.setChecked(True)
        self.ui.actionFilterUntranslated.setChecked(True)
        
    def startRecentAction(self):
        action = self.sender()
        if action:
            self.fileaction.setFileName(action.data().toString())

    def createRecentAction(self):
        for i in range(World.MaxRecentFiles):
            self.ui.recentaction.append(QtGui.QAction(self))
            self.ui.recentaction[i].setVisible(False)
            self.connect(self.ui.recentaction[i], QtCore.SIGNAL("triggered()"), self.startRecentAction)
            self.ui.menuOpen_Recent.addAction(self.ui.recentaction[i])
        self.updateRecentAction()

    def updateRecentAction(self):
        """
        Update recent actions of Open Recent Files with names of recent opened files
        """
        files = World.settings.value("recentFileList").toStringList()
        numRecentFiles = min(files.count(), World.MaxRecentFiles)
        for i in range(numRecentFiles):
            self.ui.recentaction[i].setText(files[i])
            self.ui.recentaction[i].setData(QtCore.QVariant(files[i]))
            self.ui.recentaction[i].setVisible(True)

        for j in range(numRecentFiles, World.MaxRecentFiles):
            self.ui.recentaction[j].setVisible(False)

    def closeEvent(self, event):
        """
        @param QCloseEvent Object: received close event when closing mainwindows
        """
        QtGui.QMainWindow.closeEvent(self, event)
        if self.operator.modified():
            if self.fileaction.aboutToClose(self):
                event.accept()
            else:
                event.ignore()
                
        # remember last geometry
        World.settings.setValue("lastGeometry", QtCore.QVariant(self.geometry()))
        
        # remember last state
        state = self.saveState(1)
        World.settings.setValue("MainWindowState", QtCore.QVariant(state))
        World.settings.setValue("TuViewHidden", QtCore.QVariant(self.dockTUview.isHidden()))
        
    def setTitle(self, title):
        """set the title of program.
        @param title: title string."""
        shownName = QtCore.QFileInfo(title).fileName()
        self.setWindowTitle(self.tr("%1[*] - %2").arg(shownName).arg(World.settingApp))

    def toggleFirstLastUnit(self, atFirst, atLast):
        """set enable/disable first, previous, next, and last unit buttons
        @param atFirst: bool indicates that the unit is at first place
        @param atLast: bool indicates that the unit is at last place
        """
        self.ui.actionFirst.setDisabled(atFirst)
        self.ui.actionPrevious.setDisabled(atFirst)
        self.ui.actionNext.setDisabled(atLast)
        self.ui.actionLast.setDisabled(atLast)
    
    def startInNewWindow(self):
        other = MainWindow()
        MainWindow.windowList.append(other)
        if other.fileaction.openFile():
            other.show()
        
    def showTemporaryMessage(self, text):
        self.ui.statusbar.showMessage(text, 3000)
        
    def focusChanged(self, oldWidget, newWidget):
        if (oldWidget):
            self.disconnect(oldWidget, QtCore.SIGNAL("copyAvailable(bool)"), self.enableCopyCut)
            self.disconnect(oldWidget, QtCore.SIGNAL("undoAvailable(bool)"), self.enableUndo)
            self.disconnect(oldWidget, QtCore.SIGNAL("redoAvailable(bool)"), self.enableRedo)
            # cut, copy and paste in oldWidget
            if (callable(getattr(oldWidget, "cut", None))):
                self.disconnect(self.ui.actionCut, QtCore.SIGNAL("triggered()"), oldWidget, QtCore.SLOT("cut()"))

            if (callable(getattr(oldWidget, "copy", None))):
                self.disconnect(self.ui.actionCopy, QtCore.SIGNAL("triggered()"), oldWidget, QtCore.SLOT("copy()"))

            if (callable(getattr(oldWidget, "paste", None))):
                self.disconnect(self.ui.actionPaste, QtCore.SIGNAL("triggered()"), oldWidget, QtCore.SLOT("paste()"))            
            # undo, redo and selectAll in oldWidget
            if (callable(getattr(oldWidget, "document", None))):
                self.disconnect(self.ui.actionUndo, QtCore.SIGNAL("triggered()"), oldWidget.document(), QtCore.SLOT("undo()"))
                self.disconnect(self.ui.actionRedo, QtCore.SIGNAL("triggered()"), oldWidget.document(), QtCore.SLOT("redo()"))

            if (callable(getattr(oldWidget, "selectAll", None))):
                self.disconnect(self.ui.actionSelectAll , QtCore.SIGNAL("triggered()"), oldWidget, QtCore.SLOT("selectAll()"))
        if (newWidget):
            self.connect(newWidget, QtCore.SIGNAL("copyAvailable(bool)"), self.enableCopyCut)
            self.connect(newWidget, QtCore.SIGNAL("undoAvailable(bool)"), self.enableUndo)
            self.connect(newWidget, QtCore.SIGNAL("redoAvailable(bool)"), self.enableRedo)
            # cut, copy and paste in newWidget
            if (callable(getattr(newWidget, "cut", None))):
                self.connect(self.ui.actionCut, QtCore.SIGNAL("triggered()"), newWidget, QtCore.SLOT("cut()"))

            if (callable(getattr(newWidget, "copy", None))):
                self.connect(self.ui.actionCopy, QtCore.SIGNAL("triggered()"), newWidget, QtCore.SLOT("copy()"))

            if (callable(getattr(newWidget, "paste", None))):
                self.connect(self.ui.actionPaste, QtCore.SIGNAL("triggered()"), newWidget, QtCore.SLOT("paste()"))
                if (callable(getattr(newWidget, "isReadOnly", None))):
                    self.ui.actionPaste.setEnabled(not newWidget.isReadOnly())
                else:
                    self.ui.actionPaste.setEnabled(True)
            else:
                self.ui.actionPaste.setEnabled(False)
            # Select All
            if (callable(getattr(newWidget, "selectAll", None))):
                self.connect(self.ui.actionSelectAll , QtCore.SIGNAL("triggered()"), newWidget, QtCore.SLOT("selectAll()"))

            if (callable(getattr(newWidget, "textCursor", None))):
                hasSelection = newWidget.textCursor().hasSelection()
                self.enableCopyCut(hasSelection)
            else:
                self.enableCopyCut(False)

            #it will not work for QLineEdits
            if (callable(getattr(newWidget, "document", None))):
                undoAvailable = newWidget.document().isUndoAvailable()
                redoAvailable = newWidget.document().isRedoAvailable()
                self.enableUndo(undoAvailable)
                self.enableRedo(redoAvailable)
                self.connect(self.ui.actionUndo, QtCore.SIGNAL("triggered()"), newWidget.document(), QtCore.SLOT("undo()"))
                self.connect(self.ui.actionRedo, QtCore.SIGNAL("triggered()"), newWidget.document(), QtCore.SLOT("redo()"))
            else:
                self.enableUndo(False)
                self.enableRedo(False)

def main(inputFile = None):
    # set the path for QT in order to find the icons
    if __name__ == "__main__":
        QtCore.QDir.setCurrent(os.path.join(sys.path[0], "../ui"))
    else:
        QtCore.QDir.setCurrent(os.path.join(sys.path[0], "ui"))
    app = QtGui.QApplication(sys.argv)
    editor = MainWindow()
    editor.show()
    if (inputFile):
        if os.path.exists(inputFile):
            editor.fileaction.setFileName(inputFile)
        else:
            msg = editor.tr("%1 file name doesn't exist").arg(inputFile)
            QtGui.QMessageBox.warning(editor, editor.tr("File not found") , msg)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
