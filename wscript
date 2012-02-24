
import glob
import Options
import Utils
import os
import sys

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

  libpath = ['/lib', '/usr/lib', '/usr/local/lib', '/opt/local/lib', '/usr/X11/lib']

  # Some hackery to allow pre-compiled cairo binaries to be supplied for
  # platforms where it is necessary to do so
  sysname, nodename, release, version, machine = os.uname()
  libcairo_overrides = os.path.join(conf.cwd, 'cairo', sysname, nodename, machine)

  libcairo_libpath = os.path.join(libcairo_overrides, 'lib')
  libcairo_include = os.path.join(libcairo_overrides, 'include')
  libcairo_pkgconfig = os.path.join(libcairo_overrides, 'pkgconfig')

  if os.path.lexists(libcairo_libpath):
    libpaths.append(libcairo_libpath)

  if os.path.lexists(libcairo_include):
    conf.env.CAIRO_INCLUDES = libcairo_include
  # End hackery

  conf.check(lib='cairo', libpath=libpath, uselib_store='CAIRO', mandatory=True)
  if os.path.lexists(libcairo_pkgconfig):
    conf.check_cfg(package='cairo', args='--cflags --libs', mandatory=True, path=libcairo_pkgconfig)
  else:
    conf.check_cfg(package='cairo', args='--cflags --libs', mandatory=True)

  flags = ['-O3', '-Wall', '-D_FILE_OFFSET_BITS=64', '-D_LARGEFILE_SOURCE']
  conf.env.append_value('CCFLAGS', flags)
  conf.env.append_value('CXXFLAGS', flags)

def build(bld):
  obj = bld.new_task_gen('cxx', 'shlib', 'node_addon')
  obj.target = 'canvas'
  obj.source = bld.glob('src/*.cc')
  obj.uselib = ['CAIRO', 'GIF', 'JPEG']
