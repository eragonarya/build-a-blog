#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape=True)

def get_posts(limit, offset):
    blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT " + str(limit) + " OFFSET " + str(offset))
    return blogs

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a,**kw)

    def render_str(self,template,**params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self,template, **kw):
        self.write(self.render_str(template,**kw))

class Blog(db.Model):
        title = db.StringProperty(required = True)
        blog = db.TextProperty(required = True)
        created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self,title='',blog='',error='',link=''):
        cpage = 0
        if self.request.get('page')=='' or int(self.request.get('page')) <= 0:
            cpage = 1
        else:
            cpage = int(self.request.get('page'))
        offset = (cpage-1)*5
        nextPage = cpage + 1
        maxPages = get_posts(5,offset).count()//5+1
        if maxPages % 5 == 0:
            maxPages -= 1
        if maxPages < nextPage:
            nextPage = -1

        self.render("blog.html",title=title,blog=blog,error=error, blogs=get_posts(5,offset), npage=nextPage,ppage=cpage-1)
    def get(self):
        self.render_front()

class Submit(Handler):
    def render_front(self,title='',blog='',error='',link=''):
        self.render("submission.html",title=title,blog=blog, error=error)
    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get('title')
        blog = self.request.get('blog')
        if title and blog:
            b = Blog(title = title, blog = blog)
            b.put()
            link = b.key().id()
            self.redirect("/blog/"+str(link))
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title,blog,error)
class ViewPostHandler(Handler):
    def render_front(self,title='',blog='',error=''):
        self.render("individualblog.html",title=title,blog=blog,error=error)
    def get(self, id):
        blogid = Blog.get_by_id(int(id))
        self.render_front(title=blogid,blog=blogid)


app = webapp2.WSGIApplication([('/',MainPage),('/blog',MainPage),('/newpost',Submit),webapp2.Route('/blog/<id:\d+>',ViewPostHandler)], debug = True)
