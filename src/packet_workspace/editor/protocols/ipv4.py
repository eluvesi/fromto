# ipv4.py
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
from scapy.all import IP, conf, get_if_addr
from scapy.utils import valid_ip


@Gtk.Template(resource_path=
    '/com/github/eluvesi/FromTo/packet_workspace/editor/protocols/ipv4.ui'
)
class IPv4SettingsGroup(Adw.PreferencesGroup):
    __gtype_name__ = 'IPv4SettingsGroup'

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
    version_spinrow = Gtk.Template.Child()
    version_reset_button = Gtk.Template.Child()
    ihl_spinrow = Gtk.Template.Child()
    ihl_auto_button = Gtk.Template.Child()
    tos_spinrow = Gtk.Template.Child()
    tos_reset_button = Gtk.Template.Child()
    len_spinrow = Gtk.Template.Child()
    len_auto_button = Gtk.Template.Child()
    id_spinrow = Gtk.Template.Child()
    id_reset_button = Gtk.Template.Child()
    flags_r_button = Gtk.Template.Child()
    flags_d_button = Gtk.Template.Child()
    flags_m_button = Gtk.Template.Child()
    frag_spinrow = Gtk.Template.Child()
    frag_reset_button = Gtk.Template.Child()
    ttl_spinrow = Gtk.Template.Child()
    ttl_reset_button = Gtk.Template.Child()
    proto_spinrow = Gtk.Template.Child()
    proto_auto_button = Gtk.Template.Child()
    chksum_spinrow = Gtk.Template.Child()
    chksum_auto_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None
        self._updating = False

        for row, field in (
            (self.src_entryrow, 'src'),
            (self.dst_entryrow, 'dst'),
        ):
            row.connect('changed', self._on_ip_changed, field)

        for row, field in (
            (self.version_spinrow, 'version'),
            (self.ihl_spinrow, 'ihl'),
            (self.tos_spinrow, 'tos'),
            (self.len_spinrow, 'len'),
            (self.id_spinrow, 'id'),
            (self.frag_spinrow, 'frag'),
            (self.ttl_spinrow, 'ttl'),
            (self.proto_spinrow, 'proto'),
            (self.chksum_spinrow, 'chksum'),
        ):
            row.connect('notify::value', self._on_field_changed, field)

        for button, field in (
            (self.src_auto_button, 'src'),
            (self.version_reset_button, 'version'),
            (self.ihl_auto_button, 'ihl'),
            (self.tos_reset_button, 'tos'),
            (self.len_auto_button, 'len'),
            (self.id_reset_button, 'id'),
            (self.frag_reset_button, 'frag'),
            (self.ttl_reset_button, 'ttl'),
            (self.proto_auto_button, 'proto'),
            (self.chksum_auto_button, 'chksum'),
        ):
            button.connect('clicked', self._on_auto, field)

        for button in (
            self.flags_r_button,
            self.flags_d_button,
            self.flags_m_button,
        ):
            button.connect('toggled', self._on_flags_changed)

    def set_packet(self, packet):
        """Display IPv4 fields from the supplied packet."""
        self._packet = packet
        self._updating = True
        try:
            enabled = packet is not None and packet.haslayer(IP)
            self.set_sensitive(enabled)
            if not enabled:
                return

            ip = packet[IP]
            try:
                ip = IP(bytes(ip))
            except Exception:
                pass

            self.src_entryrow.set_text(str(ip.src))
            self.dst_entryrow.set_text(str(ip.dst))

            for row, field in (
                (self.version_spinrow, 'version'),
                (self.ihl_spinrow, 'ihl'),
                (self.tos_spinrow, 'tos'),
                (self.len_spinrow, 'len'),
                (self.id_spinrow, 'id'),
                (self.frag_spinrow, 'frag'),
                (self.ttl_spinrow, 'ttl'),
                (self.proto_spinrow, 'proto'),
                (self.chksum_spinrow, 'chksum'),
            ):
                value = getattr(ip, field)
                row.set_value(value if value is not None else 0)

            flags = int(ip.flags)
            self.flags_r_button.set_active(bool(flags & 4))
            self.flags_d_button.set_active(bool(flags & 2))
            self.flags_m_button.set_active(bool(flags & 1))
        finally:
            self._updating = False

    def _on_ip_changed(self, row, field):
        if self._updating or self._packet is None:
            return

        value = row.get_text().strip()
        if not valid_ip(value):
            return

        self._packet[IP].setfieldval(field, value)
        self.emit('packet-changed')

    def _on_field_changed(self, row, _pspec, field):
        if self._updating or self._packet is None:
            return

        self._packet[IP].setfieldval(field, int(row.get_value()))
        self.emit('packet-changed')

    def _on_flags_changed(self, _button):
        if self._updating or self._packet is None:
            return

        flags = (
            (4 if self.flags_r_button.get_active() else 0)
            | (2 if self.flags_d_button.get_active() else 0)
            | (1 if self.flags_m_button.get_active() else 0)
        )
        self._packet[IP].flags = flags
        self.emit('packet-changed')

    def _on_auto(self, _button, field):
        if self._packet is None or not self._packet.haslayer(IP):
            return

        if field == 'src':
            self._packet[IP].src = get_if_addr(conf.iface)
        else:
            delattr(self._packet[IP], field)

        self.set_packet(self._packet)
        self.emit('packet-changed')

