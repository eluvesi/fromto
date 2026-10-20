# preview_page.py
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

from scapy.all import hexdump


@Gtk.Template(resource_path='/com/github/eluvesi/FromTo/preview_page.ui')
class PreviewPage(Gtk.Box):
    __gtype_name__ = 'PreviewPage'

    hexdump_textview = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None
        self._show_empty_state()

    @property
    def packet(self):
        """The packet currently displayed by the preview."""
        return self._packet

    def set_packet(self, packet):
        """Set the packet to preview and update the displayed dump."""
        self._packet = packet
        self.refresh()

    def refresh(self):
        """Refresh the dump after the packet has been modified."""
        if self._packet is None:
            self._show_empty_state()
            return

        try:
            dump = hexdump(self._packet, dump=True)
        except Exception as error:
            self._set_text(f'Unable to generate packet preview:\n{error}')
            return

        self._set_text(dump or '(Empty packet)')

    def _show_empty_state(self):
        self._set_text('Select a packet to preview its bytes.')

    def _set_text(self, text):
        buffer = self.hexdump_textview.get_buffer()
        buffer.set_text(text)


