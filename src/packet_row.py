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


class PacketRow(Adw.ActionRow):
    __gtype_name__ = 'PacketRow'

    __gsignals__ = {
        'move-packet': (GObject.SignalFlags.RUN_LAST, None, (int,)),
        'remove-packet': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self, packet, position, total):
        super().__init__()
        self.packet = packet
        self.position = position
        self.total = total
        self.__build_ui()

    def __build_ui(self):
        title, subtitle = self._describe_packet(self.packet)
        self.set_title(title)
        self.set_subtitle(subtitle)

        send_button = Gtk.Button(
            icon_name='send-symbolic',
            tooltip_text=_('Send packet'),
            valign=Gtk.Align.CENTER,
            sensitive=False,  # Button disabled until sending is implemented.
        )
        self.add_prefix(send_button)

        actions_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            css_classes=['linked'],
        )

        self.up_button = Gtk.Button(
            icon_name='go-up-symbolic',
            tooltip_text=_('Move up'),
            valign=Gtk.Align.CENTER,
        )
        self.up_button.connect(
            'clicked',
            lambda *_: self.emit('move-packet', -1),
        )
        actions_box.append(self.up_button)

        self.down_button = Gtk.Button(
            icon_name='go-down-symbolic',
            tooltip_text=_('Move down'),
            valign=Gtk.Align.CENTER,
        )
        self.down_button.connect(
            'clicked',
            lambda *_: self.emit('move-packet', 1),
        )
        actions_box.append(self.down_button)

        remove_button = Gtk.Button(
            icon_name='user-trash-symbolic',
            tooltip_text=_('Remove packet'),
            valign=Gtk.Align.CENTER,
            css_classes=['destructive-action'],
        )
        remove_button.connect(
            'clicked',
            lambda *_: self.emit('remove-packet'),
        )
        actions_box.append(remove_button)

        self.add_suffix(actions_box)
        self.update_position(self.position, self.total)

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
