# tkpane.py
#
# PURPOSE
#   Simplify the construction of a Tkinter UI by encapsulating one or more
#   widgets into 'pane' objects that have no direct dependence on any other
#   UI elements.  Panes interact with other application elements through
#   methods and callback functions.
#
# AUTHORS
#   Dreas Nielsen (RDN)
#
# COPYRIGHT AND LICENSE
#   Copyright (c) 2018, R. Dreas Nielsen
#   This program is free software: you can redistribute it and/or modify it 
#   under the terms of the GNU General Public License as published by the Free 
#   Software Foundation, either version 3 of the License, or (at your option) 
#   any later version. This program is distributed in the hope that it will be 
#   useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
#   Public License for more details. The GNU General Public License is available 
#   at http://www.gnu.org/licenses/.
#
#===============================================================================

"""Encapsulate UI elements in a 'pane' object with uniform methods for enabling, 
disabling, and clearing the contained widgets; standard lists of callback methods 
that pass specific data to allow communication between panes, and callback methods
for reporting status and progress."""

__version__ = "0.8.1"


try:
    import Tkinter as tk
except:
    import tkinter as tk

import copy


#===============================================================================
#       Action method handlers
# Handler objects are to be used in the action method callbacks of the TkPane class.
#-------------------------------------------------------------------------------

class Handler(object):
    """Define a callback function that takes no arguments."""
    
    def __init__(self, function):
        self.function = function

    def call(self, tkpane_obj):
        # This method takes a TkPane object for consistency with other Handler
        # classes, although th TkPane object is not used.
        self.function()


class PaneDataHandler(object):
    """Define a callback function that will receive a dictionary of a pane's own data values."""
    
    def __init__(self, function):
        self.function = function

    def call(self, tkpane_obj):
        self.function(tkpane_obj.values())


class PaneKeyHandler(object):
    """Define a callback function that will receive a list of a pane's own data keys."""

    def __init__(self, function):
        self.function = function

    def call(self, tkpane_obj):
        self.function(tkpane_obj.datakeylist)


class AllDataHandler(object):
    """Define a callback function that will receive a dictionary of all of a pane's data values."""

    def __init__(self, function):
        self.function = function

    def call(self, tkpane_obj):
        self.function(tkpane_obj.datdict)


def has_handler_function(handler_list, function):
    """Determine whether any Handler object in the given list is for the specified function.
    
    Returns True or False.
    """
    for h in handler_list:
        if h.function == function:
            return True
    return False



#===============================================================================
#       The TkPane class
#-------------------------------------------------------------------------------

class TkPane(tk.Frame):
    """Base class for Tkinter UI elements (panes).  This class is meant to be subclassed,

    Subclasses are expected to call the TkPane class' initialization function.
    
    :param parent: The parent widget for this pane (ordinarily a frame or top-level element).
    :param config_opts: A dictionary of keyword arguments for configuring the pane's frame.
    :param grid_opts: A dictionary of keyword arguments for gridding the pane's frame.
    
    Attributes of a TkPane object that may be assigned after instantiation are:
    
    * required: A Boolean indicating whether valid data must be entered.
      Note that this applies to all widgets on the pane.  If some data values
      are required by the application and others are not, the widgets for
      those different data values should be on different panes.
    * datakeylist: A list of dictionary keys for data items managed by this
      pane.
    * datadict: A dictionary containing all data managed or used by this pane.
    * on_change_data_valid: A list of Handler object to be called when data
      are changed and valid.
    * on_change_data_invalid: A list of Handler objects to be called when
      data are changed and invalid.
    * on_exit_data_valid: A list of Handler objects to be called when the
      pane loses focus and the data are valid.
    * on_exit_data_invalid: A list of Handler objects to be called when
      the pane loses focus and the data are invalid.
    * on_enable: A list of Handler objects to be called when this pane
      is enabled.
    * on_clear: A list of Handler objects to be called when this pane
      is cleared.
    * on_disable: A list of Handler objects to be called when this pane
      is disabled.
    * keys_to_enable: Keys of datadict that must be defined for this pane
      to be enabled.
    * status_reporter: An object with a well-known method (set_status)
      for reporting status information.
    * progress_reporter: An object with well-known methods (set_determinate,
      set_indeterminate, set_value, start, stop) for reporting or displaying
      progress information.
    
    Methods to be overridden by subclasses that manage data are:
    
    * save_data(is_valid): Updates or clears the data dictionary with widget values, depending on whether the data are valid.
    * valid_data(widget=None): Evaluates whether data entered into widgets on the pane are valid, Returns True or False.
    * entry_widgets(): Returns a list of widgets used for data entry.
    * enable_pane(): Enable widgets on this pane.
    * clear_pane(): Clear data from widgets on this pane.
    * disable_pane(): Disable widgets on this pane.
    
    Subclasses must create all the widgets on the pane and configure their
    appearance and actions.  Interactions between panes should be managed
    using the lists of Handler callbacks.
    """

    def __init__(self, parent, pane_name, config_opts=None, grid_opts=None):
        # Create and configure the Frame for this pane.
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.pane_name = pane_name
        if config_opts is not None:
            self.configure(**config_opts)
        self.original_values = {}
        self.grid(row=0, column=0, sticky=tk.NSEW)
        if grid_opts is not None:
            self.grid(**grid_opts)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # When the user enters the pane, copy the datadict for later comparison.
        self.bind("<Enter>", self.entering)
        # When the user leaves the pane, trigger a method to update the datadict,
        # cascade Handler functions, and send a status message.
        self.bind("<Leave>", self.leaving)
        self.bind("<FocusOut>", self.leaving)
        # 'invalid_color' will be used as the background color of Entry or other
        # widgets when the data value is invalid.  If 'invalid_color' is assigned
        # directly, it will not be applied immediately; use 'set_invalid_color()'
        # to assign *and* apply it.
        #self.invalid_color = "#ffccff"
        self.invalid_color = "#fff5ff"
        self.valid_color = "#ffffff"
        #=======================================================================
        #       ASSIGNABLE CALLBACKS
        # Callback function handlers (PaneDataHandler, PaneKeyHandler, or
        # AllDataHandler objects) should be assigned to each of these lists
        # as appropriate.
        #-----------------------------------------------------------------------
        # Handlers that will be called when data in the pane are changed during
        # editing (e.g., during key entry into an Entry widget) and the data
        # are valid.  These handlers might enable other panes.
        self.on_change_data_valid = []
        # Handlers that will be called when data in the pane are changed during
        # editing (e.g., during key entry into an Entry widget) and the data
        # are invalid.  These handlers might disable and/or clear other panes.
        self.on_change_data_invalid = []
        # Handlers that will be called when the pane loses focus and the data
        # are valid.
        self.on_exit_data_valid = []
        # Handlers that will be called when the pane loses focus and the data
        # are invalid.
        self.on_exit_data_invalid = []
        # Handlers that will be called when this pane is enabled.
        self.on_enable = []
        # Handlers that will be called when this pane is cleared.
        self.on_clear = []
        # Handlers that will be called when this pane is disabled.
        self.on_disable = []
        #=======================================================================
        #       ASSIGNABLE ATTRIBUTES
        # The following attributes should be assigned, as needed, after
        # a TkPane subclass object is instantiated.
        #-----------------------------------------------------------------------
        # The 'required' Boolean should be used to control whether the user
        # can leave the pane if input widgets do not have valid data.  This
        # will require customization of the subclass by binding the <FocusOut>
        # event to input widgets using a method that implements the validity check.
        self.required = False
        # 'datakeylist' should contain the names (keys) of only the data items 
        # managed by this pane.
        self.datakeylist = []
        # 'datadict' contains values of data items managed by this pane and also, 
        # possibly, other data values (e.g., as provided by calls to 'enable()') 
        # that may be needed.
        self.datadict = {}
        # 'keys_to_enable' should contain a list of the datadict keys that must be
        # defined for the pane to actually enable itself.  This may include some,
        # all, or none of the values in 'datakeylist', and may include other
        # data keys such as those provided to the 'enable' method or to some
        # custom method.
        self.keys_to_enable = []
        # 'status_reporter' should be an object with well-known methods for
        # reporting textual status information, as on a status bar.  Method
        # names should be:
        #    * 'set_status': Displays the specified text.
        #    * 'clear_status':Clears any displayed text.
        self.status_reporter = None
        # 'progress_reporter' should be an object with well-known methods for
        # reporting progress, as on a progress bar.  Method names should be:
        #    * 'set_determinate': Sets a progress bar to show progress over a 
        #      fixed range of values, e.g., 0 to 100.
        #    * 'set_indeterminate': Sets a progress bar to show a continuously
        #      active progress indicator (e.g., oscillating).
        #    * 'set_value': Sets a definite progress bar to a specific value.
        #    * 'start': Starts an indefinite progress bar.
        #    * 'stop': Stops an indefinite progress bar.
        self.progress_reporter = None
        #=======================================================================

    def call_handlers(self, handler_list):
        for h in handler_list:
            h.call(self)

    def save_data(self, is_valid, entry_widget=None):
        """Update the pane's data dictionary with data from entry widgets.
        
        This may add a value, revise a value, or remove a key (if not is_valid).
        This may also change widget displays, e.g., setting invalid values to
        empty strings or the equivalent.
        
        This method must be overridden by any subclass that manages data.
        """
        pass

    def valid_data(self, entry_widget=None):
        """Evaluate whether data entered into one or all widgets on the pane are valid,
        
        Returns True or False.  Defaults to returning True.
        This method must be overridden by any subclass that manages data.
        """
        return True
    
    def show_widget_validity(self, widget, is_valid):
        """Set the widget's background color to the 'valid' or 'invalid' color."""
        col = self.valid_color if is_valid or not self.required else self.invalid_color
        try:
            widget.configure(background=col)
        except:
            # If the background color is not configurable on this widget.
            pass
    
    def entry_widgets(self):
        """Return a list of entry widgets on the pane.
        
        The purpose of this method is for the TkPane to automatically recolor
        all entry widgets based on their validity.  Defaults to returning an
        empty list.
        
        This method should be overridden by any subclass that manages data.
        """
        return []
    
    def show_widgets_validity(self):
        """Set all widgets' background color to the 'valid' or 'invalid' color."""
        for w in self.entry_widgets():
            self.show_widget_validity(w, self.valid_data(w))
    
    def handle_change_validity(self, is_valid, entry_widget=None):
        """Update the data dictionary from pane widgets and call appropriate handlers for data changes.
        
        :param is_valid: A Boolean indicating whether or not data on the pane are valid.
        :param entry_widget: The widget that has been changed.  Its state will be changed as appropriate to indicate the data validity.
        
        If entry_widget is not provided, all widgets will have their state changed to indicate the data validity.
        """
        self.save_data(is_valid, entry_widget)
        if is_valid:
            self.call_handlers(self.on_change_data_valid)
        else:
            self.call_handlers(self.on_change_data_invalid)
        if entry_widget is not None:
            self.show_widget_validity(entry_widget, is_valid)
        else:
            for w in self.entry_widgets():
                self.show_widget_validity(w, is_valid)
    
    def handle_exit_validity(self, is_valid, widget_list=None):
        """Update the data dictionary from pane widgets and call appropriate handlers for pane exiting.
        
        :param is_valid: A Boolean indicating whether or not data on the pane are valid.
        :param widget_list: A list of widgets to which 'is_valid' applies.  Their states will be changed as appropriate to indicate the data validity.
        
        If widget_list is not provided, all widgets will have their state changed to indicate the data validity.
        """
        self.save_data(is_valid, None)
        if is_valid:
            self.call_handlers(self.on_exit_data_valid)
        else:
            self.call_handlers(self.on_exit_data_invalid)
        if widget_list is not None:
            for w in widget_list:
                self.show_widget_validity(w, is_valid)
        else:
            for w in self.entry_widgets():
                self.show_widget_validity(w, is_valid)
    
    def send_status_message(self, is_valid):
        """Send a status message reporting data values and/or validity if data have changed.
        
        :param is_valid: A Boolean indicating whether or not the data on the pane are valid.
        
        This method may be overridden."""
        if self.datadict != self.original_values:
            if is_valid:
                vals = self.values()
                dk = vals.keys()
                if len(dk) == 0:
                    self.report_status(u"%s data cleared." % self.pane_name)
                elif len(dk) == 1:
                    self.report_status(u"%s set to %s." % (self.pane_name, vals[dk[0]]))
                else:
                    msg = "%s data set to:" % self.pane_name
                    for i, k in enumerate(dk):
                        if i > 0:
                            msg += ";"
                        msg += "%s %s=%s" % (msg, k, vals[k])
                    msg += "."
                    self.report_status(msg)
            else:
                self.report_status(u"%s is invalid." % self.pane_name)

    def entering(self, event):
        """Record the initial data value to be used later to determine if it has changed."""
        self.original_values = copy.deepcopy(self.datadict)
    
    def leaving(self, event):
        """Revise the data dictionary, call all exit handlers, and report status.
        
        Revision of the data dictionary is carried out through the save_data
        method, which should be overridden by subclasses.  The appropriate set
        of exit handlers is called depending on sata validity.
        """
        is_valid = self.valid_data(None)
        self.handle_exit_validity(is_valid)
        self.send_status_message(is_valid)
        if is_valid and self.original_values != self.datadict:
            self.original_values = copy.deepcopy(self.datadict)

    def values(self):
        """Return data values managed by this pane as a dictionary.

        If the 'datakeylist' and 'datadict' attributes are managed properly,
        this function will work as intended, but subclasses may need to
        override this method if they are not using the datadict to store the
        pane's data.
        """
        return dict([(k, self.datadict[k]) for k in self.datakeylist if self.datadict.get(k)])
    
    def clear_data(self, data_key=None):
        """Remove the specified value from the pane's data dictionary.
        
        :param data_key: The key of the dictionary entry to remove.
        
        If no data key is specified, all data values managed by this pane will
        be removed.  This method is intended primarily for use by subclasses."""
        if data_key is None:
            for k in self.datakeylist:
                if k in self.datadict.keys():
                    del self.datadict[k]
        else:
            if data_key in self.datadict.keys():
                del self.datadict[data_key]

    def set_invalid_color(self, color):
        """Save the color to be applied to any invalid widgets, and immediately apply it."""
        self.invalid_color = color
        self.show_widgets_validity()

    def requires(self, other_pane, clear_on_enable=False, clear_on_disable=False):
        """Set handler functions for the other pane to enable or disable this pane.
        
        :param other_pane: The pane which must have valid data for this pane to be enabled.
        :param clear_on_enable: A Boolean indicating whether this pane should be cleared when it is enabled.
        :param clear_on_disable: A Boolean indicating whether this pane should be cleared when it is disabled.
       
        The other pane's lists of Handler callbacks are modified to enable or
        disable this pane when the other pane's data are valid or invalid,
        respectively.  The other pane's 'required' attribute is also set to True.
        Optionally, this pane can also be cleared when it is either enabled or 
        disabled as a result of data validity changes in the other pane.
        """
        other_pane.required = True
        self.keys_to_enable = list(set(self.keys_to_enable) | set(other_pane.datakeylist))
        if not has_handler_function(other_pane.on_change_data_valid, self.enable):
            other_pane.on_change_data_valid.append(PaneDataHandler(self.enable))
        if not has_handler_function(other_pane.on_exit_data_valid, self.enable):
            other_pane.on_exit_data_valid.append(PaneDataHandler(self.enable))
        if not has_handler_function(other_pane.on_change_data_invalid, self.disable):
            other_pane.on_change_data_invalid.append(PaneKeyHandler(self.disable))
        if not has_handler_function(other_pane.on_exit_data_invalid, self.disable):
            other_pane.on_exit_data_invalid.append(PaneKeyHandler(self.disable))
        if clear_on_enable:
            if not has_handler_function(other_pane.on_change_data_valid, self.clear):
                other_pane.on_change_data_valid.append(PaneKeyHandler(self.clear))
            if not has_handler_function(other_pane.on_exit_data_valid, self.clear):
                other_pane.on_exit_data_valid.append(PaneKeyHandler(self.clear))
        if clear_on_disable:
            if not has_handler_function(other_pane.on_change_data_invalid, self.clear):
                other_pane.on_change_data_invalid.append(PaneKeyHandler(self.clear))
            if not has_handler_function(other_pane.on_exit_data_invalid, self.clear):
                other_pane.on_exit_data_invalid.append(PaneKeyHandler(self.clear))
        other_pane.show_widgets_validity()

    def can_enable(self):
        """Determine whether all the required data values are available for this pane to actually enable itself.
        
        Returns True or False.
        """
        return all([dk in self.datadict.keys() for dk in self.keys_to_enable])

    def enable_pane(self):
        """ Enable any widgets on this pane that are necessary for initial user interaction.

        This method should be overridden by child classes.
        This method is not meant to be called directly, but only called indirectly
        via the enable() method.
        """
        pass

    def clear_pane(self):
        """Clear data from widgets on this pane, as appropriate.

        This method should be overridden by child classes.
        This method is not meant to be called directly, but only called indirectly
        via the clear() method.
        """
        pass
        
    def disable_pane(self):
        """Disable any widgets on this pane that are necessary for user interaction.

        This method should be overridden by child classes.
        This method is not meant to be called directly, but only called indirectly
        via the disable() method.
        """
        pass

    def enable(self, incoming_data={}):
        """Enable this pane (subject to data requirements being met).

        :param incoming_data: A dictionary of data from the caller.
        
        This method may be overridden by child classes if simply overriding
        the enable_pane() method is not sufficient to implement the needed behavior.
        """
        if incoming_data is not None:
            for k in incoming_data.keys():
                self.datadict[k] = incoming_data[k]
        if self.can_enable():
            self.enable_pane()
            self.call_handlers(self.on_enable)

    def clear(self, keylist=[]):
        """Re-initialize any data entry or display elements on the pane.
        
        :param keylist: A list of the keys to be removed from the pane's data dictionary.

        This method may be overridden by child classes if simply overriding
        the clear_pane() method is not sufficient to implement the needed behavior.
        """
        if keylist is not None:
            for k in keylist:
                if k in self.datadict.keys():
                    del self.datadict[k]
        self.clear_pane()
        self.call_handlers(self.on_clear)

    def disable(self, keylist=[]):
        """Disable the pane so that the user can't interact with it.

        :param keylist: A list of the keys to be removed from the pane's data dictionary.

        This method may be overridden by child classes if simply overriding
        the disable_pane() method is not sufficient to implement the needed behavior.
        """
        if keylist is not None:
            for k in keylist:
                if k in self.datadict.keys():
                    del self.datadict[k]
        self.disable_pane()
        self.call_handlers(self.on_disable)

    def set(self, data):
        """Accepts data to be used by the pane as appropriate.
        
        :param data: This is intended to be a dictionary, but subclasses that override this method can accept any number of parameters of any type.
        
        This method allows other panes or application code to send data to a pane
        without triggering any callbacks.  The use of this data and even the type
        of data is defined entirely by the custom pane subclass, and should be
        respected by the caller.  No other TkPane methods use this method; it exists
        only to provide a uniform data-passing method for all subclasses.
        """
        pass
    
    def report_status(self, status_msg):
        """Send the given message to the status reporting function, if it is defined."""
        if self.status_reporter is not None:
            self.status_reporter.set_status(status_msg)
    
    def report_progress(self, progress_value):
        """Send the given progress value to the progress reporting function, if it is defined."""
        if self.progress_reporter is not None:
            self.progress_reporter.set_value(progress_value)
    
def en_or_dis_able_all(panelist):
    """Enable or disable all panes in the list, as required by their data status."""
    for p in panelist:
        if p.can_enable():
            p.enable()
        else:
            p.disable()
