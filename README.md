# YouTube Downloader

## Usage

Type this into the web console to receive a list of all videos of a channel:

```js
console.log(JSON.stringify([...document.getElementsByClassName("yt-simple-endpoint")]
    .filter(e => e.id === "video-title")
    .map(e => ({
        title: e.title,
        link: e.href,
    }))))
```
