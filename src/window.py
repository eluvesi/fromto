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
from scapy.all import get_if_list, sendp

from .packet_list import PacketList
from .packet_workspace import PacketWorkspace


@Gtk.Template(resource_path='/com/github/eluvesi/FromTo/window.ui')
class FromtoWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'FromtoWindow'

    toast_overlay = Gtk.Template.Child()
    packet_list = Gtk.Template.Child()
    packet_workspace = Gtk.Template.Child()
    interface_dropdown = Gtk.Template.Child()
    delay_spinbutton = Gtk.Template.Child()
    send_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.packet_list.connect(
            'packet-selected', self._on_packet_selected
        )
        self.packet_list.connect(
            'send-packet', self._on_send_packet
        )
        self.packet_workspace.connect(
            'toast-requested', self._on_toast_requested
        )

        # Sending remains disabled until it is implemented.
        self.send_button.set_sensitive(False)

        self._populate_interfaces()

    def _populate_interfaces(self):
        """Populate the interface dropdown using Scapy."""
        interfaces = get_if_list()
        self.interface_dropdown.set_model(Gtk.StringList.new(interfaces))
        self.interface_dropdown.set_sensitive(bool(interfaces))

    def _on_packet_selected(self, _packet_list, packet):
        """Display the selected packet in the packet workspace."""
        self.packet_workspace.set_packet(packet)

    def _on_send_packet(self, _packet_list, packet):
        """Send one packet using the selected network interface."""
        selected_item = self.interface_dropdown.get_selected_item()

        if selected_item is None:
            self.show_toast(_('No Network Interface Selected'))
            return

        interface = selected_item.get_string()

        try:
            sendp(packet, iface=interface, count=1, verbose=False)
        except Exception as error:
            self.show_toast(_('Packet Sending Failed'))
            return

        self.show_toast(_('Packet Sent'))

    def _on_toast_requested(self, _source, message):
        """Display a toast requested by the packet workspace."""
        self.show_toast(message)

    def show_toast(self, message):
        """Show a brief notification in the application window."""
        self.toast_overlay.dismiss_all()
        self.toast_overlay.add_toast(Adw.Toast.new(message))

