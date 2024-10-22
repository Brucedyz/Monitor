
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
