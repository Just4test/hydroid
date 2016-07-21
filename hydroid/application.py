from .service import Service
import yaml
import copy

class Application:
    
    def __init__(self, ns, name, base_on_name = None):
        self.ns = ns
        self.name = name
        self.base_on_name = base_on_name
        
    def __repr__(self):
        return '<APP [{}] base on [{}]>'.format(self.name, self.base_on_name)
            
    @property
    def base_on(self):
        return self.ns.get_app(self.base_on_name)
    
    @property
    def yml(self):
        '返回yml文本对象'
        pass
    
    def get_service(self, name):
        '返回app包含的指定名称的服务对象'
        pass
        
    def get_accessable_service(self, name):
        '返回app可访问的服务对象。该服务可能是app内部的服务，也可能是其依赖的上层app的服务。'
        s = self.get_service(name)
        if s:
            return s
        if self.base_on is None:
            return None
        else:
            return self.base_on.get_accessable_service(name)
    
    @property
    def adapter(self):
        return self.ns.adapter
    
    def update(self, yml):
        self.ns._app_update(self.name, yml)
    
    def list_serv(self):
        return self.ns.list_serv(self.name)
    
    def list_base_on_service(self):
        pass
    
    def state(self):
        pass
    
    def stop(self):
        pass
    
    def delete(self):
        pass
