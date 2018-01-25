from PyQt5.QtGui import QFont
from cadnano.views.styles import THE_FONT, THE_FONT_SIZE
from cadnano.views.styles import BLUE_FILL, BLUE_STROKE
from cadnano.views.styles import GRAY_FILL, GRAY_STROKE


# Grid Sizing
GRID_HELIX_RADIUS = 15.
GRID_HELIX_STROKE_WIDTH = 0.5
GRID_HELIX_MOD_HILIGHT_WIDTH = 1

# Z values
# bottom
ZGRIDHELIX = 40
ZSELECTION = 50
ZDESELECTOR = 60
ZWEDGEGIZMO = 100
ZPXIGROUP = 150
ZPARTITEM = 200
# top

# Part apperance
GRID_FILL = "#ffffff"

DEFAULT_PEN_WIDTH = 1
DEFAULT_ALPHA = 2
SELECTED_COLOR = '#5a8bff'
SELECTED_PEN_WIDTH = 2
SELECTED_ALPHA = 0


GRID_NUM_FONT = QFont(THE_FONT, 10, QFont.Bold)
USE_TEXT_COLOR = "#ffffff"
GRID_TEXT_COLOR = "#000000"

ACTIVE_STROKE = '#cccc00'
DEFAULT_GRID_DOT_COLOR = '#0000ff'
ACTIVE_GRID_DOT_COLOR = '#ff3333'  # item color

VHI_HINT_ACTIVE_STROKE = BLUE_STROKE
VHI_HINT_INACTIVE_STROKE = '#cccccc'
