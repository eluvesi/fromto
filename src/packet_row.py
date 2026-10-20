# packet_row.py
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


@Gtk.Template(resource_path='/com/github/eluvesi/FromTo/packet_row.ui')
class PacketRow(Adw.ActionRow):
    __gtype_name__ = 'PacketRow'

    __gsignals__ = {
        'move-packet': (GObject.SignalFlags.RUN_LAST, None, (int,)),
        'remove-packet': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    up_button = Gtk.Template.Child()
    down_button = Gtk.Template.Child()
    remove_button = Gtk.Template.Child()

    def __init__(self, packet, position, total):
        super().__init__()

        self.packet = packet
        self.position = position
        self.total = total

        title, subtitle = self._describe_packet(packet)
        self.set_title(title)
        self.set_subtitle(subtitle)

        self.up_button.connect(
            'clicked',
            lambda *_: self.emit('move-packet', -1),
        )
        self.down_button.connect(
            'clicked',
            lambda *_: self.emit('move-packet', 1),
        )
        self.remove_button.connect(
            'clicked',
            lambda *_: self.emit('remove-packet'),
        )

        self.update_position(position, total)

    def update_position(self, position, total):
        """Update packet reordering controls."""
        self.position = position
        self.total = total
        self.up_button.set_sensitive(position > 0)
        self.down_button.set_sensitive(position < total - 1)

    @staticmethod
    def _describe_packet(packet):
        """Return a title and subtitle describing a Scapy packet."""
        # Data Link layer
        if packet.haslayer(Ether):
            eth_frame = packet[Ether]
            source = eth_frame.src or '?'
            destination = eth_frame.dst or '?'
            data_link = 'Ethernet'
        else:
            source = '?'
            destination = '?'
            data_link = '–'

        # Network layer
        if packet.haslayer(IP):
            ip_packet = packet[IP]
            source = ip_packet.src
            destination = ip_packet.dst
            network = 'IPv4'
        elif packet.haslayer(IPv6):
            ip_packet = packet[IPv6]
            source = ip_packet.src
            destination = ip_packet.dst
            network = 'IPv6'
        else:
            network = '—'

        # Transport layer
        if packet.haslayer(TCP):
            transport = 'TCP'
        elif packet.haslayer(UDP):
            transport = 'UDP'
        elif packet.haslayer(ICMP):
            transport = 'ICMP'
        else:
            transport = '—'

        title = f'{source} → {destination}'
        subtitle = f'{data_link} · {network} · {transport}'
        return title, subtitle
