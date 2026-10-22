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

from gi.repository import Adw, Gio, GObject, Gtk
from scapy.all import Ether, ICMP, IP, TCP, UDP


@Gtk.Template(resource_path='/com/github/eluvesi/FromTo/packet_row.ui')
class PacketRow(Adw.ActionRow):
    __gtype_name__ = 'PacketRow'

    __gsignals__ = {
        'send-packet': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (),
        ),
        'move-packet': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (int,),
        ),
        'remove-packet': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (),
        ),
    }

    def __init__(self, packet, position, total):
        super().__init__()

        self.packet = packet
        self.position = position
        self.total = total

        title, subtitle = self._describe_packet(packet)
        self.set_title(title)
        self.set_subtitle(subtitle)

        self._actions = Gio.SimpleActionGroup()
        self.insert_action_group('packet', self._actions)
        self.create_action('send', lambda *_: self.emit('send-packet'))
        self.create_action('move-up', lambda *_: self.emit('move-packet', -1))
        self.create_action('move-down', lambda *_: self.emit('move-packet', 1))
        self.create_action('remove', lambda *_: self.emit('remove-packet'))

        self.update_position(position, total)

    def create_action(self, name, callback):
        """Add a row action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is activated
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self._actions.add_action(action)

    def update_position(self, position, total):
        """Update packet reordering controls."""
        self.position = position
        self.total = total

        self._actions.lookup_action('move-up').set_enabled(
            position > 0
        )
        self._actions.lookup_action('move-down').set_enabled(
            position < total - 1
        )

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
        subtitle = f'{data_link} / {network} / {transport}'
        return title, subtitle

