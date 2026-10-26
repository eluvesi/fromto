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

from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path =
    '/com/github/eluvesi/FromTo/packet_workspace/editor/protocols/udp.ui'
)
class UDPSettingsGroup(Adw.PreferencesGroup):
    __gtype_name__ = 'UDPSettingsGroup'

    sport_spinrow = Gtk.Template.Child()
    sport_restore_button = Gtk.Template.Child()
    dport_spinrow = Gtk.Template.Child()
    dport_restore_button = Gtk.Template.Child()
    len_spinrow = Gtk.Template.Child()
    len_restore_button = Gtk.Template.Child()
    chksum_spinrow = Gtk.Template.Child()
    chksum_restore_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Подключение сигналов и логика UDP.
