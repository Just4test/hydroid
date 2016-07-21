from .service import Service
from .application import Application
from .adapter import Adapter
import yaml
import copy

KEYWORD = '__hydroid'
class Namespace:
    '''
    命名空间是应用的容器
    命名空间总是绑定到一个适配器
    '''
    
    
    def __init__(self, name, adapter, yml_storage, *args, **kwds):
        '''
        初始化命名空间。
        name 命名空间名称
        adapter 适配器
        yml_storage yml存储器。如果未指定此值，则优先使用适配器自带的存储器；
                    适配器未包含存储器的话，使用默认的本地存储器。
        '''
        self.name = name
        self.adapter = adapter
        self.yml_storage = yml_storage
        adapter.init_ns(self, *args, **kwds)
        
        self._load_yml()
        self._app = {}
        for name, data in self._yml_obj.items():
            self._app[name] = Application(self, name, data[KEYWORD]['base_on'])
        
        self.refresh()
        
    @property
    def yml(self):
        return yaml.dump(self._yml_obj)
        
    def _load_yml(self):
        yml = self.yml_storage.load_yml(self)
        self._yml_obj = yaml.load(yml) or {}
        
    def _save_yml(self):
        self.yml_storage.save_yml(self, self.yml)
        
    def refresh(self):
        '从远程更新状态'
        self._serv = {}
        for s in self.adapter.list_service(self):
            if s.app_name not in self._serv:
                self._serv[s.app_name] = {}
            self._serv[s.app_name][s.name] = s
            
    def _compile(self, yml = None):
        '''
        编译。这个功能用于将应用-服务结构的yml转换为docker-compose形式的水平yml。
        也可以用于检查yml的依赖关系是否合法。
        参数：
            yml:目标yml。会将此值和self._yml_obj整合，然后进行编译操作。
        返回：
            如果编译成功，将返回docker-compose 结构的yml文本
            如果编译失败，将返回一个元组：(app_name, serv_name, err_msg)
        '''
        # 准备数据
        # base仅用于查找依赖关系
        if yml is not None:
            base = copy.deepcopy(self._yml_obj)
            if isinstance(yml, str):
                yml = yaml.load(yml)
            else:
                yml = copy.deepcopy(yml)
            for k, v in yml.items():
                base[k] = v
        else:
            base = self._yml_obj
            yml = copy.deepcopy(self._yml_obj)
            
        
        def find_serv_base_on(app_name, serv_name):
            '在指定应用的作用域中，查找指定服务由哪个父应用提供'
            while app_name in base:
                if serv_name in base[app_name]:
                    return app_name
                else:
                    app_name = base[app_name][KEYWORD]['base_on']
                
        #编译
        ret = {}
        for app_name, app_data in yml.items():
            for serv_name, serv_data in app_data.items():
                if serv_name == KEYWORD:
                    continue
                fullname = self.adapter.join_name(serv_name, app_name)
                links = serv_data.get('links')
                if links:
                    serv_data['links'] = []
                    for link in links:
                        temp = link.split(':')
                        link_serv_name = temp[0]
                        link_alias_name = temp[-1]
                        link_app_name = find_serv_base_on(app_name, link_serv_name)
                        if not link_app_name:
                            e = Exception('应用[{}]中的服务[{}]链接到[{}]，但目标在作用域中不存在'.format(app_name, serv_name, link))
                            return (app_name, serv_name,  e)
                        link = '{}:{}'.format(self.adapter.join_name(link_app_name, link_serv_name), link_alias_name)
                        serv_data['links'].append(link)
                ret[fullname] = serv_data
               
        return yaml.dump(ret) 
        
    def deploy(self):
        '将本地更改部署到远程'
        remove_list = []
        for s in self.adapter.list_service(self):
            if s.app_name not in self._yml_obj \
            or s.name not in self._yml_obj[s.app_name]:
                remove_list.append(s.full_name)
        yml = self._compile()
        self.adapter.modify(self, yml, remove_list)
        
    def create_app(self, app_name, base_on_name = None):
        '创建一个空的应用'
        if app_name in self._yml_obj:
            raise Exception('指定创建应用[{}]，但同名应用已存在'.format(app_name))
        if base_on_name and not self.get_app(base_on_name):
            raise Exception('指定当前应用基于[{}]，但其不存在。'.format(base_on_name))
        
        self._yml_obj[app_name] = {
            KEYWORD: {
                'base_on': base_on_name
            }
        }
        self._save_yml()
        app = Application(self, app_name, base_on_name)
        self._app[app_name] = app
        return app
        
    def _app_update(self, app_name, yml):
        if not app_name in self._yml_obj:
            raise Exception('指定更新应用[{}]，但应用不存在'.format(app_name))
        
        data = {app_name: yaml.load(yml)}
        data[app_name][KEYWORD] = self._yml_obj[app_name][KEYWORD]
        # 进行一次测试编译，以确认更新内容是否合法
        result = self._compile(data)
        if isinstance(result, str):
            self._yml_obj[app_name] = data[app_name]
            self._save_yml()
            self.deploy()
        else:
            raise result[2]
    
    def get_app(self, name):
        return self._app.get(name)
        
    def list_app(self):
        return self._app.values()
        
    def list_serv(self, app_name):
        return self._servdic.get(app_name, [])
        
    def list_app_base_on(self, app_name):
        '列出所有基于指定app的app'
        
        
    def refreash(self):
        '执行此方法以重新列出ns下的所有app，以及各个app下的所有serv'
        servdic = {}
        self._servdic = servdic
        
        
        for serv in self.adapter.list_service(self):
            app_name = serv.app_name
            if app_name not in servdic:
                servdic[app_name] = []
            servdic[app_name].append(serv)
            
    def rm_serv(self, fullname):
        pass
        
    def rm_app(self, name):
        '''
        移除一个app，以及该app相关的所有service
        '''
        pass
        
    def __repr__(self):
        return '<NS [{}] by {}>'.format(self.name, self.adapter)