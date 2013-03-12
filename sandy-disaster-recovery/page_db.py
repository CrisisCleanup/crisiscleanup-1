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
import datetime
import re
import logging
import wtforms.ext.dateutil.fields
import wtforms.fields
from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from wtforms.ext.appengine.db import model_form

from wtforms import HiddenField


# constants

FILENAMES = ['page.html', 'about.html', 'contact.html']

PAGE_BLOCK_MARKER_CRX = re.compile('[a-z0-9_]+_page_block')


# classes

class PageBlock(db.Model):
    name = db.StringProperty(required=True)
    html = db.TextProperty(required=True, default="<p>Your HTML here</p>")

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

def get_all_page_blocks():
    return [PageBlock.get_or_insert(name, name=name) for name in detect_page_blocks()]

def get_page_block_html(name):
    block = PageBlock.get_by_key_name(name)
    if block:
        return block.html
    else:
        return None

def get_page_block_dict():
    return {block.name:block.html for block in PageBlock.all()}

def construct_forms(page_blocks):
    return [PageBlockForm(None, block) for block in page_blocks]

def save_page_block(name, html):
    logging.warn(name)
    if name not in detect_page_blocks():
        return
    block = PageBlock.get_or_insert(name)
    block.html = html
    block.save()
    


