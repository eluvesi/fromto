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

from .ethernet import EthernetSettingsGroup
from .ipv4 import IPv4SettingsGroup
from .icmp import ICMPSettingsGroup
from .tcp import TCPSettingsGroup
from .udp import UDPSettingsGroup


PROTOCOLS = {
    'data_link': {
        'Ethernet II': ('ethernet', EthernetSettingsGroup),
    },
    'network': {
        'IPv4': ('ipv4', IPv4SettingsGroup),
    },
    'transport': {
        'ICMP': ('icmp', ICMPSettingsGroup),
        'TCP': ('tcp', TCPSettingsGroup),
        'UDP': ('udp', UDPSettingsGroup),
    },
}

def setup_protocol_layer(combo_row, stack, protocols):
    combo_row.set_model(Gtk.StringList.new(list(protocols)))

    for protocol_id, settings_group in protocols.values():
        stack.add_named(settings_group(), protocol_id)

    combo_row.connect(
        'notify::selected',
        lambda row, _: stack.set_visible_child_name(
            list(protocols.values())[row.get_selected()][0]
        ),
    )
    combo_row.set_selected(0)


@Gtk.Template(
    resource_path=
    '/com/github/eluvesi/FromTo/packet_workspace/editor/editor-page.ui'
)
class EditorPage(Gtk.Box):
    """Display a packet summary, field details, and hexadecimal dump."""
    __gtype_name__ = 'EditorPage'

    __gsignals__ = {
        'toast-requested': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (str,),
        ),
    }

    data_link_protocol_row = Gtk.Template.Child()
    data_link_protocols_stack = Gtk.Template.Child()
    network_protocol_row = Gtk.Template.Child()
    network_protocols_stack = Gtk.Template.Child()
    transport_protocol_row = Gtk.Template.Child()
    transport_protocols_stack = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None

        setup_protocol_layer(
            self.data_link_protocol_row,
            self.data_link_protocols_stack,
            PROTOCOLS["data_link"],
        )
        setup_protocol_layer(
            self.network_protocol_row,
            self.network_protocols_stack,
            PROTOCOLS["network"],
        )
        setup_protocol_layer(
            self.transport_protocol_row,
            self.transport_protocols_stack,
            PROTOCOLS["transport"],
        )

    @property
    def packet(self):
        """The packet currently displayed by the editor."""
        return self._packet

    def set_packet(self, packet):
        """Set the packet to preview and update all views."""
        self._packet = packet

