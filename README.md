SVTPlay REST

This provides a REST interface to traverse the available shows and episodes 
provided by SVTPlay.

You can access it using the following paths:

- host:port/shows, returns a JSON containing the following keys

    {<br />
      "shows": [ <-- outer key, containing a list of shows<br />
        {<br />
          "name": "SVT G\u00e4vleborg", <-- name of the show<br />
          "site-url": "http://svtplay.se/svt-gavleborg", <-- URL to the show at svtplay.se<br />
          "unique-name": "/svt-gavleborg" <-- /show-id, simply add this to the query path for details<br />
        }, <br />
    ... ]<br />
    }

- host:port/shows/show-id, returns a JSON containing the following keys

    {<br />
      "name": "SVT G\u00e4vleborg", <-- name of the show<br />
      "site-url": "http://svtplay.se/svt-gavleborg", <-- URL to the show at svtplay.se<br />
      "episodes": [ <-- list of episodes<br />
        {<br />
          "site-url": "http://svtplay.se/video/2719584/svt-gavleborg/svt-gavleborg-2-3-19-15", <-- URL to the episode at svtplay.se<br />
          "stream-url": "http://pirateplay.se:80/api/get_streams.js?url=http%3A%2F%2Fsvtplay.se%2Fvideo%2F2719584%2Fsvt-gavleborg%2Fsvt-gavleborg-2-3-19-15", <-- URL to API request to pirateplay.se<br />
          "sub-title": "2/3 19.15", <-- episode identification<br />
          "title": "SVT G\u00e4vleborg" <-- episode title<br />
          "unique-name": "/2719584" <-- unique name, simply add this to the query path for details<br />
        }, <br />
    ... ]<br />
    }

- host:port/shows/show-id/episode-id, returns a JSON containing the following keys (the same as above)

    {<br />
      "site-url": "http://svtplay.se/video/2719584/svt-gavleborg/svt-gavleborg-2-3-19-15", <br />
      "stream-url": "http://pirateplay.se:80/api/get_streams.js?url=http%3A%2F%2Fsvtplay.se%2Fvideo%2F2719584%2Fsvt-gavleborg%2Fsvt-gavleborg-2-3-19-15", <br />
      "sub-title": "2/3 19.15", <br />
      "title": "SVT G\u00e4vleborg"<br />
    }

Right now there are some outstanding issues, and room for improvement, but the general setup works now.