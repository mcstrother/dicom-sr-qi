import wx
from mirqi.core import my_utils
from mirqi.gui import report_writer
import datetime
import numbers
import traceback

class Inquiry_Parameter_Panel(wx.Panel):

    def __init__(self, *args, **kwargs):
        self.param = kwargs['parameter']
        del kwargs['parameter']
        parent = args[0]
        wx.Panel.__init__(self,parent, **kwargs)
        # add stuff
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, -1, self.param.label))
        if isinstance(self.param, datetime.date):
            pass #make a datepickerctrl
        elif isinstance(self.param.value, int) or isinstance(self.param.value, long):
            self.ctrl = wx.SpinCtrl(self)
            self.ctrl.SetValue(self.param.value)
            sizer.Add(self.ctrl)
        self.SetSizer(sizer)
            
    def get_value(self):
        return self.ctrl.GetValue()
        

class Inquiry_Panel(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs):
        self._inquiry_class = kwargs['inquiry_class']
        del kwargs['inquiry_class']
        kwargs['label'] = self._inquiry_class.get_name()
        wx.CollapsiblePane.__init__(self,*args, **kwargs)
        # add stuff
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.enabled_box = wx.CheckBox(self.GetPane(),label = "Enabled")
        sizer.Add(self.enabled_box)
        # self.enabled_box.SetValue(True)
        param_names = self._inquiry_class.get_parameter_names()
        self.param_panels = {}
        for param_name in param_names:
            param = getattr(self._inquiry_class, param_name)
            param_panel = Inquiry_Parameter_Panel(self.GetPane(), parameter=param)
            self.param_panels[param_name] = param_panel
            sizer.Add(param_panel,0)
        self.GetPane().SetSizer(sizer) # see http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.CollapsiblePane.html for why GetPane is used here
        

    def is_enabled(self):
        return self.enabled_box.GetValue()

    def get_inquiry_class(self):
        for param_name in self._inquiry_class.get_parameter_names():
            new_value = self.param_panels[param_name].get_value()
            getattr(self._inquiry_class, param_name).value = new_value
        return self._inquiry_class
        

class Inquiry_Selection_Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.inq_panels = []
        for inq in my_utils.get_inquiry_classes():
            inq_panel = Inquiry_Panel(self, inquiry_class=inq)
            self.inq_panels.append(inq_panel)
            sizer.Add(inq_panel,1,wx.ALIGN_LEFT)
        self.SetSizer(sizer)

    def get_inquiry_classes(self):
        out = []
        for p in self.inq_panels:
            if p.is_enabled():
                out.append(p.get_inquiry_class())
        return out

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

    def get_file_names(self):
        """Return full file paths that have been selected
        """
        return self.GetCheckedStrings()

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
        
    def get_file_names(self):
        """Return full file paths that have been selected
        """
        return self.data_file_list.get_file_names()

class Main_Frame(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.main_panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.data_panel = Data_Panel(self.main_panel, style=wx.RAISED_BORDER)
        self.inq_selection_panel = Inquiry_Selection_Panel(self.main_panel, style=wx.RAISED_BORDER)
        sizer.Add(self.data_panel,1,wx.ALIGN_LEFT|wx.EXPAND)
        sizer.Add(self.inq_selection_panel,2,wx.ALIGN_LEFT|wx.EXPAND)
        run_button = wx.Button(self.main_panel, label = "Run")
        self.Bind(wx.EVT_BUTTON, self.run, run_button)
        sizer.Add(run_button,0,wx.ALIGN_CENTER)
        self.main_panel.SetSizer(sizer)

    def run(self, event):
        inq_classes = self.inq_selection_panel.get_inquiry_classes()
        prog_dlg = wx.ProgressDialog(title = "Running inquiries",
                                     message = "Processing data files",
                                     maximum = 5+len(inq_classes)+1,
                                     parent = self.main_panel,
                                     style = wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT|wx.PD_ELAPSED_TIME)
        procs = my_utils.get_procs_from_files(self.data_panel.get_file_names())
        if not prog_dlg.Update(5, "Running inquiry #1")[0]:
            return
        inq_objects = []
        for n,cls in enumerate(inq_classes):
            try:
                inq_object = cls(procs)
                inq_objects.append(cls(procs))
            except Exception as e:
                dlg = wx.MessageDialog(self.main_panel,
                                       message = "An error occured while running "\
                                       + inq_class.__name__\
                                       + "\n Error message is: \n" \
                                       + traceback.format_exc() +'\n'\
                                       + str(e),
                                       style=wx.CANCEL|wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destory()
            if not prog_dlg.Update(5+n, "Running inquiry #"+str(2+n)):
                break
        prog_dlg.Update(5+len(inq_classes), "Writing report")
        try:
            report_writer.write_report(inq_objects)
        except Exception as e:
            dlg = wx.MessageDialog(self.main_panel,
                                       message = "An error occured while attempting to write the report."\
                                       "\n Error message is: \n" +traceback.format_exc()\
                                       +'\n'+ str(e),
                                       style=wx.CANCEL|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
        prog_dlg.Update(5+len(inq_classes)+1, "Done")
        
            

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
    



