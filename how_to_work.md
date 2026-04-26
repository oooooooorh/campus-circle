🚀 “校园圈”全栈项目 Azure 部署实战总结与运维指南
📁 一、 项目整体架构
本项目采用前后端分离架构，部署在微软 Azure 云平台上：
前端 (Vue 3)：部署在 Azure Static Web Apps (静态 Web 应用)。通过 GitHub Actions 实现自动化 CI/CD 部署，拥有全球 CDN 加速。
后端 (FastAPI + Playwright + SQLite)：打包为 Docker 镜像，存储在 Azure Container Registry (ACR)，最终运行在 Azure Web App for Containers (应用服务) 上。
🛠️ 二、 踩坑记录与核心技术点 (复盘总结)
在本次部署中，我们成功解决了一系列经典的线上环境配置问题，这些经验非常宝贵：
Docker 环境与系统兼容问题
问题：Windows 安装 Docker Desktop 提示 WSL 版本过低。
解决：通过命令行 wsl --update 或微软官网手动下载安装 WSL2 Linux 内核更新包解决。
前端网络请求错误 (ERR_CONNECTION_REFUSED)
问题：前端部署上线后，无法获取数据。
解决：查出前端代码打包时忘记修改 API 基础路径。将 127.0.0.1:8000 修改为 Azure 后端分配的公网 HTTPS 域名。
前后端跨域安全限制 (CORS Error)
问题：前端域名访问后端域名时被浏览器拦截。
解决：由于后端运行在 Docker 容器内，Azure 门户的 CORS 设置无法穿透容器。最终在 FastAPI 的 main.py 中引入并配置 CORSMiddleware，放行了跨域请求。
SQLite 数据库多进程死锁崩溃 (table already exists)
问题：后端容器启动时报 Application Error，查看日志流发现多个进程同时尝试建表导致 SQLite 报错。
解决：修改 Dockerfile 的启动命令，将多进程的 Gunicorn 替换为单进程的 Uvicorn (CMD["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])，完美适配了 SQLite 的单线程特性。
Azure 容器端口映射 (WEBSITES_PORT)
关键点：Azure 默认监听容器的 80 端口，但 FastAPI 默认运行在 8000 端口。必须在 Azure Web App 的环境变量中显式添加 WEBSITES_PORT = 8000 才能让外部流量正确打入容器。
<br>
🔄 三、 日常维护与更新指南（下一次怎么更新代码？）
当项目上线后，你不可避免地需要修改 Bug 或者开发新功能。请保存好以下流程，以后每次更新代码照做即可。
🎨 场景 A：我只修改了“前端代码” (Vue)
前端的更新是最舒服的，因为我们配置了 GitHub Actions，它实现了“全自动部署”。
在本地电脑修改你的 Vue 代码。
打开终端（确保在你的项目根目录下），执行 Git 三连：
code
Bash
git add .
git commit -m "update: 描述你修改了什么前端功能"
git push github main
喝口水，等 2 分钟。GitHub Actions 会自动触发打包并上传到 Azure。
刷新你的前端网页，新功能就生效了！
⚙️ 场景 B：我修改了“后端代码” (FastAPI/Python)
后端的更新需要重新打包 Docker 镜像并推送到云端。流程如下：
第一步：本地重新打包镜像
打开终端，进入你的 backend 文件夹，执行构建命令（请把 campusregistry 换成你的 ACR 名字，注意最后的一个点 . 不能漏）：
code
Bash
# 建议一直使用 v1 标签去覆盖旧镜像，这样最省事
docker build -t campusregistry.azurecr.io/campus-backend:v1 .
第二步：推送镜像到 Azure 仓库
code
Bash
docker push campusregistry.azurecr.io/campus-backend:v1
(如果提示未登录，请先执行 az acr login --name campusregistry 或使用 docker login 手动输入账号密码)
第三步：重启 Azure 上的后端服务 (必须做)
由于镜像更新了，服务器不会自己知道，我们需要“踹”它一脚让它重新拉取：
登录 Azure 门户。
进入你的 campus-api (应用服务 Web App) 页面。
点击页面顶部的 “重启” (Restart) 按钮。
等 1-2 分钟，新的后端逻辑就生效了！
🚨 场景 C：新增了前后端联调的接口
如果你在后端写了一个新接口，前端也写了对应页面的调用逻辑：
先更新后端：按照【场景 B】把后端 Docker 传上去并重启。
再验证后端：去 https://campus-api-xxxx.../docs 看看新接口有没有刷出来。
最后更新前端：按照【场景 A】把前端推送到 GitHub。
(顺序不要反了，否则前端先上去会因为找不到后端新接口而报错)
💡 附录：高频排错指令
如果你发现后端更新后网页挂了，想看原因：
去 Azure 门户 -> campus-api -> 左侧菜单 -> “日志流” (Log stream)，看黑底白字的报错。
如果你在本地想看 Docker 镜像有没有打包成功：执行 docker images。