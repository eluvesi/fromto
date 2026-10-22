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

        self.packet_list.connect('packet-selected', self._on_packet_selected)
        self.packet_list.connect('send-packet', self._on_send_packet)

        # Sending remains disabled until it is implemented.
        self.send_button.set_sensitive(False)

        self._populate_interfaces()

    def _populate_interfaces(self):
        """Populate the interface dropdown using Scapy."""
        interfaces = get_if_list()
        self.interface_dropdown.set_model(Gtk.StringList.new(interfaces))
        self.interface_dropdown.set_sensitive(bool(interfaces))

    def _on_packet_selected(self, _packet_list, packet):
        """Display the selected packet in the packet editor."""
        self.packet_editor.set_packet(packet)

    def _show_message(self, heading, body):
        """Show a message dialog."""
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=heading,
            body=body,
        )
        dialog.add_response('close', 'Close')
        dialog.set_close_response('close')
        dialog.present()

    def _on_send_packet(self, _packet_list, packet):
        """Send one packet using the selected network interface."""
        selected_item = self.interface_dropdown.get_selected_item()

        if selected_item is None:
            self._show_message(
                'No interface selected',
                'Select a network interface before sending a packet.',
            )
            return

        interface = selected_item.get_string()

        try:
            sendp(
                packet,
                iface=interface,
                count=1,
                verbose=False,
            )
        except Exception as error:
            self._show_message(
                'Packet sending failed',
                f'Interface: {interface}\n'
                f'{type(error).__name__}: {error}',
            )
            return

        self._show_message(
            'Packet sent',
            f'Scapy completed the send operation on {interface}.',
        )

