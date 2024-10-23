传感器型号ADL400N-CT/D10  
485隔离器 https://detail.tmall.com/item.htm?_u=n166ks0128b&id=697469868950&spm=a1z09.2.0.0.cb982e8di1rQzl&skuId=5009997785668
主控板Beaglebone Y  
要将您的代码部署到Linux服务器上，并使用Nginx来配合Flask应用以实现网页展示，我们需要进行一些步骤，包括安装和配置Flask与Nginx，并使其协同工作。以下是完整的解决方案：  
整体思路
Flask：仍然用Python编写数据采集的Flask应用，用于读取电能表的电压和电流值。  
Nginx：用作反向代理，转发来自客户端的请求到Flask应用，同时提供静态文件支持。  
Gunicorn：作为WSGI服务器，负责运行Flask应用，接收和处理Nginx的请求。  
修改后的代码  
首先，我们对Flask的部分代码进行稍微修改，以适应在生产环境中通过Gunicorn来运行。

1. 部署Flask应用
在Linux服务器上安装Python虚拟环境：
```
sudo apt update
sudo apt install python3-pip python3-venv
```
创建虚拟环境：
```
python3 -m venv myenv
```
激活虚拟环境
```
source myenv/bin/activate
```
激活后，您会看到命令提示符前面有(myenv)，表示正在使用虚拟环境。

安装必要的Python包：

```
pip install minimalmodbus flask gunicorn
```
保存您的Flask代码，例如保存为 app.py。

运行应用（使用Gunicorn）：

```
gunicorn -w 4 -b 0.0.0.0:6900 app:app
```
-w 4：表示使用4个工作线程来处理请求。
-b 0.0.0.0:5000：表示监听所有IP地址的5000端口。
2. 配置Nginx
接下来，您需要配置Nginx作为反向代理，转发请求到Gunicorn运行的Flask应用。

安装Nginx：

```
sudo apt install nginx
```
创建Nginx配置文件： 编辑新的Nginx配置，通常配置文件位于 /etc/nginx/sites-available/ 目录中。您可以创建一个新的文件，例如 flask_app：

```
sudo nano /etc/nginx/sites-available/flask_app
```
添加以下配置内容：

```
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
your_domain_or_IP：替换为您的域名或服务器的IP地址。
创建符号链接以启用该配置：

```
sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled/
```
测试Nginx配置并重新启动Nginx：

```
sudo nginx -t
sudo systemctl restart nginx
```
3. 使用Supervisor管理应用
为了确保Flask应用在服务器重启后自动运行，我们可以使用Supervisor来管理Gunicorn进程。

安装Supervisor：

```
sudo apt install supervisor
```
创建Supervisor配置文件： 编辑一个新的Supervisor配置文件，例如 /etc/supervisor/conf.d/flask_app.conf：

```
sudo nano /etc/supervisor/conf.d/flask_app.conf
```
添加以下配置：

```
[program:flask_app]
directory=/path/to/your/app
command=/path/to/your/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
autostart=true
autorestart=true
stderr_logfile=/var/log/flask_app.err.log
stdout_logfile=/var/log/flask_app.out.log
```
更新Supervisor并启动Flask应用：

```
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start flask_app
```

总结
Flask应用负责从电能表读取电压和电流，并通过网页显示。
Gunicorn运行Flask应用，充当WSGI服务器。
Nginx充当反向代理，将用户请求转发到Gunicorn。
Supervisor用于管理和确保应用在系统重启后自动启动。
这样，您的Linux服务器就可以通过Nginx和Gunicorn来提供电力监控的网页服务，并确保系统重启时自动恢复运行。

Nginx 测试输出中显示的警告 "conflicting server name '_' on 0.0.0.0:80, ignored" 表明在您的 Nginx 配置中有两个相互冲突的 server block，都在监听 0.0.0.0:80，并且使用了相同的 server 名称（_）。这种冲突可能导致您的配置文件没有按预期生效，Nginx 仍然提供默认的文件索引页面，而不是转发到您的 Flask 应用。

解决方案
要解决这个问题，确保 Nginx 只有一个服务器块在监听端口 80，并正确代理请求到 Gunicorn。

步骤 1：修改 Nginx 配置，确保唯一的 server block
编辑 Nginx 配置文件：
```
sudo nano /etc/nginx/sites-available/flask_app
```
确保您的配置如下，并且去掉其他可能冲突的 server block：
```
server {
    listen 80;
    server_name _;  # 匹配所有请求
    location / {
        proxy_pass http://127.0.0.1:6900;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
确保 proxy_pass 指向了 http://127.0.0.1:6900，这样请求可以被转发到 Gunicorn。

删除默认的 Nginx 配置文件，如果它也监听 80 端口（通常是 /etc/nginx/sites-enabled/default）：
```
sudo rm /etc/nginx/sites-enabled/default
```
步骤 2：测试并重新启动 Nginx
测试 Nginx 配置文件是否正确：
```
sudo nginx -t
```
确保没有任何错误或警告。
重新启动 Nginx：
```
sudo systemctl restart nginx
```
步骤 3：确认通过 Nginx 转发请求
本地测试：在 BeagleBone 上测试是否可以通过 Nginx 访问 Flask 应用：
```
curl http://127.0.0.1
```
如果配置正确，应该返回 Flask 应用的 HTML 页面，而不是文件索引页面。
外部设备测试：使用外部设备的浏览器，通过 BeagleBone 的 IP 地址访问，例如：

arduino
复制代码
```
http://192.168.120.17
```
这应该转发到 Gunicorn 并显示 Flask 应用页面。

总结
删除默认 Nginx 配置：删除 /etc/nginx/sites-enabled/default，以避免多个 server 块冲突。
确保唯一的 server 配置监听 80 端口，并正确代理到 Gunicorn。
重启 Nginx 后使用 curl 进行本地测试，确保返回正确的 Flask 页面，而不是 Nginx 的文件索引页面。
通过这些步骤，您应该能够解决配置冲突的问题，并使 Nginx 能够正确代理请求到您的 Flask 应用，从而实现通过 IP 访问。

重启 Flask 应用
Supervisor：

```
sudo supervisorctl restart flask_app
```
手动管理： 使用 Ctrl+C 停止当前运行的 Gunicorn 进程，然后重新启动：
```
gunicorn -w 1 -b 0.0.0.0:6900 app:app
```
