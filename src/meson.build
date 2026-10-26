pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'fromto'
gnome = import('gnome')

gnome.compile_resources('fromto',
  'fromto.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'fromto.in',
  output: 'fromto',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

fromto_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'packet_list/packet_list.py',
  'packet_list/packet_row.py',
  'packet_workspace/packet_workspace.py',
  'packet_workspace/editor/editor_page.py',
  'packet_workspace/editor/protocols/ethernet.py',
  'packet_workspace/editor/protocols/ipv4.py',
  'packet_workspace/editor/protocols/icmp.py',
  'packet_workspace/editor/protocols/tcp.py',
  'packet_workspace/editor/protocols/udp.py',
  'packet_workspace/preview/preview_page.py',
]

install_data(fromto_sources, install_dir: moduledir)
