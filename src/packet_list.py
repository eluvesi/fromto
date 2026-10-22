# packet_list.py
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

from gi.repository import Adw, GObject, Gtk
from scapy.all import Ether, ICMP, IP, TCP, UDP
from itertools import count

from .packet_row import PacketRow


@Gtk.Template(resource_path='/com/github/eluvesi/FromTo/packet_list.ui')
class PacketList(Gtk.Box):
    __gtype_name__ = 'PacketList'

    __gsignals__ = {
        'packet-selected': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        'send-packet': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
    }

    packet_listbox = Gtk.Template.Child()
    add_packet_buttonrow = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._rows = []

        self.add_packet_buttonrow.connect('activated', self._on_add_packet)
        self.packet_listbox.connect('row-selected', self._on_row_selected)

        # Temporary solution for creating different packets.
        self._packet_counter = count(0)

    @property
    def packets(self):
        """Return the packets in queue order."""
        return [row.packet for row in self._rows]

    def _create_default_packet(self):
        """Create a temporary packet until the editor is implemented."""
        number = next(self._packet_counter) % 4 + 1
        return (
            Ether()
            / IP(src=f'192.0.2.{number}', dst=f'192.0.2.{number}')
            / UDP(sport=50000+number, dport=53)
        )

    def _on_add_packet(self, *_args):
        """Add a new packet to the list."""
        packet = self._create_default_packet()
        index = len(self._rows)
        total = index + 1

        row = PacketRow(packet, index, total)
        row.connect('send-packet', self._on_send_packet)
        row.connect('move-packet', self._on_move_packet)
        row.connect('remove-packet', self._on_remove_packet)
        self._rows.append(row)

        self.packet_listbox.insert(row, index)
        self.packet_listbox.select_row(row)

        self._update_rows()

    def _on_send_packet(self, row):
        """Emit a request to send the packet from the selected row."""
        if row not in self._rows:
            return

        self.emit('send-packet', row.packet)

    def _on_remove_packet(self, row):
        """Remove a packet row from the list."""
        if row not in self._rows:
            return

        self._rows.remove(row)
        self.packet_listbox.remove(row)

        self._update_rows()

    def _on_move_packet(self, row, offset):
        """Move a packet row up or down."""
        if row not in self._rows:
            return

        old_index = self._rows.index(row)
        new_index = old_index + offset
        if not 0 <= new_index < len(self._rows):
            return

        self._rows.pop(old_index)
        self._rows.insert(new_index, row)

        self.packet_listbox.remove(row)
        self.packet_listbox.insert(row, new_index)
        self.packet_listbox.select_row(row)

        self._update_rows()

    def _on_row_selected(self, _listbox, row):
        """Emit a signal when the selected packet changes."""
        packet = row.packet if row is not None else None
        self.emit('packet-selected', packet)

    def _update_rows(self):
        """Refresh move-button sensitivity for every row."""
        total = len(self._rows)
        for index, row in enumerate(self._rows):
            row.update_position(index, total)


