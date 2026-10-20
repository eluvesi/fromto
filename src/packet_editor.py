# packet_editor.py
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


from gi.repository import Adw, Gtk


@Gtk.Template(resource_path='/com/github/eluvesi/FromTo/packet_editor.ui')
class PacketEditor(Gtk.Box):
    __gtype_name__ = 'PacketEditor'

    editor_viewstack = Gtk.Template.Child()
    edit_page = Gtk.Template.Child()
    preview_textview = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None

    @property
    def packet(self):
        """The packet currently displayed by the editor."""
        return self._packet

    def set_packet(self, packet):
        """Set the packet displayed by the editor."""
        self._packet = packet

        # Page-specific updates will be implemented separately.
        self._update_edit_page()
        self._update_preview_page()

    def _update_edit_page(self):
        """Update the Edit page from the current packet."""
        # TODO: Populate the protocol editors.
        pass

    def _update_preview_page(self):
        """Update the Preview page from the current packet."""
        # TODO: Generate a hexadecimal dump of the packet.
        pass

