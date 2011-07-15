import os
import wx

class Data_File_List(wx.CheckListBox):
    def __init__(self, *args, **kwargs):
        wx.CheckListBox.__init__(self, *args, **kwargs)

    def add_file(self, file_paths):
        for path in file_paths:
            file_path = os.path.abspath(path)
            file_name = os.path.basename(file_path)
            self.Insert(file_path, self.GetCount())
            #self.AppendAndEnsureVisible(file_name)

    def get_file_names(self):
        """Return full file paths that have been selected
        """
        return self.GetCheckedStrings()

class Data_Panel(wx.Panel):

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        add_source_button = wx.Button(self,0, 'Add data source')
        self.Bind(wx.EVT_BUTTON, self.select_file,add_source_button)
        sizer.Add(add_source_button,0, flag=wx.ALIGN_BOTTOM)
        self.data_file_list = Data_File_List(self)
        sizer.Add(self.data_file_list,flag=wx.EXPAND)
        self.SetSizer(sizer)
        self.file_dialog = wx.FileDialog(self,style=wx.FD_CHANGE_DIR|wx.FD_MULTIPLE)

    def select_file(self, event):
        #consider using FilePickerCtrl http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.FilePickerCtrl.html
        if self.file_dialog.ShowModal() == wx.ID_OK:
            self.data_file_list.add_file(self.file_dialog.GetPaths())
        
    def get_file_names(self):
        """Return full file paths that have been selected
        """
        return self.data_file_list.get_file_names()

