# packet_workspace.py
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

from .preview_page import PreviewPage


@Gtk.Template(resource_path='/com/github/eluvesi/FromTo/packet-workspace.ui')
class PacketWorkspace(Gtk.Box):
    __gtype_name__ = 'PacketWorkspace'

    __gsignals__ = {
        'toast-requested': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (str,),
        ),
    }

    editor_page = Gtk.Template.Child()
    preview_page = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._packet = None

        self.preview_page.connect(
            'toast-requested', self._on_toast_requested
        )

    @property
    def packet(self):
        """The packet currently displayed by the workspace."""
        return self._packet

    def set_packet(self, packet):
        """Set the packet displayed by the workspace."""
        self._packet = packet
        # EditPage will be added here when its widget is implemented.
        self.preview_page.set_packet(packet)

    def refresh(self):
        """Refresh page representations after the packet has changed."""
        # EditPage will be added here when its widget is implemented.
        self.preview_page.refresh()

    def _on_toast_requested(self, _source, message):
        """Forward toast requests from workspace pages."""
        self.emit('toast-requested', message)

