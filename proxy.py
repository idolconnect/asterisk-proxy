import asyncio
import aiohttp
from aiohttp import web
import crypto
import json
import os
import time
from datetime import datetime

CLIENT_MSG = []
SERVER_MSG = []
runloop = asyncio.get_event_loop()
thesession = aiohttp.ClientSession()

os.path.isdir("logs/") or os.mkdir("logs/")

async def save(endpoint, request_headers, get_params, request_body, response_headers, response_body):
    date = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    decrypted_response_body = json.loads(crypto.decrypt(response_body.decode()))
    try:
        decrypted_request_body = json.loads(crypto.decrypt(request_body))
    except:
        decrypted_request_body = request_body.decode()
    data = {
        "endpoint": endpoint,
        "request": {
            "headers": request_headers,
            "get_params": get_params,
            "body": decrypted_request_body
        },
        "response": {
            "headers": response_headers,
            "body": decrypted_response_body
        }
    }
    log_file_path = "logs/{}_{}.json".format(date, endpoint.replace("/", "-"))
    with open(log_file_path, "w") as cur:
        cur.write(json.dumps(data))
        os.chmod(log_file_path, 0o644)
    print("logging success")

class ProxyState(object):
    def __init__(self):
        self.replays = {}

    async def proxy_do(self, request):
        get_param = "?"
        for i, j in request.GET.items():
            get_param = get_param + "{}={}&".format(i,j)
        actual_request_target = request.match_info["rurl"]
        to_url = "{0}://{1}/{2}{3}".format(
            request.scheme, request.headers.get("Host"), actual_request_target, get_param
        )
        print("notice: request to", to_url)

        content = await request.content.read()

        headers = dict(request.headers)
        headers["ACCEPT-ENCODING"] = "*/*"
        headers["X-IDOLCONNECT-GZIP"] = "off"

        is_api_request = "X-IDOLCONNECT-APPVERSION" in headers

        if request.method == "POST":
            async with thesession.post(to_url, headers=headers, data=content) as resp:
                bdy = await resp.content.read()
                mutable_h = dict(resp.headers)
                if "TRANSFER-ENCODING" in mutable_h:
                    del mutable_h["TRANSFER-ENCODING"]
                if is_api_request:
                    await save(actual_request_target, dict(headers), dict(request.GET), content, mutable_h, bdy)
                our_response = web.Response(status=resp.status, headers=mutable_h, body=bdy)
        else:
            async with thesession.get(to_url, headers=headers) as resp:
                bdy = await resp.content.read()
                mutable_h = dict(resp.headers)
                if "TRANSFER-ENCODING" in mutable_h:
                    del mutable_h["TRANSFER-ENCODING"]
                if is_api_request:
                    await save(actual_request_target, dict(headers), dict(request.GET), content, mutable_h, bdy)
                our_response = web.Response(status=resp.status, headers=mutable_h, body=bdy)

        return our_response

state = ProxyState()
proxy = web.Application(loop=runloop)
proxy.router.add_route("*", r"/{rurl:.*}", state.proxy_do)

def begin(host="0.0.0.0", port=10080, sdt=60.0):
    prox_handler = proxy.make_handler()
    loop = proxy.loop

    psrv = loop.run_until_complete(loop.create_server(prox_handler, host, port))
    print("Proxy starts on port", port)

    try:
        loop.run_forever()
    except KeyboardInterrupt:  # pragma: no branch
        pass
    finally:
        psrv.close()
        loop.run_until_complete(psrv.wait_closed())
        loop.run_until_complete(proxy.shutdown())
        loop.run_until_complete(prox_handler.finish_connections(sdt))
        loop.run_until_complete(proxy.cleanup())
        loop.close()

begin()
