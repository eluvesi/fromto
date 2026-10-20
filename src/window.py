# window.py
#
# Copyright 2026 eluvesi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk
from scapy.all import get_if_list

from .packet_editor import PacketEditor
from .packet_list import PacketList
from .packet_row import PacketRow


@Gtk.Template(resource_path='/com/github/eluvesi/FromTo/window.ui')
class FromtoWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'FromtoWindow'

    packet_list = Gtk.Template.Child()
    packet_editor = Gtk.Template.Child()
    interface_dropdown = Gtk.Template.Child()
    delay_spinbutton = Gtk.Template.Child()
    send_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._populate_interfaces()

        # Sending remains disabled until it is implemented.
        self.send_button.set_sensitive(False)

    def _populate_interfaces(self):
        """Populate the interface dropdown using Scapy."""
        interfaces = get_if_list()
        self.interface_dropdown.set_model(Gtk.StringList.new(interfaces))
        self.interface_dropdown.set_sensitive(bool(interfaces))

