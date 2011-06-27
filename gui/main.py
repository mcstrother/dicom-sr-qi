import wx

class Data_Panel(wx.Panel):

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        add_source_button = wx.Button(self,-1, 'Add data source')
        self.Bind(wx.EVT_BUTTON, self.get_file)
        sizer.Add(add_source_button,1)

    def get_file(self, event):
        return wx.FileSelector()


class Main_Frame(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(Data_Panel(self, style=wx.RAISED_BORDER),1,wx.ALIGN_CENTER)
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
    



