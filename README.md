SVTPlay REST

This provides a REST interface to traverse the available shows and episodes 
provided by SVTPlay.

You can access it using the following paths:

- host:port/shows, returns a JSON containing the following keys


```JSON
{
    "shows": [ <-- outer key, containing a list of shows
    {
        "name": "SVT G\u00e4vleborg", <-- name of the show
        "site-url": "http://svtplay.se/svt-gavleborg", <-- URL to the show at svtplay.se
        "unique-name": "/svt-gavleborg" <-- /show-id, simply add this to the query path for details
    }, 
... ]
}
```

- host:port/shows/show-id, returns a JSON containing the following keys

```JSON
{
    "name": "SVT G\u00e4vleborg", <-- name of the show
    "site-url": "http://svtplay.se/svt-gavleborg", <-- URL to the show at svtplay.se
    "episodes": [ <-- list of episodes
    {
        "site-url": "http://svtplay.se/video/2719584/svt-gavleborg/svt-gavleborg-2-3-19-15", <-- URL to the episode at svtplay.se
        "stream-url": "http://pirateplay.se:80/api/get_streams.js?url=http%3A%2F%2Fsvtplay.se%2Fvideo%2F2719584%2Fsvt-gavleborg%2Fsvt-gavleborg-2-3-19-15", <-- URL to API request to pirateplay.se
        "sub-title": "2/3 19.15", <-- episode identification
        "title": "SVT G\u00e4vleborg" <-- episode title
        "unique-name": "/2719584" <-- unique name, simply add this to the query path for details
    }, 
... ]
}
```

- host:port/shows/show-id/episode-id, returns a JSON containing the following keys (the same as above)

```JSON
{
    "site-url": "http://svtplay.se/video/2719584/svt-gavleborg/svt-gavleborg-2-3-19-15", 
    "stream-url": "http://pirateplay.se:80/api/get_streams.js?url=http%3A%2F%2Fsvtplay.se%2Fvideo%2F2719584%2Fsvt-gavleborg%2Fsvt-gavleborg-2-3-19-15", 
    "sub-title": "2/3 19.15", 
    "title": "SVT G\u00e4vleborg"
}
```

Right now there are some outstanding issues, and room for improvement, but the general setup works now.