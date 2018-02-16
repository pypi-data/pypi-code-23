import wx

from ..wallet import Wallet


class OverviewTab(wx.Panel):  # type: ignore
    def __init__(self,
                 parent: wx.Window,
                 wallet: Wallet) -> None:
        super().__init__(parent)
        self.wallet = wallet
        self.create_overview_tab()

    def create_overview_tab(self) -> None:
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        balance_text = wx.StaticText(self, label=f'Balance: {self.wallet.balance}')
        hbox.Add(balance_text, flag=wx.ALL)
        self.SetSizer(hbox)
