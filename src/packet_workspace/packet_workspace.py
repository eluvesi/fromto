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

from .editor_page import EditorPage
from .preview_page import PreviewPage


@Gtk.Template(
    resource_path =
    '/com/github/eluvesi/FromTo/packet_workspace/packet-workspace.ui'
)
class PacketWorkspace(Gtk.Box):
    __gtype_name__ = 'PacketWorkspace'

    __gsignals__ = {
        'toast-requested': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (str,),
        ),
        'apply-packet': (
            GObject.SignalFlags.RUN_LAST,
            GObject.TYPE_BOOLEAN,
            (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT),
        ),
    }

    editor_page = Gtk.Template.Child()
    preview_page = Gtk.Template.Child()
    apply_button = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()
    changes_revealer = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._original_packet = None
        self._working_packet = None
        self._has_changes = False

        self.apply_button.connect(
            'clicked', self._on_apply
        )
        self.cancel_button.connect(
            'clicked', self._on_cancel
        )
        self.editor_page.connect(
            'packet-changed', self._on_packet_changed
        )
        self.editor_page.connect(
            'toast-requested', self._on_toast_requested
        )
        self.preview_page.connect(
            'toast-requested', self._on_toast_requested
        )

    @property
    def packet(self):
        """Return the packet being edited."""
        return self._working_packet

    def set_packet(self, packet):
        """Load a packet and create a working copy."""
        self._original_packet = packet
        self._working_packet = packet.copy() if packet is not None else None
        self._has_changes = False

        self.editor_page.set_packet(self._working_packet)
        self.preview_page.set_packet(self._working_packet)

        self._update_actions()

    def _on_packet_changed(self, _editor):
        """Handle edits made in EditorPage."""
        if self._working_packet is None:
            return

        self._has_changes = True
        self.preview_page.refresh()
        self._update_actions()

    def _on_apply(self, _button):
        """Commit changes to PacketList."""
        if self._working_packet is None or not self._has_changes:
            return

        if not self.emit(
            'apply-packet', self._original_packet, self._working_packet
        ):
            self.emit(
                'toast-requested',
                _('Could not apply changes: packet no longer exists.'),
            )
            return

        # Start a new editing session using a fresh working copy
        self.set_packet(self._working_packet)

    def _on_cancel(self, _button):
        """Discard changes and restore the original packet."""
        if self._original_packet is None:
            return

        # Start a new editing session using an original packet
        self.set_packet(self._original_packet)

    def _update_actions(self):
        """Update the visibility and sensitivity of action buttons."""
        visible = self._working_packet is not None and self._has_changes
        self.changes_revealer.set_reveal_child(visible)
        self.apply_button.set_sensitive(visible)
        self.cancel_button.set_sensitive(visible)

    def _on_toast_requested(self, _source, message):
        """Forward toast requests from workspace pages."""
        self.emit('toast-requested', message)

