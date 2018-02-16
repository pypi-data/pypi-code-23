import wx

from ..wallet import Wallet

DEFAULT_COLUMN_WIDTH = 100


class ReceiveTab(wx.Panel):  # type: ignore
    def __init__(self,
                 parent: wx.Window,
                 wallet: Wallet) -> None:
        super().__init__(parent)
        self.wallet = wallet
        self.init_popup_menu()
        self.create_receive_tab()

    def create_receive_tab(self) -> None:
        receive_text = wx.StaticText(self, label='Receive Addresses: ')

        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.list_ctrl.InsertColumn(0, 'Addresses')

        if self.wallet.addresses:
            for address in self.wallet.addresses:
                self.list_ctrl.Append([str(address)])
            column_width = wx.LIST_AUTOSIZE
        else:
            column_width = DEFAULT_COLUMN_WIDTH

        self.list_ctrl.SetColumnWidth(0, column_width)

        new_address_button = wx.Button(self, label='Generate New Address')

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(receive_text, flag=wx.CENTER)
        vbox.Add(self.list_ctrl, proportion=20, flag=wx.EXPAND)
        vbox.Add(new_address_button, proportion=2, flag=wx.CENTER)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(vbox, proportion=1, flag=(wx.EXPAND | wx.ALL), border=10)

        self.Bind(wx.EVT_BUTTON, self.new_address_button_clicked, new_address_button)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.address_right_click, self.list_ctrl)
        self.Bind(wx.EVT_MENU, self.popup_menu_clicked)

        self.SetSizer(hbox)

    def init_popup_menu(self) -> None:
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(0, 'Copy Address')

    def popup_menu_clicked(self,
                           event: wx.ContextMenuEvent) -> None:
        index = event.GetId()
        if index == 0:
            # Copy
            selected = self.list_ctrl.GetFirstSelected()
            address = self.list_ctrl.GetItemText(selected)
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(text=address))
            wx.TheClipboard.Close()

    def new_address_button_clicked(self,
                                   event: wx.CommandEvent) -> None:
        new_address = self.wallet.create_new_address()
        self.list_ctrl.Append([new_address])

    def address_right_click(self,
                            event: wx.ListEvent) -> None:
        address = event.GetText()
        if address:
            self.PopupMenu(self.popup_menu)
