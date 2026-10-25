# packet_row.py
#
# Copyright 2026 eluvesi
#
# This file is part of From To.
#
# From To is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# From To is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with From To. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gdk, Gio, GObject, Gtk
from scapy.all import Ether, ICMP, IP, TCP, UDP


@Gtk.Template(resource_path='/com/github/eluvesi/FromTo/packet-row.ui')
class PacketRow(Adw.ActionRow):
    """Display a packet and provide packet actions."""
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
        'drop-packet': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (int, int),
        ),
    }

    def __init__(self, packet, position, total):
        super().__init__()

        self.packet = packet
        self.position = position
        self.total = total

        self._actions = Gio.SimpleActionGroup()
        self.insert_action_group('packet', self._actions)
        self.create_action('send', lambda *_: self.emit('send-packet'))
        self.create_action('move-up', lambda *_: self.emit('move-packet', -1))
        self.create_action('move-down', lambda *_: self.emit('move-packet', 1))
        self.create_action('remove', lambda *_: self.emit('remove-packet'))

        title, subtitle = self._describe_packet(packet)
        self.set_title(title)
        self.set_subtitle(subtitle)

        self.update_position(position, total)
        self._setup_drag_and_drop()

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

    def _setup_drag_and_drop(self):
        """Set up drag-and-drop for this row."""
        source = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
        source.connect('prepare', self._on_drag_prepare)
        self.add_controller(source)

        target = Gtk.DropTarget.new(
            GObject.TYPE_INT,
            Gdk.DragAction.MOVE,
        )
        target.connect('drop', self._on_drop)
        self.add_controller(target)

    def _on_drag_prepare(self, _source, _x, _y):
        """Provide the row position as drag content."""
        return Gdk.ContentProvider.new_for_value(self.position)

    def _on_drop(self, _target, source_index, _x, _y):
        """Request moving the dragged row to this position."""
        if source_index == self.position:
            return False

        self.emit('drop-packet', source_index, self.position)
        return True

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

