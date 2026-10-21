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
    """Display a packet summary, field details, and hexadecimal dump."""

    __gtype_name__ = 'PreviewPage'

    summary_textview = Gtk.Template.Child()
    details_textview = Gtk.Template.Child()
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
        """Set the packet to preview and update all views."""
        self._packet = packet
        self.refresh()

    def refresh(self):
        """Refresh all previews after the packet has been modified."""
        if self._packet is None:
            self._show_empty_state()
            return

        try:
            previews = (
                (self.summary_textview, self._packet.summary()),
                (self.details_textview, self._packet.show2(dump=True)),
                (self.hexdump_textview, hexdump(self._packet, dump=True)),
            )
        except Exception as error:
            message = f'Unable to generate packet preview:\n{error}'
            self._set_all_text(message)
            return

        for textview, text in previews:
            self._set_text(textview, text or '(No data)')

    def _show_empty_state(self):
        """Display a placeholder when no packet is selected."""
        self._set_all_text('Select a packet to preview its contents.')

    def _set_all_text(self, text):
        """Set the same text in all preview fields."""
        self._set_text(self.summary_textview, text)
        self._set_text(self.details_textview, text)
        self._set_text(self.hexdump_textview, text)

    @staticmethod
    def _set_text(textview, text):
        """Replace the contents of a text view's buffer."""
        buffer = textview.get_buffer().set_text(text)

