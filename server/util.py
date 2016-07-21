import leancloud

role_admin = None
role_user = None
adapter_map = {}

def init_leancloud():
    
    ################# INIT ROLE ################
    def get_or_create_role(name):
        query = leancloud.Query(leancloud.Role)
        query.equal_to('name', name)
        result = query.find()
        if 1 == len(result):
            return result[0], False
        else:
            ret = leancloud.Role(name)
            ret.save()
            print('Create role {}'.format(name))
            return ret, True
            
    global role_admin, role_user
    role_admin, no_admin = get_or_create_role('Administrator')
    if no_admin:
        user_admin = leancloud.User()
        user_admin.set_username('admin')
        user_admin.set_password('admin')
        user_admin.sign_up()
        role_admin.get_users().add(user_admin)
        role_admin.save()
        print('Create user admin/admin')
        
    role_user, _ = get_or_create_role('User')
    

def create_adapter(name, clazz, data):