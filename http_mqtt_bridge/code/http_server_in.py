import json
import traceback
import cherrypy
import logging
import zmq
import threading
import multiprocessing
logger = logging.getLogger("main.http_server_in")
context = zmq.Context()

zmq_lock = threading.Lock()

class HTTPInBuildingBlock(multiprocessing.Process):
    def __init__(self, config, zmq_conf):
        super().__init__()

        self.config = config
        self.constants = config['constants']

        # declarations
        self.zmq_conf = zmq_conf
        self.zmq_out = None

    def do_connect(self):
        self.zmq_out = context.socket(self.zmq_conf['type'])
        if self.zmq_conf["bind"]:
            self.zmq_out.bind(self.zmq_conf["address"])
        else:
            self.zmq_out.connect(self.zmq_conf["address"])

    def run(self):
        logger.info("started")
        self.do_connect()
        cherrypy.config.update({
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8080})
        try:
            cherrypy.quickstart(PostHandler(self), config={'global': {
                'engine.autoreload.on': False,
                'server.thread_pool':1
            }})
        except Exception:
            logger.error(traceback.format_exc())
        
        logger.info("Done")


    def dispatch(self, output):
        with zmq_lock:
            logger.info(f"dispatch to { output['path']} of {output['payload']}")
            self.zmq_out.send_json({'path': output.get('path', ""), 'payload': output['payload']})


class PostHandler(object):
    def __init__(self,parent):
        self.parent = parent

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def default(self, *args):
        if cherrypy.request.method == "POST":
            topic = '/'.join(args)
            payload = cherrypy.request.json
            logger.debug(f"{topic}:>:{payload}")
            self.parent.dispatch({'path':topic,'payload':payload})
            return
        
