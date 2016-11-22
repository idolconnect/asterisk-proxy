## asterisk-proxy

A simple man-in-the-middle proxy from [whale-simulator](https://github.com/summertriangle-dev/whale-simulator). Requires Python 3.5 and aiohttp.
Some features are not implemented, sorry!

As always, thanks to summertriangle-dev's work.

### Run it

```bash
$ pyenv virtualenv 3.5.2 asterisk-proxy
$ pyenv local asterisk-proxy
$ pip install -r requirements.txt
$ python proxy.py
```

Please rewrite your `host` as:
```
app01.gameicone.net <proxy running computer ip>
```