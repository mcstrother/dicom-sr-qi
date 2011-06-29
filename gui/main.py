import wx
from mirqi.core import my_utils
import datetime
import numbers

class Inquiry_Parameter_Panel(wx.Panel):

    def __init__(self, *args, **kwargs):
        param = kwargs['parameter']
        del kwargs['parameter']
        parent = args[0]
        wx.Panel.__init__(self,parent, **kwargs)
        # add stuff
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, -1, param.label))
        if isinstance(param, datetime.date):
            pass #make a datepickerctrl
        elif isinstance(param.value, int) or isinstance(param.value, long):
            ctrl = wx.SpinCtrl(self)
            ctrl.SetValue(param.value)
            sizer.Add(ctrl)
        self.SetSizer(sizer)
            
        
        

class Inquiry_Panel(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs):
        inquiry_class = kwargs['inquiry_class']
        del kwargs['inquiry_class']
        kwargs['label'] = inquiry_class.get_name()
        wx.CollapsiblePane.__init__(self,*args, **kwargs)
        # add stuff
        sizer = wx.BoxSizer(wx.VERTICAL)
        parameters = inquiry_class.get_parameters()
        for param in parameters:
            sizer.Add(Inquiry_Parameter_Panel(self.GetPane(), parameter=param),0)
        self.GetPane().SetSizer(sizer) # see http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.CollapsiblePane.html for why GetPane is used here
        
        

class Inquiry_Selection_Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        for inq in my_utils.get_inquiry_classes():
            inq_panel = Inquiry_Panel(self, inquiry_class=inq)
            sizer.Add(inq_panel,1,wx.ALIGN_LEFT)
        self.SetSizer(sizer)

import os        
class Data_File_List(wx.CheckListBox):
    def __init__(self, *args, **kwargs):
        wx.CheckListBox.__init__(self, *args, **kwargs)

    def add_file(self, file_paths):
        for path in file_paths:
            file_path = os.path.abspath(path)
            file_name = os.path.basename(file_path)
            self.Insert(file_path, self.GetCount())
            #self.AppendAndEnsureVisible(file_name)
            

class Data_Panel(wx.Panel):

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        add_source_button = wx.Button(self,-1, 'Add data source')
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
        


class Main_Frame(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        main_panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(Data_Panel(main_panel, style=wx.RAISED_BORDER),1,wx.ALIGN_LEFT|wx.EXPAND)
        sizer.Add(Inquiry_Selection_Panel(main_panel, style=wx.RAISED_BORDER),2,wx.ALIGN_LEFT|wx.EXPAND)
        main_panel.SetSizer(sizer)


class MirqiApp(wx.App):
    def OnInit(self):
        frame = Main_Frame(None, title = "MIR Quality Improvement")
        frame.Show(True)
        frame.Centre()
        return True

def main():
    app = MirqiApp(0)
    app.MainLoop()

if __name__ == "__main__":
    main()
    



