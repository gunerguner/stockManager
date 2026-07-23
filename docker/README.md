# stockManager Docker 部署

所有 Compose 与镜像定义集中在 **`docker/`** 目录。在仓库根目录执行 Compose 时，请使用 `-f docker/docker-compose.yml` 与 `--env-file docker/.env`（或先 `cd docker` 再 `--env-file .env`）。

## 获取代码

首次部署需从 Git 克隆本仓库（若已克隆，进入目录后执行 `git pull` 更新即可）。

HTTPS：

```bash
git clone https://github.com/gunerguner/stockManager.git
cd stockManager
```

SSH（需已配置 GitHub 公钥）：

```bash
git clone git@github.com:gunerguner/stockManager.git
cd stockManager
```

**仓库根目录**：即上述 `cd` 进入后的目录，应能看到 **`docker/`** 与内层 **`stockManager/`**（其中包含 `manage.py`）。下文所有 `docker compose` 命令均在该根目录执行（或先 `cd docker` 再按 README 内说明使用相对路径）。

若你使用 Fork 或私有镜像，将上述地址替换为自己的远程 URL 即可。

## 运行时架构

本编排包含三个服务：**`redis`**（缓存/队列等）、**`backend`**（Django + Gunicorn）、**`frontend`**（构建后的静态资源 + Nginx）。

| 组件 | 说明 |
|------|------|
| Redis | `redis:7-alpine`，持久化卷 `redis_data` |
| 后端 | 镜像由 `docker/Dockerfile.backend` 构建：**纯 Python**，仅 API + Django Admin 静态（`collectstatic`），**不含** Node / Umi 产物 |
| 前端 | 镜像由 `docker/Dockerfile.frontend` 构建：**唯一**一次 `ut run build`（默认 **Utoopack** bundler），Nginx 监听 **8080**（非 80） |

**前后端分工（与 carSales 一致）**：业务 SPA 与 `/static/umi.*` 仅存在于 **frontend** 镜像；**backend** 镜像内无 `front/dist`，改前端后须 `build frontend`，仅重建 backend **不会**更新 Umi 静态。

**构建上下文（`build.context`）为仓库根目录**（`docker-compose.yml` 中为 `..`），`dockerfile` 指向 `docker/Dockerfile.*`。仓库根 **`.dockerignore`** 在构建时生效，用于排除无关文件、加快构建。

## 目录说明

| 文件 | 作用 |
|------|------|
| `docker-compose.yml` | 编排 `redis`、`backend`、`frontend`；端口映射使用 `FRONTEND_PUBLISH_PORT`、`BACKEND_PUBLISH_PORT` 等宿主端口变量（见下文） |
| `Dockerfile.backend` | Python 依赖 + `collectstatic`（Admin）+ Gunicorn，无前端构建 |
| `Dockerfile.frontend` | Umi 构建 + Nginx 托管 SPA 静态并反代 `/api/` |
| `gunicorn.docker.conf.py` | 容器内 Gunicorn 配置（`bind 0.0.0.0:8000` 等） |
| `nginx.conf` | 前端容器内监听 **8080**；`/api/`、`/sys/admin/`、`/static/admin/` 反代至 `http://backend:8000` |
| `.env.example` | 环境变量模板，复制为 `docker/.env` 后按需修改 |

### 端口与映射

- **容器内**：前端 Nginx **8080**；后端 Gunicorn **8000**。
- **宿主机**：由 `docker/.env` 中的 **`FRONTEND_PUBLISH_PORT`**（默认 `8080`）、**`BACKEND_PUBLISH_PORT`**（默认 `8000`）映射到上述容器端口。修改 `.env` 后需重新 `up` 才生效。

## 与 carSales（Vben）部署差异

stockManager 前端为 **Umi**，**不依赖** `VITE_*` / `_app.config.js`：接口在代码里写死为同源 `/api/...`，构建配置在 `stockManager/front/config/config.ts`（如 `publicPath: '/static/'`），**没有** carSales 那种「`.dockerignore` 排除 `.env` 导致 API 地址为空」的问题。

同机部署时需注意：

| 问题类型 | stockManager | 处理 |
|----------|--------------|------|
| 静态资源 `/static/umi.*` 404 | 有（publicPath 与产物路径不一致） | `docker/nginx.conf` 中 `/static/` 使用 `alias`（已修复） |
| 接口 403 CSRF | 有（HTTPS 反代） | `docker/.env` 配置 `CSRF_TRUSTED_ORIGINS_EXTRA` |
| VITE / 标题 / mock API | **无** | 无需 `VITE_GLOB_API_URL` 或重建 frontend 传标题 |

## 前置条件

- 已安装 [Docker](https://docs.docker.com/get-docker/) 与 [Docker Compose V2](https://docs.docker.com/compose/)

## 配置

1. 复制环境变量文件：

   ```bash
   cp docker/.env.example docker/.env
   ```

2. 编辑 `docker/.env`，**至少**设置：

   - **`COMPOSE_PROJECT_NAME`**：默认 `stockmanager`（`.env.example` 已给出）。与 **carSales** 等同机部署时**勿删**；若从父目录执行 `docker compose -f 子路径/...`，更需固定项目名，否则后启动的栈会替换先启动栈的 `backend`/`frontend` 容器。
   - **`DJANGO_SECRET_KEY`**：生产环境务必使用足够长的随机字符串，勿使用示例值或空值。
   - **`DJANGO_DEBUG`**：生产建议 `false`。
   - **`CSRF_TRUSTED_ORIGINS_EXTRA`**：若通过域名或反向代理访问（HTTPS 或非常规端口），请填写 Django 要求的可信源，多个用英文逗号分隔，例如 `https://example.com,https://www.example.com:8443`。留空则仅依赖代码/默认配置中的设置。

3. 可选：`REDIS_URL`、`SQLITE_PATH`、`SQLITE_HOST_DIR`、`SQLITE_MUST_EXIST`、`RUN_MIGRATIONS_ON_START` 可按需求调整。若你通过外部拷入 sqlite 文件，推荐保持：

   - `SQLITE_PATH=/app/data/db.sqlite3`
   - `SQLITE_HOST_DIR=./sqlite-data`
   - `SQLITE_MUST_EXIST=true`
   - `RUN_MIGRATIONS_ON_START=false`

4. 若你已有完整 sqlite 文件（例如 `db.sqlite3`），请在首次启动前放到：

   - 宿主机路径：`<仓库根>/docker/sqlite-data/db.sqlite3`
   - 容器内对应路径：`/app/data/db.sqlite3`（由 `SQLITE_PATH` 指定）

   示例：

   ```bash
   mkdir -p docker/sqlite-data
   cp /path/to/your/db.sqlite3 docker/sqlite-data/db.sqlite3
   ```

## 数据卷

| 挂载/卷 | 用途 |
|------|------|
| `SQLITE_HOST_DIR:/app/data`（默认 `./sqlite-data:/app/data`，即宿主机 `docker/sqlite-data/`） | 存放 **`db.sqlite3`**（路径由 `SQLITE_PATH` 控制，默认 `/app/data/db.sqlite3`） |
| `redis_data` | Redis 持久化数据目录 |
| `log_data` | Django 应用日志目录（后端容器内 `/var/log/stockmanager/django`） |

删除卷会丢失对应数据（`redis_data`、`log_data`）；sqlite 使用的是宿主机目录挂载，建议定期备份 `docker/sqlite-data/db.sqlite3`。

## 重新上传 / 替换 SQLite 数据库

你日常若是**直接用本机/备份的 `db.sqlite3` 覆盖服务器上的库**（不是靠容器里 `migrate` 从空库长出来），按下面做即可。默认 `RUN_MIGRATIONS_ON_START=false`，**换库不会自动 migrate**，也**不会**自动清 Redis。

### 推荐步骤（仓库根目录）

1. **备份线上现有库**（建议先做）

   ```bash
   cp docker/sqlite-data/db.sqlite3 "docker/sqlite-data/db.sqlite3.bak.$(date +%Y%m%d%H%M%S)"
   ```

2. **停 backend，避免拷贝时 SQLite 被写入**

   ```bash
   docker compose -f docker/docker-compose.yml --env-file docker/.env stop backend
   ```

3. **覆盖文件**（文件名必须是 `db.sqlite3`，路径与 `.env` 中 `SQLITE_HOST_DIR` 一致）

   ```bash
   # 示例：把本地上传的库拷到挂载目录
   cp /path/to/uploaded/db.sqlite3 docker/sqlite-data/db.sqlite3
   # 确认权限对容器可读（常见：当前用户可读写即可）
   ls -l docker/sqlite-data/db.sqlite3
   ```

4. **启动 backend**

   ```bash
   docker compose -f docker/docker-compose.yml --env-file docker/.env start backend
   # 或：up -d backend
   ```

5. **按需执行迁移**（上传的库 schema **落后于当前代码**时必做；若该库已在同版本代码上 migrate 过则可跳过）

   ```bash
   docker compose -f docker/docker-compose.yml --env-file docker/.env exec backend python manage.py migrate
   docker compose -f docker/docker-compose.yml --env-file docker/.env exec backend python manage.py showmigrations backend
   ```

6. **清理 Redis 缓存**（换库后旧缓存可能仍是上一份库的数据，**建议每次换库都清**）

   - 浏览器：用 superuser 登录后走 Admin「清理缓存」，或  
   - API：`POST /api/clearCache`（需已登录且为 superuser）

### 注意

| 情况 | 处理 |
|------|------|
| 只换库、代码未变 | 覆盖文件 → 重启 backend → **清缓存**；一般不用 `build` |
| 换库 + 已 `git pull` 到更新代码 | 先按「更新代码后重新部署」`build`/`up`，再按本节换库；若新代码有 migration，对上传的库执行 `migrate` |
| 上传库比当前代码**更新**（库已跑过更新的 migration，镜像还是旧代码） | 先升级代码并重建 backend，再挂该库；不要用旧代码读新 schema |
| `SQLITE_MUST_EXIST=true` 且文件路径/文件名不对 | backend 会直接退出；检查 `docker/sqlite-data/db.sqlite3` 与 `.env` |

## Redis 缓存键与清理

本应用缓存经 django-redis 写入，键前缀为 **`stockmanager:1:`**（由 Django `KEY_PREFIX` + `VERSION` 组成，见 `stockManager/settings.py`）。示例：`stockmanager:1:user:1:operations`、`stockmanager:1:stock:price:sh600150`。

与同机其他服务共用 Redis 实例时（默认 `REDIS_URL=redis://redis:6379/1`），清理操作**仅删除此前缀下的 key**，不会 `FLUSHDB` 整库。

| 方式 | 说明 |
|------|------|
| Admin 页按钮 | 登录 superuser 后进入 `/admin`，点击「清理缓存」（仅 `access=admin` 可见） |
| API | `POST /api/clearCache`，需已登录且为 superuser；响应含 `deletedCount` |

排查缓存：`redis-cli -n 1 KEYS 'stockmanager:1:*'`（勿对生产库执行 `FLUSHDB`）。

**港股通汇率**：持仓含港股时，backend 需能访问新浪外汇 `hq.sinajs.cn`（拉 HKD/CNY 即期，须带 Referer）。若外网不可用，可依赖 Redis 中已有的 `fx:hkd_cny`（上次成功拉取后的缓存），否则汇总折算可能失败。

## 启动与停止

在**仓库根目录**执行：

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env build
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d
```

或在 `docker/` 目录下：

```bash
cd docker
docker compose --env-file .env build
docker compose --env-file .env up -d
```

停止并删除容器（**保留**数据卷）：

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env down
```

## 更新代码后重新部署

本地或服务器上**已有**按本文档部署的 Compose 栈时，拉取新代码后按下面步骤更新镜像并重启容器即可；**SQLite / Redis / 日志**在命名卷里，按默认 `down` **不会**删除卷内数据（除非你显式删卷）。

### 推荐流程（仓库根目录）

1. **拉取最新代码**

   ```bash
   cd stockManager   # 进入仓库根目录（与「获取代码」一节一致）
   git pull
   ```

2. **若 `docker/.env` 有新增变量**（例如 README 或 `.env.example` 里新加了配置），先编辑 `docker/.env` 再执行下一步。

3. **重新构建镜像并启动（或滚动替换容器）**

   ```bash
   docker compose -f docker/docker-compose.yml --env-file docker/.env build
   docker compose -f docker/docker-compose.yml --env-file docker/.env up -d
   ```

   也可一条命令在 `up` 时顺带构建（有变更的镜像会重建）：

   ```bash
   docker compose -f docker/docker-compose.yml --env-file docker/.env up -d --build
   ```

4. **数据库迁移策略（已改为可选）**：

   - 默认 `RUN_MIGRATIONS_ON_START=false`：容器启动**不自动**执行 `migrate`（适合你外部拷入完整 sqlite 文件）。
   - 默认 `SQLITE_MUST_EXIST=true`：若 `SQLITE_PATH` 指向的文件不存在，容器会直接报错退出，避免意外创建空库。
   - 需要自动迁移时，可在 `docker/.env` 里设 `RUN_MIGRATIONS_ON_START=true` 后重启容器。

   手工执行迁移命令（按需）：

   ```bash
   docker compose -f docker/docker-compose.yml --env-file docker/.env exec backend python manage.py migrate
   ```

5. **看日志确认**（可选）：

   ```bash
   docker compose -f docker/docker-compose.yml --env-file docker/.env logs -f --tail=100 backend
   ```

### 何时必须 `build`

- 改了 **Python / 前端源码**、`requirements.txt`、`Dockerfile*`、`nginx.conf`、入口脚本等会影响镜像内容的文件 → 需要 **`build` 或 `up -d --build`**。
- 只改了 **`docker/.env`** 或 **`docker-compose.yml` 的环境/端口** → 通常 **`up -d` 即可**（必要时加 `--force-recreate` 让容器重新读环境）。

### 依赖或构建异常时

若怀疑 Docker 构建缓存导致旧层残留，可对本项目做一次无缓存构建（耗时更长）：

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env build --no-cache
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d
```

## 统一入口：宿主机 Nginx 反代示例

若希望由宿主机 Nginx 统一对外（HTTPS、域名），可将流量反代到 Compose 映射出的前端端口（即 `FRONTEND_PUBLISH_PORT` 对应的地址）。前端容器内的 Nginx 已把 **`/api/`**、**`/sys/admin/`**、**`/static/admin/`** 转到后端，因此**浏览器只需访问前端**即可，无需单独暴露后端路径给公网（是否仍映射 `BACKEND_PUBLISH_PORT` 可按运维需要决定）。

示例（假设前端映射在 `127.0.0.1:8080`，且 `server_name` 与 `CSRF_TRUSTED_ORIGINS_EXTRA` 一致）：

```nginx
server {
    listen 443 ssl;
    server_name stock.example.com;

    # ssl_certificate /path/to/fullchain.pem;
    # ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

要点：`proxy_set_header Host` 与 `X-Forwarded-Proto` 会影响 Django 的 Host/CSRF 校验，请与 `CSRF_TRUSTED_ORIGINS_EXTRA` 及 `ALLOWED_HOSTS` 策略一并核对。

## 如何验证

以下默认在仓库根目录执行，且已配置 `docker/.env`。若改过端口，请将示例中的 `8080`、`8000` 换为你的 **`FRONTEND_PUBLISH_PORT`**、**`BACKEND_PUBLISH_PORT`**。

### 1. 容器状态

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env ps
```

期望：`redis`、`backend`、`frontend` 均为运行中；`redis` 可为 `healthy`。

### 2. 日志

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env logs --tail=80 redis
docker compose -f docker/docker-compose.yml --env-file docker/.env logs --tail=80 backend
docker compose -f docker/docker-compose.yml --env-file docker/.env logs --tail=80 frontend
```

### 3. curl 探测

```bash
# 前端（静态或入口页，视构建产物而定）
curl -fsS -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:${FRONTEND_PUBLISH_PORT:-8080}/"

# 经前端 Nginx 反代的 API 前缀（按项目实际路径调整）
curl -fsS -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:${FRONTEND_PUBLISH_PORT:-8080}/api/" || true

# 直连后端（若已映射 BACKEND_PUBLISH_PORT）
curl -fsS -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:${BACKEND_PUBLISH_PORT:-8000}/" || true
```

若 `curl` 报连接拒绝，检查端口是否与 `.env` 一致、容器是否已启动。

## 常见问题与排查

| 现象 | 可能原因与处理 |
|------|----------------|
| `backend` 启动失败，日志提示缺少 `DJANGO_SECRET_KEY` | 在 `docker/.env` 中设置非空的 `DJANGO_SECRET_KEY` 后重新 `up`。 |
| `backend` 启动失败，提示 `SQLITE_MUST_EXIST=true but sqlite file not found` | 先确认宿主机文件是否存在：`docker/sqlite-data/db.sqlite3`，并检查 `.env` 中 `SQLITE_HOST_DIR` 与 `SQLITE_PATH` 是否对应。 |
| 直接上传/覆盖了 `db.sqlite3` 后数据或列表异常 | 见上文「重新上传 / 替换 SQLite 数据库」：停 backend → 覆盖 → 启动 → 按需 `migrate` → **清 Redis 缓存**。 |
| 浏览器登录或表单报 **403 CSRF** | 检查访问 URL 是否与 **`CSRF_TRUSTED_ORIGINS_EXTRA`**、反向代理的 `X-Forwarded-Proto` / `Host` 一致；HTTPS 站点需写 `https://` 源。 |
| 前端空白或接口 502 | 看 `frontend`、`backend` 日志；确认 `proxy_pass http://backend:8000` 与后端实际监听一致；确认 `depends_on` 后后端已就绪。 |
| **`/static/umi.*.css` 等 404** | 生产 `publicPath` 为 `/static/`，但 Umi 产物在 `dist` 根目录。前端 Nginx 须用 `alias` 将 `/static/` 映射到 html 根（见 `docker/nginx.conf`）；改配置后需 `build` 并重建 `frontend` 容器。 |
| `redis` 不健康导致 `backend` 不启动 | 检查 `redis` 日志与卷权限；确认 `REDIS_URL` 中主机名为 `redis`、端口 `6379`。 |
| 数据库或日志丢失 | 勿随意 `docker volume rm`；`sqlite_data`、`log_data` 删除后需从备份恢复。 |
| 构建很慢或镜像很大 | 确认仓库根 **`.dockerignore`** 已排除 `node_modules`、`__pycache__` 等。`Dockerfile.frontend` 已拆层（先 `ut install` 再 `COPY` 源码），并把 utoo cache 与 `node_modules` 放在同一 BuildKit mount（`/deps`），避免跨设备 hardlink 的 EXDEV WARN。**仅改前端业务代码**时通常只重跑 `ut run build`（Utoopack），**改 `package-lock.json` 才会重装依赖**。查看各步耗时：`docker build --progress=plain -f docker/Dockerfile.frontend .`；勿滥用 `--no-cache`。 |

## 安全提示

- **不要将 `docker/.env` 提交到 Git**（已在 `.dockerignore` 中忽略构建传入，但仍勿入库）。
- 生产环境关闭 **`DJANGO_DEBUG`**，使用强随机 **`DJANGO_SECRET_KEY`**，并正确配置 **`CSRF_TRUSTED_ORIGINS_EXTRA`** 与 `ALLOWED_HOSTS`（后者在 Django `settings` 中配置）。
