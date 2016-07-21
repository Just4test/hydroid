from .adapter import Adapter
from .hydroid import Service as HydroidService
import sys
sys.path.append('../')
from alauda import *
import yaml
import hashlib

def app_name(ns):
    '返回和ns关联的应用的名称。'
    return '{}-hydroid'.format(ns.name)

class AlaudaAdapter(Adapter):
    '一个hydroid NS 对应着一个Alauda Application'
    
    ##################### 可选的YML存储器功能 #############
    
    yml_storage = True
    '使用仓库的详细说明功能存储YML'
    
    def save_yml(self, ns, yml):
        reponame = 'hydroid-{}-yml'.format(ns.name)
        repo = ns._alauda_app._alauda.get_repo(reponame)
        if repo:
            repo.delete()
        description = '这是Hydroid为[{}]命名空间存储的YML，请勿更改其详细说明。'.format(ns.name)
        build_config = BuildConfig.create_simple('http://a.cn/a.git', TagConfig.create('a', 'a'))
        print('存储YML\n', yml)
        ns._alauda_app._alauda.create_repo(reponame, description, False, build_config, yml)
        
        
    
    def load_yml(self, ns):
        reponame = 'hydroid-{}-yml'.format(ns.name)
        repo = ns._alauda_app._alauda.get_repo(reponame)
        if repo:
            print('载入YML\n', repo.full_description)
            return repo.full_description or ''
        else:
            print('载入YML\n', '')
            return ''
    
    def __init__(self, namespace, token, default_region = 'BEIJING3', urlbase = None):
        self.alauda = Alauda(namespace, token, default_region, urlbase)
        
        
    def __repr__(self):
        return '<AlaudaAdapter [{}]>'.format(self.alauda.namespace)
    
    def init_ns(self, ns, region = None):
        '返回True表示成功的初始化了NS'
        name = app_name(ns)
        temp = self.alauda.get_application(name)
        if temp:
            if region and temp.region_name != region:
                raise Exception('创建和命名空间关联的应用时失败。想要在[{}]创建，但已有位于[{}]的同名应用。'.format(name, temp.region_name))
            ns._alauda_app = temp
            return True
        ns._alauda_app = self.alauda.create_application(name, region)
        return True
    
    def get_repo(self, ns, url, context, branch):
        '根据参数返回已经存在的repo，或创建新的repo'
        name = url.split('/')[-1].replace('.git', '')
        h = hashlib.md5((url + context + branch).encode()).hexdigest()
        name = 'hydroid_{}_{}'.format(name, h[:5])
        repo = ns._alauda_app._alauda.get_repo(name)
        if repo:
            return repo #好糙的处理
            
        build_config = None
        tag_config = TagConfig.create('latest', code_branch = branch, build_context_path = context, dockerfile_location = context)
        
        if url.find('github:') == 0:
            namespace, name = url.replace('github:', '').split('/')
            build_config = BuildConfig.create_client('Github', namespace, name, tag_config)
        else:
            build_config = BuildConfig.create_simple(url, tag_config)
        description = '{}\n{}\ncontext: {}\nbranch: {}'.format(app_name(ns), url, context, branch)
        repo = ns._alauda_app._alauda.create_repo(name, description, False, build_config)
        return repo
    
    def get_yml(self, ns):
        return ns._alauda_app.yaml
        
    def modify(self, ns, patch_yml, remove):
        '''
        修改应用
        patch: 一个差异化的补丁。包含了所有改变的service的yml。
        remove: 一个列表，包含所有被移除的service。
        '''
        # 处理移除service
        for name in remove:
            ns._alauda_app.delete_service(name)
            
        # 处理补丁中的构建
        patch_obj = yaml.load(patch_yml)
        for serv_name, serv_data in patch_obj.items():
            if 'build' in serv_data:
                temp = serv_data['build']
                url = temp
                context = '/'
                branch = 'master'
                if temp is not str:
                    url = temp['url']
                    if 'context' in temp:
                        context = temp['context']
                    if 'branch' in temp:
                        branch = temp['branch']
                repo = self.get_repo(ns, url, context, branch)
                repo.build()
                
                del serv_data['build']
                serv_data['image'] = repo.url
        
        # 应用补丁
        ns._alauda_app.update(yaml.dump(patch_obj))

    
    def list_service(self, ns):
        ret = []
        for s in ns._alauda_app.list_service():
            serv_name, app_name = self.split_name(s.name)
            ret.append(HydroidService(ns, s.name, serv_name, app_name))
        return ret
    
    def get_service(self, ns, name):
        s = ns._alauda_app.get_service(name)
        if s:
            serv_name, app_name = self.split_name(s.name)
            return HydroidService(ns, s.name, serv_name, app_name)
        else:
            return None
    
    def start_service(self, ns, name):
        ns._alauda_app.get_service(name).start()
    
    def stop_service(self, ns, name):
        ns._alauda_app.get_service(name).stop()
    
    def delete_service(self, ns, name):
        ns._alauda_app.get_service(name).delete()