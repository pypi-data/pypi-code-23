import win32api, win32con, win32gui, win32ui
import time, sys
from threading import Thread

class TextWindow:
    global ref
    ref = []
    
    def __init__(self, text):
        self.text = text
        self.hInstance = None
        self.hWindow = None
        self.wndClassAtom = None
        t = Thread(target=self.Tmain)
        t.start()
        #self.Tmain()

    def delete(self):
        try:
            if self.hWindow != None:
                win32gui.PostMessage(self.hWindow, win32con.WM_DESTROY, 0, 0)
                time.sleep(0.1) # wait for window to close
                win32gui.UnregisterClass(self.wndClassAtom, self.hInstance)
                ref.remove(self)
                print("Deleted",self.text)
            else:
                print("No hWindow:",self.text)
            del self
        except:
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )

    def refCheck(self):
        self.deleteAll()
        ref.append(self)

    @staticmethod
    def deleteAll():
        if ref != []:
            for i in ref:
                i.delete()
        
    def Tmain(self):
        self.refCheck()
        
        self.hInstance = win32api.GetModuleHandle()
        className = 'MyWindowClassName'

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633576(v=vs.85).aspx
        # win32gui does not support WNDCLASSEX.
        wndClass                = win32gui.WNDCLASS()
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ff729176(v=vs.85).aspx
        wndClass.style          = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wndClass.lpfnWndProc    = self.wndProc
        wndClass.hInstance      = self.hInstance
        wndClass.hCursor        = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        wndClass.hbrBackground  = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        wndClass.lpszClassName  = className
        # win32gui does not support RegisterClassEx
        self.wndClassAtom = win32gui.RegisterClass(wndClass)

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
        # Consider using: WS_EX_COMPOSITED, WS_EX_LAYERED, WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW, WS_EX_TOPMOST, WS_EX_TRANSPARENT
        # The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
        exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632600(v=vs.85).aspx
        # Consider using: WS_DISABLED, WS_POPUP, WS_VISIBLE
        style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE
        
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632680(v=vs.85).aspx
        self.hWindow = win32gui.CreateWindowEx(
            exStyle,
            self.wndClassAtom,
            None, # WindowName
            style,
            0, # x
            0, # y
            win32api.GetSystemMetrics(win32con.SM_CXSCREEN), # width
            win32api.GetSystemMetrics(win32con.SM_CYSCREEN), # height
            None, # hWndParent
            None, # hMenu
            self.hInstance,
            None # lpParam
        )
        
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633540(v=vs.85).aspx
        win32gui.SetLayeredWindowAttributes(self.hWindow, 0x00ffffff, 255, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
        
        # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145167(v=vs.85).aspx
        #win32gui.UpdateWindow(hWindow)

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633545(v=vs.85).aspx
        win32gui.SetWindowPos(self.hWindow, win32con.HWND_TOPMOST, 0, 0, 0, 0,
            win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
        
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633548(v=vs.85).aspx
        #win32gui.ShowWindow(self.hWindow, win32con.SW_SHOW)

        win32gui.PumpMessages()
        #print("PumpMessages is off")

    def wndProc(self, hWnd, message, wParam, lParam):
        if message == win32con.WM_PAINT:
            hdc, paintStruct = win32gui.BeginPaint(hWnd)

            dpiScale = win32ui.GetDeviceCaps(hdc, win32con.LOGPIXELSX) / 60.0
            fontSize = 80

            # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145037(v=vs.85).aspx
            lf = win32gui.LOGFONT()
            lf.lfFaceName = "Times New Roman"
            lf.lfHeight = int(round(dpiScale * fontSize))
            #lf.lfWeight = 150
            # Use nonantialiased to remove the white edges around the text.
            # lf.lfQuality = win32con.NONANTIALIASED_QUALITY
            hf = win32gui.CreateFontIndirect(lf)
            win32gui.SelectObject(hdc, hf)

            rect = win32gui.GetClientRect(hWnd)
            # http://msdn.microsoft.com/en-us/library/windows/desktop/dd162498(v=vs.85).aspx
            win32gui.DrawText(
                hdc,
                self.text,
                -1,
                rect,
                win32con.DT_CENTER | win32con.DT_NOCLIP | win32con.DT_SINGLELINE | win32con.DT_VCENTER
            )
            win32gui.EndPaint(hWnd, paintStruct)
            return 0

        elif message == win32con.WM_DESTROY:
            print('Closing the window.')
            win32gui.PostQuitMessage(0)
            return 0

        else:
            return win32gui.DefWindowProc(hWnd, message, wParam, lParam)


def main():
    test = None
    text = "What"
    for i in range(10):
        test = TextWindow(str(10-i))
        #print(i)
        time.sleep(1)
        #test.delete()
    TextWindow.deleteAll()
    '''
    test = TextOnScreen("Poop")
    time.sleep(2)
    print("?")
    test.delete()
    #del test
    
    test2 = TextOnScreen("What?")
    time.sleep(1)
    test2.delete()
    '''

if __name__ == '__main__':
    main()
