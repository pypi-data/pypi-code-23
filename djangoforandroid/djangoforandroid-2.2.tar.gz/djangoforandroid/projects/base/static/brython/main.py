from mdc import MDC
import framework as fm

MDC.TemporaryDrawer(".mdc-temporary-drawer").open()
fm.bind(".mdc-toolbar .mdc-toolbar__menu-icon", 'click', MDC.TemporaryDrawer(".mdc-temporary-drawer").open)
