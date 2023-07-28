# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""WordPress Extension

Downloads, installs and configures WordPress
"""
import os
import subprocess
import json
import os.path
import logging
from build_pack_utils import utils


_log = logging.getLogger('wordpress')

def load_json(wordpressDir):
    with open(os.path.join(wordpressDir, 'setup.json')) as data_file:
        data = json.load(data_file)
    return data


# Extension Methods
def preprocess_commands(ctx):
    return []


def service_commands(ctx):
    return {}


def service_environment(ctx):
    return {}

def install_wpcli(workDir):
    print('Installing wp-cli')
    args = ['curl', '-O', 'https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar']
    subprocess.call(args, cwd=workDir)
    args = ['chmod', '+x', 'wp-cli.phar']
    subprocess.call(args, cwd=workDir)

def install_wordpress(ctx, builder, wordpressDir):
    # rewrite a temp copy of php.ini for use by wp-cli
    (builder
        .copy()
        .under('{BUILD_DIR}/php/etc')
        .where_name_is('php.ini')
        .into('TMPDIR')
     .done())
    utils.rewrite_cfgs(os.path.join(ctx['TMPDIR'], 'php.ini'),
                       {'TMPDIR': ctx['TMPDIR'],
                        'HOME': ctx['BUILD_DIR']},
                       delim='@')
    # get path to php config we just created
    phpconfig = os.path.join(ctx['TMPDIR'], 'php.ini')
    # get path to php binary
    phpcmd = os.path.join(ctx['BUILD_DIR'], 'php', 'bin', 'php')
    # set the library path so php can find it's extension
    os.environ['LD_LIBRARY_PATH'] = os.path.join(ctx['BUILD_DIR'], 'php', 'lib')

    print('Installing WordPress')
    setupjson = load_json(wordpressDir)
    if setupjson.has_key('wordpress_version'):
        args = [phpcmd, '-c', phpconfig, 'wp-cli.phar', 'core', 'download', '--version=%s' % setupjson['wordpress_version']]
    else:
        args = [phpcmd, '-c', phpconfig, 'wp-cli.phar', 'core', 'download', '--version=latest']
    subprocess.call(args, cwd=wordpressDir)
    args = [phpcmd, '-c', phpconfig, 'wp-cli.phar', 'core', 'install', '--url=%s' % setupjson['site_info']['url'], '--title=%s' % setupjson['site_info']['title'], '--admin_user=%s' % setupjson['site_info']['admin_user'], '--admin_password=%s' % setupjson['site_info']['admin_password'], '--admin_email=%s' % setupjson['site_info']['admin_email']]
    subprocess.call(args, cwd=wordpressDir)
    if setupjson.has_key('plugins') and len(setupjson['plugins']):
        for plugin in setupjson['plugins']:
          if plugin.has_key('name') and plugin.has_key('version'):
              args = [phpcmd, '-c', phpconfig, 'wp-cli.phar', 'plugin', 'install', '%s' % plugin['name'], '--version=%s' % plugin['version'], '--activate']
          elif plugin.has_key('name'):
              args = [phpcmd, '-c', phpconfig, 'wp-cli.phar', 'plugin', 'install', '%s' % plugin['name'], '--activate']
          elif plugin.has_key('url'):
              args = [phpcmd, '-c', phpconfig, 'wp-cli.phar', 'plugin', 'install', '%s' % plugin['url'], '--activate']
          subprocess.call(args, cwd=wordpressDir)
    if setupjson.has_key('themes') and len(setupjson['themes']):
        for theme in setupjson['themes']:
          if theme.has_key('name') and theme.has_key('version'):
              args = [phpcmd, '-c', phpconfig, 'wp-cli.phar', 'theme', 'install', '%s' % theme['name'], '--version=%s' % theme['version']]
          elif theme.has_key('name'):
              args = [phpcmd, '-c', phpconfig, 'wp-cli.phar', 'theme', 'install', '%s' % theme['name']]
          elif theme.has_key('url'):
              args = [phpcmd, '-c', phpconfig, 'wp-cli.phar', 'theme', 'install', '%s' % theme['url']]
          subprocess.call(args, cwd=wordpressDir)

def compile(install):
    builder = install.builder
    ctx = builder._ctx
    workDir = os.path.join(ctx['TMPDIR'], 'wordpress')
    (builder
        .move()
        .everything()
        .under('{BUILD_DIR}/{WEBDIR}')
        .into(workDir)
        .done())
    install_wpcli(workDir)
    install_wordpress(ctx, builder, workDir)
    (builder
        .move()
        .everything()
        .under(workDir)
        .into('{BUILD_DIR}/{WEBDIR}')
        .done())
    return 0
