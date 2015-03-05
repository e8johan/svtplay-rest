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

import pickle
import datetime

import urllib
import urllib2
import htmlentitydefs
from HTMLParser import HTMLParser

from flask import Flask, jsonify, abort

class SvtPlayParser(HTMLParser):
    """
        Parser for the programs page of SVTPlay.
        
        This is used to collect a list of Show instances.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        
        self.__shows = {}
        self.__lastRequest = datetime.datetime(2000, 1, 1)
        
    def maybeParse(self):
        if (datetime.datetime.utcnow() - self.__lastRequest).seconds > 3600:
            self.__lastRequest = datetime.datetime.utcnow()
            self.parse()

    def parse(self):
        response = urllib2.urlopen('http://svtplay.se/program')
        encoding = response.headers.getparam('charset')
        body = response.read().decode(encoding)

        self.feed(body)

    def serialize(self):
        showmap = {}
        for s in self.__shows.keys():
            showmap[s] = self.__shows[s].serialize()
            
        return {'lastUpdateIndex': Episode.lastUpdateIndex, 'shows': showmap}
    
    def deserialize(self, data):
        self.__shows = {}
        for s in data['shows'].keys():
            show = Show()
            show.deserialize(data['shows'][s])
            self.__shows[s] = show
            
        Episode.lastUpdateIndex = data['lastUpdateIndex']

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'play_alphabetic-list__video-link':
                    s = Show(attrs)
                    if not s.urlBase() in self.__shows.keys():
                        self.__shows[s.urlBase()] = s;

    def shows(self):
        self.maybeParse()
        return self.__shows.values()
    
    def show(self, id):
        self.maybeParse()
        return self.__shows[id]
    
    def json(self):
        self.maybeParse()
        shows = self.__shows.keys()
        res = []
        for s in shows:
            res.append({'name': self.__shows[s].name(), 'unique-name': self.__shows[s].urlBase(), 'site-url': self.__shows[s].url()})

        return jsonify({'shows': res})

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
    def urlBase(self):
        return self.__urlBase

class Show:
    def __init__(self, list=[]):
        self.__name = ''
        self.__urlBase = ''
        self.__episodes = {}
        self.__lastRequest = datetime.datetime(2000, 1, 1)
        
        for item in list:
            if item[0] == 'title':
                self.__name = item[1]
            elif item[0] == 'href':
                self.__urlBase = item[1]
    
    def maybeParse(self):
        if len(self.__episodes) == 0 or (datetime.datetime.utcnow() - self.__lastRequest).seconds > 3600:
            self.__lastRequest = datetime.datetime.utcnow()

            parser = SvtEpisodeParser(self.url(), self.__urlBase)
            parser.parse()
        
            for e in parser.episodes():
                if not e in self.__episodes.keys():
                    parser = SvtEpisodeParser('http://svtplay.se' + e, self.__urlBase)
                    parser.parse()
                    self.__episodes[e] = Episode(parser.title(), parser.subTitle(), e)
    
    def serialize(self):
        episodemap = {}
        for e in self.__episodes.keys():
            episodemap[e] = self.__episodes[e].serialize()
            
        return {'name': self.__name, 'urlBase': self.__urlBase, 'episodes': episodemap}
    
    def deserialize(self, data):
        self.__name = data['name']
        self.__urlBase = data['urlBase']
        self.__episodes = {}
        for e in data['episodes'].keys():
            episode = Episode()
            episode.deserialize(data['episodes'][e])
            self.__episodes[e] = episode
    
    def name(self):
        return self.__name
    
    def url(self):
        return 'http://svtplay.se' + self.__urlBase
    
    def urlBase(self):
        return self.__urlBase;
    
    def episodes(self):
        self.maybeParse()
        return self.__episodes.values()
    
    def episode(self, uniqueName):
        un = '/' + uniqueName + '/'
        es = [e for e in self.__episodes.keys() if e.find(un) != -1]
        if len(es) == 1:
            return self.__episodes[es[0]]
        else:
            raise KeyError
    
    def json(self):
        self.maybeParse()
        es = []
        for e in self.__episodes.keys():
            jm = self.__episodes[e].jsonmap()
            jm['unique-name'] = '/' + e.split('/')[2]
            es.append(jm)
        return jsonify({'name': self.name(), 'site-url': self.url(), 'episodes': es})
    
class Episode:
    lastUpdateIndex = 1 # Serialize by SvtPlayParser
    
    def __init__(self, title='', subTitle='', urlBase=''):
        self.__title = title
        self.__subTitle = subTitle
        self.__urlBase = urlBase
        
        if not urlBase == '':
            Episode.lastUpdateIndex = Episode.lastUpdateIndex + 1
            self.__updateIndex = Episode.lastUpdateIndex
        else:
            self.__updateIndex = 0

    def serialize(self):
        return {'title': self.__title, 'subTitle': self.__subTitle, 'urlBase': self.__urlBase, 'updateIndex': self.__updateIndex}

    def deserialize(self, data):
        self.__title = data['title']
        self.__subTitle = data['subTitle']
        self.__urlBase = data['urlBase']
        self.__updateIndex = data['updateIndex']

    def title(self):
        return self.__title
    def subTitle(self):
        return self.__subTitle
    def url(self):
        return 'http://svtplay.se' + self.__urlBase
    def updateIndex(self):
        return self.__updateIndex
    
    def jsonmap(self):
        return {'title': self.title(), 'sub-title': self.subTitle(), 'update-index': self.__updateIndex, 'site-url': self.url(), 'stream-url': 'http://pirateplay.se:80/api/get_streams.js?' + urllib.urlencode({'url': self.url()})}
    
    def json(self):
        return jsonify(self.jsonmap())

# Create Flash server
app = Flask(__name__)

# Create SVT Play parser and pre-populate cache
parser = SvtPlayParser()
try:
    parser.deserialize(pickle.load(open('shows.p', 'rb')))
except IOError:
    pass

# Flask routes
@app.route('/shows', methods=['GET'])
def getShows():
    try:
        j = parser.json()
        pickle.dump(parser.serialize(), open('shows.p', 'wb'))
        return j
    except:
        abort(500)

@app.route('/shows/<string:id>', methods=['GET'])
def getShow(id):
    try:
        j = parser.show('/' + id).json()
        pickle.dump(parser.serialize(), open('shows.p', 'wb'))
        return j
    except KeyError:
        abort(404)
    except:
        abort(500)

@app.route('/shows/<string:showId>/<string:streamId>', methods=['GET'])
def getShowStream(showId, streamId):
    try:
        s = parser.show('/' + showId)
        e = s.episode(streamId)
        j = e.json()
        pickle.dump(parser.serialize(), open('shows.p', 'wb'))
        return j
    except KeyError:
        abort(404)
    except:
        abort(500)

# Run the server
if __name__ == '__main__':    
    app.run(debug=True)

# The following snippet parses all of SVT Play and persists the results
#    for s in parser.shows():
#        print s.name()
#        s.episodes():
#    pickle.dump(parser.serialize(), open('shows.p', 'wb'))
