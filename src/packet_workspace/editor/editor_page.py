# editor_page.py
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

from gi.repository import Adw, GObject, Gtk
from scapy.all import Ether, ICMP, IP, TCP, UDP

from .ethernet import EthernetSettingsGroup
from .ipv4 import IPv4SettingsGroup
from .icmp import ICMPSettingsGroup
from .tcp import TCPSettingsGroup
from .udp import UDPSettingsGroup


# Unified registry of supported protocols.
#
# layer — the layer within the editor interface.
# settings_group — a GTK widget containing protocol settings.
# packet_class — the corresponding Scapy class.

PROTOCOLS = {
    'Ethernet II': {
        'layer': 'data_link',
        'settings_group': EthernetSettingsGroup,
        'packet_class': Ether,
    },
    'IPv4': {
        'layer': 'network',
        'settings_group': IPv4SettingsGroup,
        'packet_class': IP,
    },
    'ICMP': {
        'layer': 'transport',
        'settings_group': ICMPSettingsGroup,
        'packet_class': ICMP,
    },
    'TCP': {
        'layer': 'transport',
        'settings_group': TCPSettingsGroup,
        'packet_class': TCP,
    },
    'UDP': {
        'layer': 'transport',
        'settings_group': UDPSettingsGroup,
        'packet_class': UDP,
    },
}

def get_protocols_by_layer(layer):
    """Return the protocols pertaining to the specified layer."""
    return {
        name: definition
        for name, definition in PROTOCOLS.items()
        if definition['layer'] == layer
    }


@Gtk.Template(
    resource_path=
    '/com/github/eluvesi/FromTo/packet_workspace/editor/editor-page.ui'
)
class EditorPage(Gtk.Box):
    """Display a packet summary, field details, and hexadecimal dump."""
    __gtype_name__ = 'EditorPage'

    __gsignals__ = {
        'packet-changed': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (),
        ),
        'toast-requested': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (str,),
        ),
    }

    editor_stack = Gtk.Template.Child()

    data_link_protocol_comborow = Gtk.Template.Child()
    data_link_protocols_stack = Gtk.Template.Child()

    network_protocol_comborow = Gtk.Template.Child()
    network_protocols_stack = Gtk.Template.Child()

    transport_protocol_comborow = Gtk.Template.Child()
    transport_protocols_stack = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None
        self._setup_layers()

    @property
    def packet(self):
        """The packet currently displayed by the editor."""
        return self._packet

    def set_packet(self, packet):
        """Set the packet to preview and update all views."""
        self._packet = packet

        for group in self._settings_groups.values():
            group.set_packet(packet)

        for layer, combo_row, stack in (
            ('data_link', self.data_link_protocol_comborow,
             self.data_link_protocols_stack),
            ('network', self.network_protocol_comborow,
             self.network_protocols_stack),
            ('transport', self.transport_protocol_comborow,
             self.transport_protocols_stack),
        ):
            protocols = get_protocols_by_layer(layer)

            for index, (name, definition) in enumerate(protocols.items()):
                if packet and packet.haslayer(definition['packet_class']):
                    combo_row.set_selected(index)
                    stack.set_visible_child_name(name)
                    break

        self.editor_stack.set_visible_child_name(
            'content' if packet is not None else 'empty'
        )

    def _setup_layers(self):
        """Configure protocols selectors and settings pages at all layers."""
        self._settings_groups = {}

        self._setup_layer(
            self.data_link_protocol_comborow,
            self.data_link_protocols_stack,
            'data_link',
        )
        self._setup_layer(
            self.network_protocol_comborow,
            self.network_protocols_stack,
            'network',
        )
        self._setup_layer(
            self.transport_protocol_comborow,
            self.transport_protocols_stack,
            'transport',
        )

    def _setup_layer(self, combo_row, stack, layer):
        """Set up protocols settings pages for one layer."""
        protocols = get_protocols_by_layer(layer)
        names = list(protocols)

        combo_row.set_model(Gtk.StringList.new(names))

        for name, definition in protocols.items():
            group = definition['settings_group']()
            group.connect('packet-changed', self._on_packet_changed)
            group.connect('toast_requested', self._on_toast_requested)
            stack.add_named(group, name)
            self._settings_groups[name] = group

        def on_selected(row, _pspec):
            index = row.get_selected()
            if index < len(names):
                new_proto_name = names[index]
                old_proto_name = stack.get_visible_child_name()
                stack.set_visible_child_name(new_proto_name)
                self._replace_protocol(old_proto_name, new_proto_name)

        combo_row.connect('notify::selected', on_selected)

    def _replace_protocol(self, old_proto_name, new_proto_name):
        """Replace a packet layer while preserving the remaining layers."""
        if self._packet is None:
            return

        old_class = PROTOCOLS[old_proto_name]['packet_class']
        new_class = PROTOCOLS[new_proto_name]['packet_class']

        old_layer = self._packet.getlayer(old_class)
        if old_layer is None:
            return

        new_layer = new_class()
        new_layer.payload = old_layer.payload
        old_layer.payload = b''

        if old_layer is self._packet:
            self._packet = new_layer
        else:
            parent = self._packet
            while parent.payload is not old_layer:
                parent = parent.payload
            parent.payload = new_layer

        self.set_packet(self._packet)
        self.emit('packet-changed')

    def _on_packet_changed(self, _source):
        """Reports that the package has been modified."""
        self.emit('packet-changed')

    def _on_toast_requested(self, _source, message):
        """Forward toast requests from protocols settings groups."""
        self.emit('toast-requested', message)

