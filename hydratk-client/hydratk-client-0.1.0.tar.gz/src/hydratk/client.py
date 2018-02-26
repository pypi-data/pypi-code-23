# -*- coding: utf-8 -*-
"""Main HydraTK client module

.. module:: client
   :platform: Windows, Unix
   :synopsis: Main HydraTK client module
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from hydratk.extensions.client.core.gui import Gui

def main():
    """Main method
    
    Args:
        none

    Returns:
        void

    """

    htk = Gui.get_instance()
    htk.mainloop()

if __name__ == '__main__':
    main()
