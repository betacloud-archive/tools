#!/usr/bin/env python

# This file is subject to the terms and conditions defined in file 'LICENSE',
# which is part of this repository.

import os
import shutil
from subprocess import call
from urlparse import urlparse

from oslo_config import cfg
from oslo_log import log
import requests
import shade
import yaml

NAME = 'image-manager'
CONF = cfg.CONF
LOG = log.getLogger(NAME)

opts = [
    cfg.StrOpt('cloud',
               help='Managed cloud',
               default='service'),
    cfg.StrOpt('imagefile', default='images.yml',
               help='Image file'),
    cfg.StrOpt('tmppath', default='/tmp',
               help='Temp directory for downloads')
]
CONF.register_cli_opts(opts)


def load_images_from_file(imagefile):
    return yaml.load(open(imagefile))


def show(cloud):
    print(cloud.list_images())


def download_image(destpath, url):
    LOG.info("downloading %s" % url)
    r = requests.get(url, stream=True, allow_redirects=True)

    disassembled = urlparse(r.url)
    destfile = os.path.join(destpath, os.path.basename(disassembled.path))

    LOG.info("saving image to %s" % destfile)
    with open(destfile, 'wb') as fp:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, fp)

    return destfile


def convert_image(imagefile, format):
    LOG.info("converting %s from %s to raw" % (imagefile, format))
    destfile = "%s.raw" % imagefile
    call(["qemu-img", "convert", "-f", format, "-O", "raw", imagefile, destfile])
    return destfile


def upload(cloud):
    images = load_images_from_file(CONF.imagefile)
    for image in images:
        result = cloud.get_image(image['name'])

        if result:
            LOG.info(result)
            continue

        imagefile = download_image(CONF.tmppath, image['url'])
        rawfile = convert_image(imagefile, image['format'])

        cloud.create_image(
             name=image['name'],
             filename=rawfile,
             disk_format='raw',
             container_format='bare',
             is_public=image['public']
        )

        properties = {
            'architecture': 'x86_64',
            'os_version': image['version'],
            'os_distro': image['distro'],
#            'hw_vif_multiqueue_enabled': True
        }

        cloud.update_image_properties(
            name_or_id=image['name'],
            **properties
        )


def add_command_parsers(subparsers):
    parser = subparsers.add_parser('show')
    parser.set_defaults(func=show)

    parser = subparsers.add_parser('upload')
    parser.set_defaults(func=upload)


commands = cfg.SubCommandOpt('command', title='Commands',
                             help='Show available commands.',
                             handler=add_command_parsers)
CONF.register_cli_opts([commands])

if __name__ == '__main__':
    log.register_options(CONF)
    log.set_defaults()
    log.setup(CONF, NAME)
    CONF(project=NAME)
    shade.simple_logging(debug=True)
    cloud = shade.openstack_cloud(cloud=CONF.cloud)
    CONF.command.func(cloud)
