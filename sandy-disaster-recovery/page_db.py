#!/usr/bin/env python
#
# Copyright 2013 Chris Wood
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# System libraries.
import os
import re
import logging

import jinja2
from google.appengine.ext import db
from google.appengine.api import memcache
from wtforms.ext.appengine.db import model_form
from wtforms import HiddenField


# constants

FILENAMES = ['page.html', 'about.html', 'contact.html']

PAGE_BLOCK_MARKER_CRX = re.compile('[a-z0-9_]+_page_block')

MEMCACHE_DICT_KEY = 'page_block_dict'


# classes

class PageBlock(db.Model):
    name = db.StringProperty(required=True)
    html = db.TextProperty()

class PageBlockForm(model_form(PageBlock)):
    name = HiddenField('name')

def detect_page_blocks():
    """
    Search for page block names in files with FILENAMES.
    """
    for filename in FILENAMES:
        fd = open(filename)
        for block_name in PAGE_BLOCK_MARKER_CRX.findall(fd.read()):
            yield block_name

def get_page_block_default_html(block_name):
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
    defaults_template = jinja_env.get_template('pageblock.defaults.html')
    default_block_fn = defaults_template.blocks.get(block_name, None)
    if default_block_fn:
        return list(default_block_fn(None))[0]
    else:
        return None

def get_all_page_blocks():
    """
    Get all page blocks, creating from defaults as necessary.
    """
    page_blocks = [PageBlock.get_or_insert(name, name=name) for name in detect_page_blocks()]
    for block in page_blocks:
        if not block.html:
            block.html = get_page_block_default_html(block.name)
            block.save()
    return page_blocks

def get_page_block_dict():
    """
    Returns {block_name: html} for all known PageBlocks (memcached).
    """
    cached = memcache.get(MEMCACHE_DICT_KEY)
    if cached is not None:
        return cached
    else:
        page_block_dict = {block.name:block.html for block in get_all_page_blocks()}
        memcache.add(MEMCACHE_DICT_KEY, page_block_dict)
        return page_block_dict

def construct_forms(page_blocks):
    return [PageBlockForm(None, block) for block in page_blocks]

def save_page_block(name, html):
    logging.warn(name)
    if name not in detect_page_blocks():
        return
    block = PageBlock.get_or_insert(name)
    block.html = html
    block.save()
    memcache.delete(MEMCACHE_DICT_KEY)
    


