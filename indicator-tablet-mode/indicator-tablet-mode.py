#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gdk as gdk
import os, subprocess
import signal


rotations = ["normal", "left", "inverted", "right"]
matrices  = {"normal": "1 0 0 0 1 0 0 0 1", 
                           "left": "0 -1 1 1 0 0 0 0 1", 
                           "inverted": "-1 0 1 0 -1 1 0 0 1",
                           "right": "0 1 0 -1 0 1 0 0 1"
                          }
DISPLAY = ""
THEME = ""
THEME_DARK = "dark"
THEME_LIGHT = "light"
ICON_LAPTOP = "indicator-tablet-mode-laptop"
ICON_TABLET = "indicator-tablet-mode-tablet"

def _luminance(r, g, b, base=256):
    """Calculates luminance of a color, on a scale from 0 to 1, meaning that 1 is the highest luminance.
    r, g, b arguments values should be in 0..256 limits, or base argument should define the upper limit otherwise"""
    return (0.2126*r + 0.7152*g + 0.0722*b)/base


def __pixel_at(x, y):
    """Returns (r, g, b) color code for a pixel with given coordinates (each value is in 0..256 limits)"""
    root_window = gdk.get_default_root_window()
    buf = gdk.pixbuf_get_from_window(root_window, x, y, 1, 1)
    pixels = buf.get_pixels()
    if type(pixels) == type(""):
        rgb = tuple([int(byte.encode('hex'), 16) for byte in pixels])
    else:
        rgb = tuple(pixels)
    return rgb


def detect_theme():
    # Identify the type of theme by checking a pixel color in the panel.
    pixel_rgb = __pixel_at(2, 2)
    luminance = _luminance(*pixel_rgb[:3])
    return THEME_LIGHT if luminance >= 0.5 else THEME_DARK


def get_resource_path(theme, filename=""):
    parent = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(parent, theme, filename)


def detect_display():
    return subprocess.check_output("xrandr | grep ' connected' | cut -f 1 -d ' '", shell=True).strip()


# We always set these three simultaneously, otherwise you may disable all input.
def set_tablet_mode(b):
    set_onscreen_keyboard(b)
    set_keyboard(not b)
    set_touchpad(not b)


def set_onscreen_keyboard(b):
    # Onboard can cause unity panel to crash when it creates the onboard indicator, but it seems not due to the way we launch it.
    try:
        if b == True:
            subprocess.call("onboard &disown", shell=True)
        else:
            subprocess.call("killall onboard", shell=True)
    except:
        True


def set_keyboard(b):
    if b == True:
        subprocess.call("xinput enable 'AT Translated Set 2 keyboard'", shell=True)
    else:
        subprocess.call("xinput disable 'AT Translated Set 2 keyboard'", shell=True)


def set_touchpad(b):
    if b == True:
        subprocess.call("xinput enable 'SynPS/2 Synaptics TouchPad'", shell=True)
    else:
        subprocess.call("xinput disable 'SynPS/2 Synaptics TouchPad'", shell=True)


def set_rotation(rotation):
    global rotations
    if rotation not in rotations:
        rotation = rotations[0]
    matrix = matrices[rotation]
    # Rotate the screen
    subprocess.call("xrandr --output "+DISPLAY+" --rotate "+rotation, shell=True)
    # Apparently xrandr in Ubuntu 16.04 keeps the screen output and touchscreen input  orientation synchronized.
    # Rotate the touch input (before 16.04)
    subprocess.call("xinput set-prop 'ELAN Touchscreen' 'Coordinate Transformation Matrix' "+matrix, shell=True)
    # Make sure that in normal mode, the touchpad is enabled again (if it was disabled).
    if rotation == "normal":
        set_touchpad(True)


def next_rotation(direction):
    global rotations
    rotation = get_current_rotation()
    index = rotations.index(rotation)
    new_index = index + direction if (direction == -1 or direction == 1) else index
    set_rotation(rotations[new_index])


def get_current_rotation():
    global rotations
    # Extract the rotation from xrandr for the first connected screen (probably the main screen).
    rotation = subprocess.check_output("xrandr  | grep "+DISPLAY+" | cut -f 5 -d ' '", shell=True)
    rotation = rotation.strip();
    if rotation not in rotations:
        rotation = rotations[0]
    print "current rotation: "+rotation
    return rotation


def quit(self):
    # Reset everything:
    set_onscreen_keyboard(False)
    set_keyboard(True)
    set_touchpad(True)
    set_rotation("normal")
    Gtk.main_quit()


def build_menu(indicator):
    # create a menu
    menu = Gtk.Menu()
    
    # create menu items
    
    # tablet mode with checkbox
    menu_item_tablet = Gtk.CheckMenuItem("Tablet Mode")
    menu_item_tablet.connect("notify::active", (lambda self, data: set_tablet_mode(self.get_active()) or ind.set_icon(ICON_TABLET if self.get_active() else ICON_LAPTOP) ) )
    menu_item_tablet.set_active(False)
    menu.append(menu_item_tablet)
    menu_item_tablet.show()
    
    # rotation lock/unlock with checkbox
    # TODO: This could be implemented using monitor-sensor, like in:
    # https://linuxappfinder.com/blog/auto_screen_rotation_in_ubuntu
    # But it this example is not python and creates a temporary file in $HOME.
    # Also monitor-sensor is sometimes not triggered, eg. when rotating the device back to normal.
    
    # label
    menu_item_label = Gtk.MenuItem("Display rotation:")
    menu_item_label.set_sensitive(False)
    menu.append(menu_item_label)
    menu_item_label.show()
    
    menu.append(Gtk.SeparatorMenuItem()) # TODO: Why does this not display?
    
    # rotation normal
    group = []
    menu_item_normal = Gtk.RadioMenuItem.new_with_label(group, "normal")
    menu.append(menu_item_normal)
    menu_item_normal.connect("activate", (lambda w, data: set_rotation(data)), "normal")
    menu_item_normal.show()
    menu_item_normal.activate() # Selected by default
    group = menu_item_normal.get_group()
    
    # rotation left
    menu_item_left = Gtk.RadioMenuItem.new_with_label(group, "left")
    menu.append(menu_item_left)
    #menu_item_left.connect("activate", (lambda w, data: next_rotation(data)), 1)
    menu_item_left.connect("activate", (lambda w, data: set_rotation(data)), "left")
    menu_item_left.show()
    
    # rotation right
    menu_item_right = Gtk.RadioMenuItem.new_with_label(group, "right")
    menu.append(menu_item_right)
    #menu_item_right.connect("activate", (lambda w, data: next_rotation(data)), -1)
    menu_item_left.connect("activate", (lambda w, data: set_rotation(data)), "right")
    menu_item_right.show()
    
    # rotation inverted
    menu_item_inverted = Gtk.RadioMenuItem.new_with_label(group, "inverted")
    menu.append(menu_item_inverted)
    menu_item_inverted.connect("activate", (lambda w, data: set_rotation(data)), "inverted")
    menu_item_inverted.show()
    
    menu.append(Gtk.SeparatorMenuItem())
    
    # quit
    menu_item_quit = Gtk.MenuItem("Quit")
    menu.append(menu_item_quit)
    menu_item_quit.connect("activate", quit)
    menu_item_quit.show()
    return menu


if __name__ == "__main__":
    # Detect primary display name:
    #global DISPLAY
    DISPLAY = detect_display()
    if not DISPLAY:
        exit("Name of primary display not found")
    # Detect theme type, dark or light
    #global THEME
    THEME = detect_theme()
    
    # Create indicator
    ind = appindicator.Indicator.new_with_path(
        # indicator id
        "indicator-tablet-mode",
        # icon filename # It seems when using resource_path, extension must be omitted.
        ICON_LAPTOP,
        # category: APPLICATION_STATUS, COMMUNICATIONS, HARDWARE, SYSTEM_SERVICES, OTHER
        appindicator.IndicatorCategory.HARDWARE,
        # icon path
        get_resource_path(THEME))
    ind.set_status(appindicator.IndicatorStatus.ACTIVE)
    ind.set_menu(build_menu(ind))
    
    # TODO: Listen for change of gtk.Settings "gtk-theme-name" and change ind.set_icon_theme_path
    
    # This sets the handler for "INT" signal processing - the one issued by the OS when "Ctrl+C" is typed. The handler we assign to it is the "default" handler, which, in case of the interrupt signal, is to stop execution.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Start the GTK main loop.
    Gtk.main()
