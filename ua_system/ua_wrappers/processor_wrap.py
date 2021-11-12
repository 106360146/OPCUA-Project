
from opcua.server.binary_server_asyncio import OPCUAProtocol
from opcua.server.uaprocessor import UaProcessor, PublishRequestData
from opcua.ua.ua_binary import nodeid_from_binary, struct_from_binary
import opcua.ua.ua_binary as uabin
from opcua.common import utils
from opcua import ua
###
import logging
logger = logging.getLogger(__name__)

class UaProcessorWrap(UaProcessor):
    
    

    def _process_message(self, typeid, requesthdr, seqhdr, body):
        if typeid == ua.NodeId(ua.ObjectIds.CreateSessionRequest_Encoding_DefaultBinary):
            self.logger.info("Create session request")
            params = struct_from_binary(ua.CreateSessionParameters, body)

            # create the session on server
            self.session = self.iserver.create_session(self.name)
            # get a session creation result to send back
            sessiondata = self.session.create_session(params, sockname=self.sockname)

            response = ua.CreateSessionResponse()
            response.Parameters = sessiondata
            response.Parameters.ServerCertificate = self._connection.security_policy.client_certificate
            if self._connection.security_policy.server_certificate is None:
                data = params.ClientNonce
            else:
                data = self._connection.security_policy.server_certificate + params.ClientNonce
            response.Parameters.ServerSignature.Signature = \
                self._connection.security_policy.asymmetric_cryptography.signature(data)

            response.Parameters.ServerSignature.Algorithm = self._connection.security_policy.AsymmetricSignatureURI

            self.logger.info("sending create session response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.CloseSessionRequest_Encoding_DefaultBinary):
            self.logger.info("Close session request")

            if self.session:
                deletesubs = ua.ua_binary.Primitives.Boolean.unpack(body)
                self.session.close_session(deletesubs)
            else:
                self.logger.info("Request to close non-existing session")

            response = ua.CloseSessionResponse()
            self.logger.info("sending close session response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.ActivateSessionRequest_Encoding_DefaultBinary):
            self.logger.info("Activate session request")
            params = struct_from_binary(ua.ActivateSessionParameters, body)

            if not self.session:
                self.logger.info("request to activate non-existing session")
                raise utils.ServiceError(ua.StatusCodes.BadSessionIdInvalid)

            if self._connection.security_policy.client_certificate is None:
                data = self.session.nonce
            else:
                data = self._connection.security_policy.client_certificate + self.session.nonce
            self._connection.security_policy.asymmetric_cryptography.verify(data, params.ClientSignature.Signature)

            result = self.session.activate_session(params)

            response = ua.ActivateSessionResponse()
            response.Parameters = result

            self.logger.info("sending read response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.ReadRequest_Encoding_DefaultBinary):
            
            params = struct_from_binary(ua.ReadParameters, body)
            #params = ReadParameters(MaxAge:{self.MaxAge}, 
            #         TimestampsToReturn:{self.TimestampsToReturn}, NodesToRead:{self.NodesToRead})
            
            unpause = False
            unpause_event = self.iserver.event_comm.dispatch("Read Request Event", params.NodesToRead)
            
            if unpause_event is not None: 
                unpause_event.wait()
                unpause = True

            results = self.session.read(params)

            response = ua.ReadResponse()
            response.Results = results

            self.send_response(requesthdr.RequestHandle, seqhdr, response)
            
            if unpause:
                unpause_event.clear()
                unpause = False
                 
        elif typeid == ua.NodeId(ua.ObjectIds.WriteRequest_Encoding_DefaultBinary):
            self.logger.info("Write request")
            params = struct_from_binary(ua.WriteParameters, body)

            results = self.session.write(params)

            response = ua.WriteResponse()
            response.Results = results

            self.logger.info("sending write response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.BrowseRequest_Encoding_DefaultBinary):
            self.logger.info("Browse request")
            params = struct_from_binary(ua.BrowseParameters, body)

            results = self.session.browse(params)

            response = ua.BrowseResponse()
            response.Results = results

            self.logger.info("sending browse response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.GetEndpointsRequest_Encoding_DefaultBinary):
            self.logger.info("get endpoints request")
            params = struct_from_binary(ua.GetEndpointsParameters, body)

            endpoints = self.iserver.get_endpoints(params, sockname=self.sockname)

            response = ua.GetEndpointsResponse()
            response.Endpoints = endpoints

            self.logger.info("sending get endpoints response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.FindServersRequest_Encoding_DefaultBinary):
            self.logger.info("find servers request")
            params = struct_from_binary(ua.FindServersParameters, body)

            servers = self.local_discovery_service.find_servers(params)

            response = ua.FindServersResponse()
            response.Servers = servers

            self.logger.info("sending find servers response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.RegisterServerRequest_Encoding_DefaultBinary):
            self.logger.info("register server request")
            serv = struct_from_binary(ua.RegisteredServer, body)

            self.local_discovery_service.register_server(serv)

            response = ua.RegisterServerResponse()

            self.logger.info("sending register server response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.RegisterServer2Request_Encoding_DefaultBinary):
            self.logger.info("register server 2 request")
            params = struct_from_binary(ua.RegisterServer2Parameters, body)

            results = self.local_discovery_service.register_server2(params)

            response = ua.RegisterServer2Response()
            response.ConfigurationResults = results

            self.logger.info("sending register server 2 response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.TranslateBrowsePathsToNodeIdsRequest_Encoding_DefaultBinary):
            self.logger.info("translate browsepaths to nodeids request")
            params = struct_from_binary(ua.TranslateBrowsePathsToNodeIdsParameters, body)

            paths = self.session.translate_browsepaths_to_nodeids(params.BrowsePaths)

            response = ua.TranslateBrowsePathsToNodeIdsResponse()
            response.Results = paths

            self.logger.info("sending translate browsepaths to nodeids response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.AddNodesRequest_Encoding_DefaultBinary):
            self.logger.info("add nodes request")
            params = struct_from_binary(ua.AddNodesParameters, body)

            results = self.session.add_nodes(params.NodesToAdd)

            response = ua.AddNodesResponse()
            response.Results = results

            self.logger.info("sending add node response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.DeleteNodesRequest_Encoding_DefaultBinary):
            self.logger.info("delete nodes request")
            params = struct_from_binary(ua.DeleteNodesParameters, body)

            results = self.session.delete_nodes(params)

            response = ua.DeleteNodesResponse()
            response.Results = results

            self.logger.info("sending delete node response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.AddReferencesRequest_Encoding_DefaultBinary):
            self.logger.info("add references request")
            params = struct_from_binary(ua.AddReferencesParameters, body)

            results = self.session.add_references(params.ReferencesToAdd)

            response = ua.AddReferencesResponse()
            response.Results = results

            self.logger.info("sending add references response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.DeleteReferencesRequest_Encoding_DefaultBinary):
            self.logger.info("delete references request")
            params = struct_from_binary(ua.DeleteReferencesParameters, body)

            results = self.session.delete_references(params.ReferencesToDelete)

            response = ua.DeleteReferencesResponse()
            response.Parameters.Results = results

            self.logger.info("sending delete references response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)


        elif typeid == ua.NodeId(ua.ObjectIds.CreateSubscriptionRequest_Encoding_DefaultBinary):
            self.logger.info("create subscription request")
            params = struct_from_binary(ua.CreateSubscriptionParameters, body)

            result = self.session.create_subscription(params, self.forward_publish_response)

            response = ua.CreateSubscriptionResponse()
            response.Parameters = result

            self.logger.info("sending create subscription response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.ModifySubscriptionRequest_Encoding_DefaultBinary):
            self.logger.info("modify subscription request")
            params = struct_from_binary(ua.ModifySubscriptionParameters, body)

            result = self.session.modify_subscription(params, self.forward_publish_response)

            response = ua.ModifySubscriptionResponse()
            response.Parameters = result

            self.logger.info("sending modify subscription response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.DeleteSubscriptionsRequest_Encoding_DefaultBinary):
            self.logger.info("delete subscriptions request")
            params = struct_from_binary(ua.DeleteSubscriptionsParameters, body)

            results = self.session.delete_subscriptions(params.SubscriptionIds)

            response = ua.DeleteSubscriptionsResponse()
            response.Results = results

            self.logger.info("sending delte subscription response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.CreateMonitoredItemsRequest_Encoding_DefaultBinary):
            self.logger.info("create monitored items request")
            params = struct_from_binary(ua.CreateMonitoredItemsParameters, body)
            results = self.session.create_monitored_items(params)

            response = ua.CreateMonitoredItemsResponse()
            response.Results = results

            self.logger.info("sending create monitored items response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.ModifyMonitoredItemsRequest_Encoding_DefaultBinary):
            self.logger.info("modify monitored items request")
            params = struct_from_binary(ua.ModifyMonitoredItemsParameters, body)
            results = self.session.modify_monitored_items(params)

            response = ua.ModifyMonitoredItemsResponse()
            response.Results = results

            self.logger.info("sending modify monitored items response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.DeleteMonitoredItemsRequest_Encoding_DefaultBinary):
            self.logger.info("delete monitored items request")
            params = struct_from_binary(ua.DeleteMonitoredItemsParameters, body)

            results = self.session.delete_monitored_items(params)

            response = ua.DeleteMonitoredItemsResponse()
            response.Results = results

            self.logger.info("sending delete monitored items response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.HistoryReadRequest_Encoding_DefaultBinary):
            self.logger.info("history read request")
            params = struct_from_binary(ua.HistoryReadParameters, body)

            results = self.session.history_read(params)

            response = ua.HistoryReadResponse()
            response.Results = results

            self.logger.info("sending history read response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.RegisterNodesRequest_Encoding_DefaultBinary):
            self.logger.info("register nodes request")
            params = struct_from_binary(ua.RegisterNodesParameters, body)
            self.logger.info("Node registration not implemented")

            response = ua.RegisterNodesResponse()
            response.Parameters.RegisteredNodeIds = params.NodesToRegister

            self.logger.info("sending register nodes response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.UnregisterNodesRequest_Encoding_DefaultBinary):
            self.logger.info("unregister nodes request")
            params = struct_from_binary(ua.UnregisterNodesParameters, body)

            response = ua.UnregisterNodesResponse()

            self.logger.info("sending unregister nodes response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.PublishRequest_Encoding_DefaultBinary):
            self.logger.info("publish request")

            if not self.session:
                return False

            params = struct_from_binary(ua.PublishParameters, body)

            data = PublishRequestData()
            data.requesthdr = requesthdr
            data.seqhdr = seqhdr
            with self._datalock:
                self._publishdata_queue.append(data)  # will be used to send publish answers from server
                if self._publish_result_queue:
                    result = self._publish_result_queue.pop(0)
                    self.forward_publish_response(result)
            self.session.publish(params.SubscriptionAcknowledgements)
            self.logger.info("publish forward to server")

        elif typeid == ua.NodeId(ua.ObjectIds.RepublishRequest_Encoding_DefaultBinary):
            self.logger.info("re-publish request")

            params = struct_from_binary(ua.RepublishParameters, body)
            msg = self.session.republish(params)

            response = ua.RepublishResponse()
            response.NotificationMessage = msg

            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.CloseSecureChannelRequest_Encoding_DefaultBinary):
            self.logger.info("close secure channel request")
            self._connection.close()
            response = ua.CloseSecureChannelResponse()
            self.send_response(requesthdr.RequestHandle, seqhdr, response)
            return False

        elif typeid == ua.NodeId(ua.ObjectIds.CallRequest_Encoding_DefaultBinary):
            self.logger.info("call request")

            params = struct_from_binary(ua.CallParameters, body)

            results = self.session.call(params.MethodsToCall)

            response = ua.CallResponse()
            response.Results = results

            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.SetMonitoringModeRequest_Encoding_DefaultBinary):
            self.logger.info("set monitoring mode request")

            params = struct_from_binary(ua.SetMonitoringModeParameters, body)

            # FIXME: Implement SetMonitoringMode
            # Send dummy results to keep clients happy
            response = ua.SetMonitoringModeResponse()
            results = ua.SetMonitoringModeResult()
            ids = params.MonitoredItemIds
            statuses = [ua.StatusCode(ua.StatusCodes.Good) for node_id in ids]
            results.Results = statuses
            response.Parameters = results

            self.logger.info("sending set monitoring mode response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        elif typeid == ua.NodeId(ua.ObjectIds.SetPublishingModeRequest_Encoding_DefaultBinary):
            self.logger.info("set publishing mode request")

            params = struct_from_binary(ua.SetPublishingModeParameters, body)

            # FIXME: Implement SetPublishingMode
            # Send dummy results to keep clients happy
            response = ua.SetPublishingModeResponse()
            results = ua.SetPublishingModeResult()
            ids = params.SubscriptionIds
            statuses = [ua.StatusCode(ua.StatusCodes.Good) for node_id in ids]
            results.Results = statuses
            response.Parameters = results

            self.logger.info("sending set publishing mode response")
            self.send_response(requesthdr.RequestHandle, seqhdr, response)

        else:
            self.logger.warning("Unknown message received %s", typeid)
            raise utils.ServiceError(ua.StatusCodes.BadServiceUnsupported)

        return True

class OPCUAProtocolWrap(OPCUAProtocol):
    """Interface for OPCUA protocol.
    """

    iserver = None
    loop = None
    logger = None
    policies = None
    clients = None

    def __str__(self):
        return "OPCUAProtocol({}, {})".format(self.peername, self.processor.session)
    __repr__ = __str__

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        self.logger.info('New connection from %s', self.peername)
        self.transport = transport
        self.processor = UaProcessorWrap(self.iserver, self.transport)
        self.processor.set_policies(self.policies)
        self.data = b""
        self.iserver.asyncio_transports.append(transport)
        self.clients.append(self)

    def connection_lost(self, ex):
        self.logger.info('Lost connection from %s, %s', self.peername, ex)
        self.transport.close()
        self.iserver.asyncio_transports.remove(self.transport)
        self.processor.close()
        if self in self.clients:
            self.clients.remove(self)

    def data_received(self, data):
        logger.debug("received %s bytes from socket", len(data))
        if self.data:
            data = self.data + data
            self.data = b""
        self._process_data(data)

    def _process_data(self, data):
        buf = ua.utils.Buffer(data)
        while True:
            try:
                backup_buf = buf.copy()
                try:
                    hdr = uabin.header_from_binary(buf)
                except ua.utils.NotEnoughData:
                    logger.info("We did not receive enough data from client, waiting for more")
                    self.data = backup_buf.read(len(backup_buf))
                    return
                if len(buf) < hdr.body_size:
                    logger.info("We did not receive enough data from client, waiting for more")
                    self.data = backup_buf.read(len(backup_buf))
                    return
                ret = self.processor.process(hdr, buf)
                if not ret:
                    logger.info("processor returned False, we close connection from %s", self.peername)
                    self.transport.close()
                    return
                if len(buf) == 0:
                    return
            except Exception:
                logger.exception("Exception raised while parsing message from client, closing")
                return