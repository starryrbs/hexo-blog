## 部署

> 运行自动化部署

    fab deploy

>  修改配置 (下面为远程服务器的连接信息)

    env.user = ''
    env.password = ''
    env.sudo_password = env.password
    env.hosts = ['']
    env.port = 