#!/usr//bin/env python
# coding=UTF-8
#
#    SVTPlay REST - A REST interface for traversing SVTPlay
#    Copyright (C) 2015 Johan Thelin
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import urllib2
import htmlentitydefs
from HTMLParser import HTMLParser

class SvtPlayParser(HTMLParser):
    """
        Parser for the programs page of SVTPlay.
        
        This is used to collect a list of Show instances.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        
        self.__shows = []
        
    def parse(self):
        response = urllib2.urlopen('http://svtplay.se/program')
        encoding = response.headers.getparam('charset')
        body = response.read().decode(encoding)

        self.feed(body)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'play_alphabetic-list__video-link':
                    self.__shows.append(Show(attrs))

    def shows(self):
        return self.__shows

class SvtEpisodeParser(HTMLParser):
    """
        Parser for episode pages of SVTPlay.
        
        This is used by a Show instance when more information is requested.
        
        Calls to methods of this class may result in http requests, so be prepared to wait.
        
        The result is a collection of Episode instances.
    """
    def __init__(self, url, urlBase):
        HTMLParser.__init__(self)
        self.__url = url
        self.__urlBase = urlBase
        self.__inTitle = False
        self.__inSubTitle = False

        self.__title = ''
        self.__subTitle = ''
        self.__episodes = []

    def parse(self):
        response = urllib2.urlopen(self.__url)
        encoding = response.headers.getparam('charset')
        body = response.read().decode(encoding)
        self.feed(body)
    
    def handle_starttag(self, tag, attrs):
        self.__inTitle = False
        self.__inSubTitle = False
        
        if tag == 'a':
            hasClass = False
            href = ''
            
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'play_js-video-link playJsGridItem play_js-videolist-element-link play_videolist-element__link':
                    hasClass = True
                elif attr[0] == 'href' and attr[1].find(self.__urlBase) >= 0:
                    href = attr[1]
            
            if hasClass and href != '':
                self.__episodes.append(href)
        elif tag == 'h1':
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'play_video-area-aside__title':
                    self.__inTitle = True
        elif tag == 'h2':
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'play_video-area-aside__sub-title':
                    self.__inSubTitle = True

    def handle_entityref(self, name):
        self.handle_data(unichr(htmlentitydefs.name2codepoint[name]))
    
    def handle_charref(self, name):
        print "UNHANDLED CHARREF", name
        self.handle_data("CHARREF" + name) 

    def handle_data(self, data):
        if self.__inTitle:
            self.__title = self.__title + unicode(" ".join(data.split()))
        elif self.__inSubTitle:
            self.__subTitle = self.__subTitle + unicode(" ".join(data.split()))

    def episodes(self):
        return self.__episodes
    def title(self):
        return self.__title
    def subTitle(self):
        return self.__subTitle

class Show:
    def __init__(self, list):
        self.__name = ''
        self.__canMobile = False
        self.__canInternational = False
        self.__urlBase = ''
        self.__episodes = []
        
        for item in list:
            if item[0] == 'title':
                self.__name = item[1]
            elif item[0] == 'href':
                self.__urlBase = item[1]
            elif item[0] == 'data-mobile':
                if item[1] == 'true':
                    self.__canMobile = True
            elif item[0] == 'data-abroad':
                if item[1] == 'true':
                    self.__canInternational = True
    
    def name(self):
        return self.__name
    
    def canMobile(self):
        return self.__canMobile

    def canInternational(self):
        return self.__canInternational

    def url(self):
        return 'http://svtplay.se' + self.__urlBase
    
    def episodes(self):
        if len(self.__episodes) == 0:
            parser = SvtEpisodeParser(self.url(), self.__urlBase)
            parser.parse()
        
            for e in parser.episodes():
                parser = SvtEpisodeParser('http://svtplay.se' + e, self.__urlBase)
                parser.parse()
                self.__episodes.append(Episode(parser.title(), parser.subTitle(), e))

        return self.__episodes
    
class Episode:
    def __init__(self, title, subTitle, urlBase):
        self.__title = title
        self.__subTitle = subTitle
        self.__urlBase = urlBase

    def title(self):
        return self.__title
    def subTitle(self):
        return self.__subTitle
    def url(self):
        return 'http://svtplay.se' + self.__urlBase

parser = SvtPlayParser()
parser.parse()

for s in parser.shows():
    print s.name(), s.url()
    for e in s.episodes():
        print "    ", e.title(), e.subTitle(), e.url()
    print "    count:", len(s.episodes())

print "count:", len(parser.shows())