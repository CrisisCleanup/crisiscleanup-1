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
import jinja2
import os
import HTMLParser


# Local libraries.
import base
import page_db


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_edit_pages.html')

GLOBAL_ADMIN_NAME = "Admin"

HTML_PARSER = HTMLParser.HTMLParser()

class AdminEditPagesHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        if not org.name == GLOBAL_ADMIN_NAME:
            self.redirect("/")
            return

        # construct forms from all page blocks
        page_blocks = page_db.get_all_page_blocks()
        forms = page_db.construct_forms(page_blocks)
        
        # render page
        self.response.out.write(template.render(forms=forms))
        
    def AuthenticatedPost(self, org, event):
        if not org.name == GLOBAL_ADMIN_NAME:
            self.redirect("/")
            return

        # save form data received
        block_name = self.request.get('name', None)
        block_html = self.request.get('html', None)
        if block_name and block_html:
            block_html = HTML_PARSER.unescape(block_html)
            page_db.save_page_block(block_name, block_html)
        self.redirect('/admin-edit-pages')
        return

class AdminDownloadPageBlocks(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        if not org.name == GLOBAL_ADMIN_NAME:
            self.redirect("/")
            return

        # create downloadable defaults file
        page_blocks = page_db.get_all_page_blocks()
        s  = "{# PageBlock defaults #}\n"
        s += "{# ================== #}\n\n"
        s += "{# CMS-style PageBlocks are populated with these values as defaults. #}\n\n"
        for block in page_blocks:
            s += "{%% block %s %%}\n" % block.name
            s += block.html.strip() + "\n"
            s += "{% endblock %}\n\n"
        self.response.out.write(s)
        return

