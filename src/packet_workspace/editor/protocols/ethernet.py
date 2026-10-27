# ethernet.py
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
from scapy.all import Ether, conf, get_if_hwaddr
from scapy.utils import valid_mac


@Gtk.Template(resource_path=
    '/com/github/eluvesi/FromTo/packet_workspace/editor/protocols/ethernet.ui'
)
class EthernetSettingsGroup(Adw.PreferencesGroup):
    __gtype_name__ = 'EthernetSettingsGroup'

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

    src_entryrow = Gtk.Template.Child()
    src_auto_button = Gtk.Template.Child()
    dst_entryrow = Gtk.Template.Child()
    dst_auto_button = Gtk.Template.Child()
    type_spinrow = Gtk.Template.Child()
    type_auto_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None
        self._updating = False

        for row, field in (
            (self.src_entryrow, 'src'),
            (self.dst_entryrow, 'dst'),
        ):
            row.connect('changed', self._on_mac_changed, field)

        for button, field in (
            (self.src_auto_button, 'src'),
            (self.dst_auto_button, 'dst'),
            (self.type_auto_button, 'type'),
        ):
            button.connect('clicked', self._on_auto, field)

        self.type_spinrow.connect(
            'notify::value', self._on_type_changed
        )

    def set_packet(self, packet):
        """Display Ethernet fields from the supplied packet."""
        self._packet = packet
        self._updating = True
        try:
            enabled = packet is not None and packet.haslayer(Ether)
            self.set_sensitive(enabled)
            if not enabled:
                return

            ether = packet[Ether]
            try:
                ether = Ether(bytes(ether))
            except Exception:
                pass

            self.src_entryrow.set_text(str(ether.src))
            self.dst_entryrow.set_text(str(ether.dst))

            value = ether.type
            self.type_spinrow.set_value(value if value is not None else 0)
        finally:
            self._updating = False

    def _on_mac_changed(self, row, field):
        if self._updating or self._packet is None:
            return

        value = row.get_text().strip()
        if not valid_mac(value):
            return

        self._packet[Ether].setfieldval(field, value)
        self.emit('packet-changed')

    def _on_type_changed(self, row, _pspec):
        if self._updating or self._packet is None:
            return

        self._packet[Ether].type = int(row.get_value())
        self.emit('packet-changed')

    def _on_auto(self, _button, field):
        if self._packet is None or not self._packet.haslayer(Ether):
            return

        if field == 'src':
            self._packet[Ether].src = get_if_hwaddr(conf.iface)
        else:
            delattr(self._packet[Ether], field)

        self.set_packet(self._packet)
        self.emit('packet-changed')

