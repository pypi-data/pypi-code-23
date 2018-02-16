import wx

from .worker import WorkerThread
from ..wallet import Wallet

CONFIRMED = 'Confirmed'
PENDING = 'Pending'
RETRYING = 'Retrying'


class HistoryTab(wx.Panel):  # type: ignore
    def __init__(self,
                 parent: wx.Window,
                 wallet: Wallet) -> None:
        super().__init__(parent)
        self.wallet = wallet
        self.worker = WorkerThread()
        self.init_popup_menu()
        self.create_history_tab()

    def create_history_tab(self) -> None:
        self.transactions = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.transactions.InsertColumn(0, 'Transactions')
        self.transactions.InsertColumn(1, 'Status')

        for bundle in self.wallet.bundles['unconfirmed']:
            self.transactions.Append([str(bundle.hash), PENDING])
        for bundle in self.wallet.bundles['confirmed']:
            self.transactions.Append([str(bundle.hash), CONFIRMED])

        self.transactions.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.transactions.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.transactions, proportion=1, flag=wx.EXPAND)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(vbox, proportion=1, flag=(wx.EXPAND | wx.ALL), border=10)

        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.transactions_right_click, self.transactions)
        self.Bind(wx.EVT_MENU, self.popup_menu_clicked)

        self.SetSizer(hbox)

    def init_popup_menu(self) -> None:
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(0, 'Retry Bundle')

    def popup_menu_clicked(self,
                           event: wx.ContextMenuEvent) -> None:
        index = event.GetId()
        if index == 0:
            # Retry Bundle
            bundle_hashes = []
            list_index = self.transactions.GetFirstSelected()
            while list_index != -1:
                if self.transactions.GetItemText(list_index, col=1) == PENDING:
                    bundle_hashes.append(self.transactions.GetItemText(list_index))
                    list_index = self.transactions.GetNextSelected(list_index)

            print(bundle_hashes)
            bundles = []
            for bundle in self.wallet.bundles['unconfirmed']:
                if bundle.hash in bundle_hashes:
                    bundles.append(bundle)

            self.worker.send(self.wallet.retry_unconfirmed_bundles, args=tuple(bundles))

    def transactions_right_click(self,
                                 event: wx.ListEvent) -> None:
        if event.GetText():
            self.PopupMenu(self.popup_menu)
