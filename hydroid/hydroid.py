from .adapter import Adapter
from .namespace import Namespace
from .service import Service
from .application import Application

class LocalYmlStorage:
    def save_yml(self, ns, yml):
        filename = 'Hydroid_{}.yml'.format(ns.name)
        with open(filename, 'w') as f:
            f.write(yml)
            
    def load_yml(self, ns, app_name):
        filename = 'Hydroid_{}.yml'.format(ns.name)
        if __import__('os').path.isfile(filename):
            return open(filename).read()
        else:
            return ''

class Hydroid:
    
    def __init__(self):
        self.nsdic = {}
        
    def create_ns(self, name, adapter, yml_storage = None, *args, **kwds):
        yml_storage = yml_storage or (adapter if adapter.yml_storage else LocalYmlStorage())
        ns = Namespace(name, adapter, yml_storage, *args, **kwds)
        self.nsdic[name] = ns
        return ns
        
    def ns(self, name):
        return self.nsdic[name] 
