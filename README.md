# From To

[![GNU GPL v3.0 or later](https://img.shields.io/badge/GNU_GPL_3.0_or_later-bd0000?logo=gplv3&logoColor=ffffff)](COPYING)
[![Made for GNOME](https://img.shields.io/badge/Made_for_GNOME-3584e4?logo=gnome&logoColor=ffffff)](https://www.gnome.org/)
[![Please do not theme this app](https://stopthemingmy.app/badge.svg)](https://stopthemingmy.app)

![From To Icon](./data/icons/hicolor/scalable/apps/com.github.eluvesi.FromTo.svg)

From To is a network packet crafting tool for creating, editing, and sending custom packets.

It lets you configure Ethernet, IPv4, TCP, UDP, and ICMP headers, inspect packets in hexadecimal form, and send them through a selected network interface.

Built with GTK and libadwaita, From To follows GNOME design philosophy and integrates naturally with the GNOME desktop.


## Screenshots

![Screenshot](./data/screenshots/main.png)


## Building

From To uses [Meson](https://mesonbuild.com/) as its build system and [Ninja](https://ninja-build.org/) as its build backend.

Before building, make sure the required build tools and application dependencies are installed. For example, on Fedora, you can install them with:

```
sudo dnf install python3 meson ninja-build gtk4 glib2-devel python3-gobject python3-scapy
```

Package names and installation commands may differ on other distributions.

1. Clone the repository and navigate to the project directory:

   ```
   git clone https://github.com/eluvesi/fromto.git
   cd fromto
   ```

2. Configure and build the application:

   ```
   meson setup build
   meson compile -C build
   ```

3. Install the application:

   ```
   sudo meson install -C build
   ```

   To uninstall the application, run:

   ```
   sudo ninja uninstall -C build
   ```

