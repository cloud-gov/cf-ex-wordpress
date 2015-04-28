"""WordPress Extension

Downloads, installs and configures WordPress
"""
import os
import os.path
import logging
from build_pack_utils import utils


_log = logging.getLogger('wordpress')


DEFAULTS = utils.FormattedDict({
    'WORDPRESS_VERSION': '4.2.1',  # or 'latest'
    'WORDPRESS_PACKAGE': 'wordpress-{WORDPRESS_VERSION}.tar.gz',
    'WORDPRESS_HASH': 'c93a39be9911591b19a94743014be3585df0512f',
    'WORDPRESS_URL': 'https://wordpress.org/{WORDPRESS_PACKAGE}'
})


def merge_defaults(ctx):
    for key, val in DEFAULTS.iteritems():
        if key not in ctx:
            ctx[key] = val


# Extension Methods
def preprocess_commands(ctx):
    return ()


def service_commands(ctx):
    return {}


def service_environment(ctx):
    return {}


def compile(install):
    ctx = install.builder._ctx
    merge_defaults(ctx)
    print 'Installing Wordpress %s' % ctx['WORDPRESS_VERSION']
    inst = install._installer
    workDir = os.path.join(ctx['TMPDIR'], 'wordpress')
    inst.install_binary_direct(
        ctx['WORDPRESS_URL'],
        ctx['WORDPRESS_HASH'],
        workDir,
        fileName=ctx['WORDPRESS_PACKAGE'],
        strip=True)
    (install.builder
        .move()
        .everything()
        .under('{BUILD_DIR}/{WEBDIR}')
        .into(workDir)
        .done())
    (install.builder
        .move()
        .everything()
        .under(workDir)
        .into('{BUILD_DIR}/{WEBDIR}')
        .done())
    return 0
