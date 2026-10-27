# tcp.py
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
from scapy.all import TCP


@Gtk.Template(resource_path=
    '/com/github/eluvesi/FromTo/packet_workspace/editor/protocols/tcp.ui'
)
class TCPSettingsGroup(Adw.PreferencesGroup):
    __gtype_name__ = 'TCPSettingsGroup'

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
    seq_spinrow = Gtk.Template.Child()
    seq_reset_button = Gtk.Template.Child()
    ack_spinrow = Gtk.Template.Child()
    ack_reset_button = Gtk.Template.Child()
    dataofs_spinrow = Gtk.Template.Child()
    dataofs_auto_button = Gtk.Template.Child()

    reserved_2_button = Gtk.Template.Child()
    reserved_1_button = Gtk.Template.Child()
    reserved_0_button = Gtk.Template.Child()

    flag_ns_button = Gtk.Template.Child()
    flag_cwr_button = Gtk.Template.Child()
    flag_ece_button = Gtk.Template.Child()
    flag_urg_button = Gtk.Template.Child()
    flag_ack_button = Gtk.Template.Child()
    flag_psh_button = Gtk.Template.Child()
    flag_rst_button = Gtk.Template.Child()
    flag_syn_button = Gtk.Template.Child()
    flag_fin_button = Gtk.Template.Child()

    window_spinrow = Gtk.Template.Child()
    window_reset_button = Gtk.Template.Child()
    chksum_spinrow = Gtk.Template.Child()
    chksum_auto_button = Gtk.Template.Child()
    urgptr_spinrow = Gtk.Template.Child()
    urgptr_reset_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None
        self._updating = False

        for row, field in (
            (self.sport_spinrow, 'sport'),
            (self.dport_spinrow, 'dport'),
            (self.seq_spinrow, 'seq'),
            (self.ack_spinrow, 'ack'),
            (self.dataofs_spinrow, 'dataofs'),
            (self.window_spinrow, 'window'),
            (self.chksum_spinrow, 'chksum'),
            (self.urgptr_spinrow, 'urgptr'),
        ):
            row.connect('notify::value', self._on_field_changed, field)

        for button, field in (
            (self.sport_reset_button, 'sport'),
            (self.dport_reset_button, 'dport'),
            (self.seq_reset_button, 'seq'),
            (self.ack_reset_button, 'ack'),
            (self.dataofs_auto_button, 'dataofs'),
            (self.window_reset_button, 'dataofs'),
            (self.chksum_auto_button, 'chksum'),
            (self.urgptr_reset_button, 'urgptr'),
        ):
            button.connect('clicked', self._on_auto, field)

        for button in (
            self.reserved_2_button,
            self.reserved_1_button,
            self.reserved_0_button,
        ):
            button.connect('toggled', self._on_reserved_changed)

        for button in (
            self.flag_ns_button,
            self.flag_cwr_button,
            self.flag_ece_button,
            self.flag_urg_button,
            self.flag_ack_button,
            self.flag_psh_button,
            self.flag_rst_button,
            self.flag_syn_button,
            self.flag_fin_button,
        ):
            button.connect('toggled', self._on_flag_changed)

    def set_packet(self, packet):
        """Display TCP fields from the supplied packet."""
        self._packet = packet
        self._updating = True

        try:
            enabled = packet is not None and packet.haslayer(TCP)
            self.set_sensitive(enabled)

            if not enabled:
                return

            tcp = packet[TCP]
            try:
                tcp = TCP(bytes(tcp))
            except Exception:
                pass

            for row, field in (
                (self.sport_spinrow, 'sport'),
                (self.dport_spinrow, 'dport'),
                (self.seq_spinrow, 'seq'),
                (self.ack_spinrow, 'ack'),
                (self.dataofs_spinrow, 'dataofs'),
                (self.window_spinrow, 'window'),
                (self.chksum_spinrow, 'chksum'),
                (self.urgptr_spinrow, 'urgptr'),
            ):
                value = getattr(tcp, field)
                row.set_value(value if value is not None else 0)

            reserved = int(tcp.reserved)
            self.reserved_2_button.set_active(bool(reserved & 4))
            self.reserved_1_button.set_active(bool(reserved & 2))
            self.reserved_0_button.set_active(bool(reserved & 1))

            for button, flag in (
                (self.flag_ns_button, 'ns'),
                (self.flag_cwr_button, 'cwr'),
                (self.flag_ece_button, 'ece'),
                (self.flag_urg_button, 'urg'),
                (self.flag_ack_button, 'ack'),
                (self.flag_psh_button, 'psh'),
                (self.flag_rst_button, 'rst'),
                (self.flag_syn_button, 'syn'),
                (self.flag_fin_button, 'fin'),
            ):
                button.set_active(flag in tcp.flags)
        finally:
            self._updating = False

    def _on_field_changed(self, row, _pspec, field):
        if self._updating or self._packet is None:
            return

        self._packet[TCP].setfieldval(field, int(row.get_value()))
        self.emit('packet-changed')

    def _on_reserved_changed(self, _button):
        if self._updating or self._packet is None:
            return

        reserved = (
            (4 if self.reserved_2_button.get_active() else 0)
            | (2 if self.reserved_1_button.get_active() else 0)
            | (1 if self.reserved_0_button.get_active() else 0)
        )
        self._packet[TCP].reserved = reserved
        self.emit('packet-changed')

    def _on_flag_changed(self, _button):
        if self._updating or self._packet is None:
            return

        flags = (
            (256 if self.flag_ns_button.get_active() else 0)
            | (128 if self.flag_cwr_button.get_active() else 0)
            | (64 if self.flag_ece_button.get_active() else 0)
            | (32 if self.flag_urg_button.get_active() else 0)
            | (16 if self.flag_ack_button.get_active() else 0)
            | (8 if self.flag_psh_button.get_active() else 0)
            | (4 if self.flag_rst_button.get_active() else 0)
            | (2 if self.flag_syn_button.get_active() else 0)
            | (1 if self.flag_fin_button.get_active() else 0)
        )
        self._packet[TCP].flags = flags
        self.emit('packet-changed')

    def _on_auto(self, _button, field):
        if self._packet is None or not self._packet.haslayer(TCP):
            return

        delattr(self._packet[TCP], field)
        self.set_packet(self._packet)
        self.emit('packet-changed')

