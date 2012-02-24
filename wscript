import glob
import Options
import Utils
import os

srcdir = '.'
blddir = 'build'
VERSION = '0.0.1'

def set_options(opt):
  opt.tool_options('compiler_cxx')
  opt.add_option('--profile', action='store_true', help='Enable profiling', dest='profile', default=False)

def configure(conf):
  o = Options.options
  conf.env['USE_PROFILING'] = o.profile
  conf.check_tool('compiler_cxx')
  conf.check_tool('node_addon')
  conf.env.append_value('CPPFLAGS', '-DNDEBUG')

  if conf.check(lib='gif', libpath=['/lib', '/usr/lib', '/usr/local/lib', '/opt/local/lib'], uselib_store='GIF', mandatory=False):
    conf.env.append_value('CPPFLAGS', '-DHAVE_GIF=1')

  if conf.check(lib='jpeg', libpath=['/lib', '/usr/lib', '/usr/local/lib', '/opt/local/lib'], uselib_store='JPEG', mandatory=False):
    conf.env.append_value('CPPFLAGS', '-DHAVE_JPEG=1')

  if conf.env['USE_PROFILING'] == True:
    conf.env.append_value('CXXFLAGS', ['-pg'])
    conf.env.append_value('LINKFLAGS', ['-pg'])

  # Some hackery to allow pre-compiled cairo binaries to be supplied for
  # platforms where it is necessary to do so
  cairo_libpath = ['/lib', '/usr/lib', '/usr/local/lib', '/opt/local/lib', '/usr/X11/lib']

  sysname, nodename, release, version, machine = os.uname()
  libcairo_overrides = os.path.join(conf.cwd, 'cairo', sysname, nodename, machine)

  libcairo_path = os.path.join(libcairo_overrides, 'lib')
  libcairo_include = os.path.join(libcairo_overrides, 'include')
  libcairo_pkgconfig = os.path.join(libcairo_overrides, 'pkgconfig')

  if os.path.lexists(libcairo_path):
    cairo_libpath.append(libcairo_path)

  if os.path.lexists(libcairo_include):
    conf.env.CAIRO_INCLUDES = libcairo_include

  conf.check_cxx(lib=['cairo', 'pixman-1'], libpath=cairo_libpath, uselib_store='CAIRO', mandatory=True)
  if os.path.lexists(libcairo_pkgconfig):
    pkgconfig = 'PKG_CONFIG_PATH=%s pkg-config' % libcairo_pkgconfig
    conf.check_cfg(package=os.path.join(libcairo_pkgconfig, 'cairo.pc'), args='--cflags --libs', mandatory=True, path=pkgconfig)
  else:
    conf.check_cfg(package='cairo', args='--cflags --libs', mandatory=True)

  flags = ['-O3', '-Wall', '-D_FILE_OFFSET_BITS=64', '-D_LARGEFILE_SOURCE']
  conf.env.append_value('CCFLAGS', flags)
  conf.env.append_value('CXXFLAGS', flags)

def build(bld):
  obj = bld.new_task_gen('cxx', 'shlib', 'node_addon')
  obj.target = 'canvas'
  obj.source = bld.glob('src/*.cc')
  obj.uselib = ['CAIRO', 'GIF', 'JPEG', 'PIXMAN']
  if 'CAIRO_INCLUDES' in obj.env:
    obj.includes = obj.env.CAIRO_INCLUDES
