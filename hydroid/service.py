
class Service:
    
    def __init__(self, ns, full_name, name, app_name):
        self.ns = ns
        self.full_name = full_name
        self.name = name
        self.app_name = app_name
        
    def __repr__(self):
        return '<SERV [{}] in [{}]>'.format(self.name, self.app_name)
        
    @property
    def adapter(self):
        return self.ns.adapter
        
    def start(self):
        return self.adapter.start_service(self.ns, self.full_name)
        
    def stop(self):
        return self.adapter.stop_service(self.ns, self.full_name)
        
    def delete(self):
        return self.adapter.delete_service(self.ns, self.full_name)