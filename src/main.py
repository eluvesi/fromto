# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import FromtoWindow


class FromtoApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id='com.github.eluvesi.FromTo',
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
            resource_base_path='/com/github/eluvesi/FromTo',
        )

        self.settings = Gio.Settings.new('com.github.eluvesi.FromTo')
        self.settings.connect(
            'changed::color-scheme',
            self._apply_color_scheme,
        )
        self._apply_color_scheme()

        self.create_action(
            'quit',
            lambda *_: self.quit(),
            ['<control>q'],
        )
        self.create_action(
            'preferences',
            self.on_preferences_action,
            ['<control>comma'],
        )
        self.create_action(
            'about',
            self.on_about_action,
        )

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if necessary.
        """
        win = self.props.active_window
        if not win:
            win = FromtoWindow(application=self)
        win.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(
            application_name='From To',
            application_icon='com.github.eluvesi.FromTo',
            developer_name='eluvesi',
            license_type=Gtk.License.GPL_3_0,
            website='https://github.com/eluvesi/fromto',
            version='0.1.0',
            translator_credits = _('translator-credits'),
            developers=['eluvesi https://github.com/eluvesi'],
            designers=['eluvesi https://github.com/eluvesi'],
            copyright='© 2026 eluvesi'
        )
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        if not hasattr(self, 'preferences_dialog'):
            builder = Gtk.Builder.new_from_resource(
                '/com/github/eluvesi/FromTo/preferences-dialog.ui'
            )

            self.preferences_dialog = builder.get_object('preferences_dialog')

            self.settings.bind(
                'color-scheme',
                builder.get_object('color_scheme_togglegroup'),
                'active-name',
                Gio.SettingsBindFlags.DEFAULT,
            )

        self.preferences_dialog.present(self.props.active_window)

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def _apply_color_scheme(self, *args):
        """Apply the saved application color scheme."""
        scheme = self.settings.get_string('color-scheme')

        match scheme:
            case 'light':
                color_scheme = Adw.ColorScheme.FORCE_LIGHT
            case 'dark':
                color_scheme = Adw.ColorScheme.FORCE_DARK
            case _:
                color_scheme = Adw.ColorScheme.DEFAULT

        Adw.StyleManager.get_default().set_color_scheme(color_scheme)


def main(version):
    """The application's entry point."""
    app = FromtoApplication()
    return app.run(sys.argv)

