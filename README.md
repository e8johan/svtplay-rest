SVTPlay REST

This provides a REST interface to traverse the available shows and episodes 
provided by SVTPlay.

You can access it using the following paths:

- `host:port/shows` returns a JSON containing the following keys
  - `shows` contains a list of shows
    - `name` the human-reaadable name of the show
    - `site-url` the URL of the show at svtplay.se
    - `unique-name` the unique name of the show (the `show-id` used in the next request)
- `host:port/shows/show-id`, returns a JSON containing the following keys
  - `name` the human readable name of the show
  - `site-url` the URL of the show at svtplay.se
  - `episodes` a list of episodes
    - `title` the human-readable title of the episode
    - `sub-title` the human-readable identification of the show, e.g. "Avsnitt 3" or a date, but this can also be a descriptive string
    - `unique-name` the unique name of the episode (the `episode-id` used in the next request)
    - `update-index` an index increased everytime a new episode is added to the database, for detecting updates
    - `site-url` the URL of the episode at svtplay.se
    - `stream-url` a prepared URL to pass to pirateplay.se to get links to the stream data
- `host:port/shows/show-id/episode-id`, returns a JSON containing the keys for each unique show as described above
    - `title`
    - `sub-title`
    - `update-index`
    - `site-url`
    - `stream-url`

An example flow looks something like this:

GET request sent to `host:port/shows`.
    
```JSON
{
    "shows": [
    {
        "name": "SVT G\u00e4vleborg",
        "site-url": "http://svtplay.se/svt-gavleborg",
        "unique-name": "/svt-gavleborg"
    }, 
... ]
}
```

Take the `unique-name` of the show of interest and append to the request URL. I.e. send a GET request to `host:port/shows/svt-gavleborg`.

```JSON
{
    "name": "SVT G\u00e4vleborg",
    "site-url": "http://svtplay.se/svt-gavleborg",
    "episodes": [
    {
        "site-url": "http://svtplay.se/video/2719584/svt-gavleborg/svt-gavleborg-2-3-19-15",
        "stream-url": "http://pirateplay.se:80/api/get_streams.js?url=http%3A%2F%2Fsvtplay.se%2Fvideo%2F2719584%2Fsvt-gavleborg%2Fsvt-gavleborg-2-3-19-15",
        "sub-title": "2/3 19.15",
        "title": "SVT G\u00e4vleborg",
        "unique-name": "/2719584",
        "update-index": 8
    }, 
... ]
}
```

Again, take the `unique-name` of the episode of interest and append to the request URL. I.e. send a GET request to `host:port/shows/svt-gavleborg/2719584`

```JSON
{
    "site-url": "http://svtplay.se/video/2719584/svt-gavleborg/svt-gavleborg-2-3-19-15", 
    "stream-url": "http://pirateplay.se:80/api/get_streams.js?url=http%3A%2F%2Fsvtplay.se%2Fvideo%2F2719584%2Fsvt-gavleborg%2Fsvt-gavleborg-2-3-19-15", 
    "sub-title": "2/3 19.15", 
    "title": "SVT G\u00e4vleborg",
    "update-index": 8
}
```

Right now there are some outstanding issues, and room for improvement, but the general setup works now.