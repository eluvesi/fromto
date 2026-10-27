# udp.py
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
from scapy.all import UDP


@Gtk.Template(resource_path=
    '/com/github/eluvesi/FromTo/packet_workspace/editor/protocols/udp.ui'
)
class UDPSettingsGroup(Adw.PreferencesGroup):
    __gtype_name__ = 'UDPSettingsGroup'

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

    sport_spinrow = Gtk.Template.Child()
    sport_reset_button = Gtk.Template.Child()
    dport_spinrow = Gtk.Template.Child()
    dport_reset_button = Gtk.Template.Child()
    len_spinrow = Gtk.Template.Child()
    len_auto_button = Gtk.Template.Child()
    chksum_spinrow = Gtk.Template.Child()
    chksum_auto_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None
        self._updating = False

        for row, field in (
            (self.sport_spinrow, 'sport'),
            (self.dport_spinrow, 'dport'),
            (self.len_spinrow, 'len'),
            (self.chksum_spinrow, 'chksum'),
        ):
            row.connect('notify::value', self._on_field_changed, field)

        for button, field in (
            (self.sport_reset_button, 'sport'),
            (self.dport_reset_button, 'dport'),
            (self.len_auto_button, 'len'),
            (self.chksum_auto_button, 'chksum'),
        ):
            button.connect('clicked', self._on_auto, field)

    def set_packet(self, packet):
        """Display UDP fields from the supplied packet."""
        self._packet = packet
        self._updating = True
        try:
            enabled = packet is not None and packet.haslayer(UDP)
            self.set_sensitive(enabled)
            if not enabled:
                return

            udp = packet[UDP]
            try:
                udp = UDP(bytes(udp))
            except Exception:
                pass

            for row, field in (
                (self.sport_spinrow, 'sport'),
                (self.dport_spinrow, 'dport'),
                (self.len_spinrow, 'len'),
                (self.chksum_spinrow, 'chksum'),
            ):
                value = getattr(udp, field)
                row.set_value(value if value is not None else 0)
        finally:
            self._updating = False

    def _on_field_changed(self, row, _pspec, field):
        if self._updating or self._packet is None:
            return

        self._packet[UDP].setfieldval(field, int(row.get_value()))
        self.emit('packet-changed')

    def _on_auto(self, _button, field):
        if self._packet is None or not self._packet.haslayer(UDP):
            return

        delattr(self._packet[UDP], field)
        self.set_packet(self._packet)
        self.emit('packet-changed')

