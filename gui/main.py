import wx
from mirqi.core import my_utils
import datetime
import numbers

class Inquiry_Panel(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs):
        inquiry_class = kwargs['inquiry_class']
        del kwargs['inquiry_class']
        kwargs['label'] = inquiry_class.get_name()
        wx.CollapsiblePane.__init__(self,*args, **kwargs)
        # add stuff
        parameters = inquiry_class.get_parameters()
        ctrls = self._get_parameter_controls(parameters)
        sizer = wx.BoxSizer(wx.VERTICAL)
        for ctrl in ctrls:
            sizer.Add(ctrl)
        self.GetPane().SetSizer(sizer)
        

    def _get_parameter_controls(self, parameters):
        ctrls = []
        parent = self.GetPane() # see http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.CollapsiblePane.html
        for parameter in parameters:
            if isinstance(parameter,datetime.date):
                pass #make a datepickerctrl
            elif isinstance(parameter, numbers.Integral):
                ctrl = wx.SpinCtrl(parent)
                ctrl.SetValue(parameter)
                ctrls.append(ctrl)
        return ctrls
            
        

class Inquiry_Selection_Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        for inq in my_utils.get_inquiry_classes(): 
            sizer.Add(Inquiry_Panel(self, inquiry_class=inq),0,wx.ALIGN_LEFT)
        self.SetSizer(sizer)
        

class Data_Panel(wx.Panel):

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        add_source_button = wx.Button(self,-1, 'Add data source')
        self.Bind(wx.EVT_BUTTON, self.get_file)
        sizer.Add(add_source_button,1, flag=wx.ALIGN_LEFT)

    def get_file(self, event):
        #consider using FilePickerCtrl http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.FilePickerCtrl.html
        return wx.FileSelector()


class Main_Frame(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(Data_Panel(self, style=wx.RAISED_BORDER),1,wx.ALIGN_CENTER)
        sizer.Add(Inquiry_Selection_Panel(self, style=wx.RAISED_BORDER),2,wx.ALIGN_CENTER)
        self.SetSizer(sizer)


class MirqiApp(wx.App):
    def OnInit(self):
        frame = Main_Frame(None)
        frame.Show(True)
        frame.Centre()
        return True

def main():
    app = MirqiApp(0)
    app.MainLoop()

if __name__ == "__main__":
    main()
    



