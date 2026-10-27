# icmp.py
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
from scapy.all import ICMP


@Gtk.Template(resource_path=
    '/com/github/eluvesi/FromTo/packet_workspace/editor/protocols/icmp.ui'
)
class ICMPSettingsGroup(Adw.PreferencesGroup):
    __gtype_name__ = 'ICMPSettingsGroup'

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

    type_togglegroup = Gtk.Template.Child()
    code_spinrow = Gtk.Template.Child()
    code_reset_button = Gtk.Template.Child()
    chksum_spinrow = Gtk.Template.Child()
    chksum_auto_button = Gtk.Template.Child()
    id_spinrow = Gtk.Template.Child()
    id_reset_button = Gtk.Template.Child()
    seq_spinrow = Gtk.Template.Child()
    seq_reset_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None
        self._updating = False

        self.type_togglegroup.connect(
            'notify::active-name', self._on_type_changed
        )

        for row, field in (
            (self.code_spinrow, 'code'),
            (self.chksum_spinrow, 'chksum'),
            (self.id_spinrow, 'id'),
            (self.seq_spinrow, 'seq'),
        ):
            row.connect('notify::value', self._on_field_changed, field)

        for button, field in (
            (self.code_reset_button, 'code'),
            (self.chksum_auto_button, 'code'),
            (self.id_reset_button, 'id'),
            (self.seq_reset_button, 'seq'),
        ):
            button.connect('clicked', self._on_auto, field)

    def set_packet(self, packet):
        """Display ICMP fields from the supplied packet."""
        self._packet = packet
        self._updating = True
        try:
            enabled = packet is not None and packet.haslayer(ICMP)
            self.set_sensitive(enabled)
            if not enabled:
                return

            icmp = packet[ICMP]
            try:
                icmp = ICMP(bytes(icmp))
            except Exception:
                pass

            self.type_togglegroup.set_active_name(
                {
                    8: 'echo-request',
                    0: 'echo-reply',
                }.get(int(icmp.type), None)
            )

            for row, field in (
                (self.code_spinrow, 'code'),
                (self.chksum_spinrow, 'chksum'),
                (self.id_spinrow, 'id'),
                (self.seq_spinrow, 'seq'),
            ):
                value = getattr(icmp, field)
                row.set_value(value if value is not None else 0)
        finally:
            self._updating = False

    def _on_type_changed(self, group, _pspec):
        if self._updating or self._packet is None:
            return

        icmp_type = {
            'echo-request': 8,
            'echo-reply': 0,
        }.get(group.get_active_name())

        if icmp_type is None:
            return

        self._packet[ICMP].type = icmp_type
        self.emit('packet-changed')

    def _on_field_changed(self, row, _pspec, field):
        if self._updating or self._packet is None:
            return

        self._packet[ICMP].setfieldval(field, int(row.get_value()))
        self.emit('packet-changed')

    def _on_auto(self, _button, field):
        if self._packet is None or not self._packet.haslayer(ICMP):
            return

        delattr(self._packet[ICMP], field)
        self.set_packet(self._packet)
        self.emit('packet-changed')

