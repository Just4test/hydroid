class Adapter:
    'dadala适配器接口'
    
    ################# 服务名分割和组合。通常不需要覆盖 ##################
    
    separator = '-in-'
    
    def split_name(self, full_name):
        '用于编译：将全名分割为服务名和应用名'
        temp = full_name.split(self.separator)
        if len(temp) == 2:
            serv_name = temp[0]
            app_name = temp[1]
            return serv_name, app_name
        else:
            raise Exception('不合法的全名：[{}]。全名必须被分隔符[{}]分成两部分'.
            format(full_name, self.separator))
         
    def join_name(self, serv_name, app_name):
        '用于编译：将服务名和应用名组合成全名'
        ret = serv_name + self.separator + app_name
        if 2 == len(ret.split(self.separator)):
            return ret
        else:
            raise Exception('[{}]和[{}]拼合成的全名不合法'.
            format(serv_name, app_name))
    
    ##################### 可选的YML存储器功能 #############
    
    yml_storage = False
    '指定适配器是否能保存yml。如果指定为True, 则需要实现save_yml和load_yml'
    
    def save_yml(self, ns, yml):
        pass
    
    def load_yml(self, ns):
        pass
    
    ################ 适配器功能 ##################
    
    def init_ns(self, ns, *args, **kwds):
        '返回True表示成功的初始化了NS'
        return False
    
    def modify(self, patch, remove):
        '''
        修改应用
        patch: 一个差异化的补丁。包含了所有改变的service的yml。
        remove: 一个列表，包含所有被移除的service。
        '''
        
    
    def list_service(self, ns):
        pass
    
    def get_service(self, ns, name):
        pass
    
    def start_service(self, ns, name):
        pass
    
    def stop_service(self, ns, name):
        pass
    
    def delete_service(self, ns, name):
        pass