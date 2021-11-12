from ua_system.request_handler import EventCommunicator
from opcua.server.internal_server import InternalServer, InternalSession
from ua_system.ua_wrappers.processor_wrap import OPCUAProtocolWrap
from opcua.server.binary_server_asyncio import BinaryServer
from opcua import Server
from opcua.ua import  uatypes


class BinaryServerWrap(BinaryServer):
    def __init__(self, internal_server, hostname, port):
        super().__init__(internal_server, hostname, port)

    def start(self):
        prop = dict(
                iserver=self.iserver,
                loop=self.loop,
                logger=self.logger,
                policies=self._policies,
                clients=self.clients
            )
        protocol_factory = type('OPCUAProtocolWrap', (OPCUAProtocolWrap,), prop)

        coro = self.loop.create_server(protocol_factory, self.hostname, self.port)
        self._server = self.loop.run_coro_and_wait(coro)
        # get the port and the hostname from the created server socket
        # only relevant for dynamic port asignment (when self.port == 0)
        if self.port == 0 and len(self._server.sockets) == 1:
            # will work for AF_INET and AF_INET6 socket names
            # these are to only families supported by the create_server call
            sockname = self._server.sockets[0].getsockname()
            self.hostname = sockname[0]
            self.port = sockname[1]
        self.logger.warning('Listening on {0}:{1}'.format(self.hostname, self.port))
        
class ServerWrap(Server):
    def __init__(self, shelffile=None, iserver=None):
        super().__init__(shelffile=None, iserver=InternalServerWrap())
        

    def start(self):
        """
        Start to listen on network lau
        """
        self._setup_server_nodes()
        self.iserver.start()
        try:
            if not self.bserver:
                self.bserver = BinaryServerWrap(self.iserver, self.endpoint.hostname, self.endpoint.port)
            self.bserver.set_policies(self._policies)
            self.bserver.set_loop(self.iserver.loop)
            self.bserver.start()
        except Exception as exp:
            self.iserver.stop()
            raise exp

class InternalServerWrap(InternalServer):
    def __init__(self, shelffile=None, user_manager=None, session_cls=None):
        super().__init__(shelffile=shelffile, user_manager=user_manager, session_cls=session_cls)
        self.event_comm = EventCommunicator()

    def add_request_handler(self, event, handler):
        self.event_comm.add_handler(event, handler)
