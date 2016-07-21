# 简介
Hydroid致力于让微服务后台开发者以简单的操作创建自己的调试环境。可以将其看作一个扩展的docker-compose。

# 解决的问题
单机环境中，docker-compose 用于构建并运行一组相互依赖的服务(以下称为应用)。Hydroid使用适配器抽象了对资源的访问，从而允许在更为复杂的环境下——你自己的数据中心、AWS，甚至混合环境——从配置文件构建并运行应用。

相比于 docker-compose 只能创建独立的应用，Hydroid 允许创建具有单向依赖的应用。如果应用A依赖于B，则A中的服务可以连接到B中的服务。

通常在开发后台应用时，会有一个test环境用于运行测试代码。如果有多个开发者协作，他们在使用test环境上会有冲突。对此，有的解决方法是创建多个test环境。这导致一个问题，多个test环境中会有一些重复的组件，浪费了系统资源。Hydroid 不仅允许各个开发者创建自己的test应用，还支持应用依赖: test是一个完整的后台架构，包含所有服务。开发者A可以创建test-A，指定其依赖test，且仅包含自己关心的几个服务。
￼

上图中，如果开发者需要本地调试依赖API服务器的前端服务器，则他可以本地运行前端和API，或者仅运行前端，并将前端连接到test环境的api服务器。然而在AWS等现代LaaS中，API这类内部服务通常是不暴露在公网上的。以往的解决方法是VPN到AWS内网以访问API；或者把每一个API都暴露在公网上。Hydroid 的混合适配器允许开发者在本地运行需要调试的服务，并将其映射到AWS的应用中。
￼
# 工作方式
Hydroid 适配器提供计算资源的访问能力。它非常类似 docker-compose ，从一个yml文本创建一个应用。
Hydroid 控制器将各个应用的yml编译为一整个yml，从而实现跨应用的服务连接。
# 示例
```python
#创建hydroid实例
hydroid = Hydroid()
#创建适配器实例
adapter = AlaudaAdapter('username', 'oauth')
#以适配器创建命名空间
ns = hydroid.create_ns('ns', adapter)
#创建应用app1
app1 = ns.create_app('app1', None, open('app1.yml''))
app1.start()
#创建基于app1的应用app2
app2 = ns.create_app('app2', 'app1', open('app2.yml'))
app2.start()
#重新设定app1的yml。这会导致app2被重新部署。
app1.set_yml(open('app1_new.yml'))

```
# 概念
## Hydroid
实质上只是简单地管理命名空间。
- 创建命名空间
- 根据名字获取命名空间
## Namespace
命名空间，连接到适配器并实现核心的控制器功能:编译多个应用yml到一个总yml。
- 创建应用
- 列出应用
- 根据名字获取应用
- 刷新状态
- 编译yml
- 重新部署整个命名空间
- 重新部署单个应用
## Application
应用。它对应着一个yml，以及一组服务。应用之间可以有依赖关系。
- 读取yml
- 更新yml
- 重新部署
- 刷新状态
- 列出应用内的服务
- 根据名字获取应用内的服务
- 根据名字获取可以链接的服务
- 启动
- 停止
- 自我删除
## Service
应用中的单个服务。从yml级别，服务是只读的。
- 启动
- 停止
- 获取访问链接