# Copyright 2016 Hynek Schlawack
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

"""
Service discovery for web exposure.
"""

try:
    from consul import Check
    from consul.aio import Consul as _Consul  # prevent accidental usage
except ImportError:
    Check = Consul = None


__all__ = [
    "ConsulAgent",
]


class ConsulAgent:
    """
    Service discovery via a local Consul agent.

    Pass as ``service_discovery`` into
    :func:`prometheus_async.aio.web.start_http_server`/
    :func:`prometheus_async.aio.web.start_http_server_in_thread`.

    :param str name: Application name that is used for the name and the service
        ID if not set.
    :param str service_id: Consul Service ID.  If not set, *name* is used.
    :param tuple tags: Tags to use in Consul registration.
    :param str token: A consul access token.
    :param bool deregister: Whether to deregister when the HTTP server is
        closed.
    """
    def __init__(self, *, name="app-metrics", service_id=None, tags=(),
                 token=None, deregister=True):
        self.name = name
        self.service_id = service_id or name
        self.tags = tags
        self.token = token
        self.deregister = deregister

    async def register(self, metrics_server, loop):
        """
        :return: A coroutine callable to deregister or ``None``.
        """
        consul = _Consul(token=self.token, loop=loop)

        if not await consul.agent.service.register(
            name=self.name,
            service_id=self.service_id,
            address=metrics_server.socket.addr,
            port=metrics_server.socket.port,
            tags=self.tags,
            check=Check.http(
                metrics_server.url, "10s",
            )
        ):  # pragma: nocover
            return None

        async def deregister():
            try:
                if self.deregister is True:
                    await consul.agent.service.deregister(self.service_id)
            finally:
                consul.close()

        return deregister
