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
| 后端 | 镜像由 `docker/Dockerfile.backend` 构建，容器内 Gunicorn 监听 **8000** |
| 前端 | 镜像由 `docker/Dockerfile.frontend` 构建，容器内 Nginx 监听 **8080**（非 80） |

**构建上下文（`build.context`）为仓库根目录**（`docker-compose.yml` 中为 `..`），`dockerfile` 指向 `docker/Dockerfile.*`。仓库根 **`.dockerignore`** 在构建时生效，用于排除无关文件、加快构建。

## 目录说明

| 文件 | 作用 |
|------|------|
| `docker-compose.yml` | 编排 `redis`、`backend`、`frontend`；端口映射使用 `FRONTEND_PUBLISH_PORT`、`BACKEND_PUBLISH_PORT` 等宿主端口变量（见下文） |
| `Dockerfile.backend` | Python 依赖 + Gunicorn 启动 Django |
| `Dockerfile.frontend` | 前端构建 + Nginx 托管静态与反代 |
| `gunicorn.docker.conf.py` | 容器内 Gunicorn 配置（`bind 0.0.0.0:8000` 等） |
| `nginx.conf` | 前端容器内监听 **8080**；`/api/`、`/sys/admin/`、`/static/admin/` 反代至 `http://backend:8000` |
| `.env.example` | 环境变量模板，复制为 `docker/.env` 后按需修改 |

### 端口与映射

- **容器内**：前端 Nginx **8080**；后端 Gunicorn **8000**。
- **宿主机**：由 `docker/.env` 中的 **`FRONTEND_PUBLISH_PORT`**（默认 `8080`）、**`BACKEND_PUBLISH_PORT`**（默认 `8000`）映射到上述容器端口。修改 `.env` 后需重新 `up` 才生效。

## 前置条件

- 已安装 [Docker](https://docs.docker.com/get-docker/) 与 [Docker Compose V2](https://docs.docker.com/compose/)

## 配置

1. 复制环境变量文件：

   ```bash
   cp docker/.env.example docker/.env
   ```

2. 编辑 `docker/.env`，**至少**设置：

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
| 浏览器登录或表单报 **403 CSRF** | 检查访问 URL 是否与 **`CSRF_TRUSTED_ORIGINS_EXTRA`**、反向代理的 `X-Forwarded-Proto` / `Host` 一致；HTTPS 站点需写 `https://` 源。 |
| 前端空白或接口 502 | 看 `frontend`、`backend` 日志；确认 `proxy_pass http://backend:8000` 与后端实际监听一致；确认 `depends_on` 后后端已就绪。 |
| `redis` 不健康导致 `backend` 不启动 | 检查 `redis` 日志与卷权限；确认 `REDIS_URL` 中主机名为 `redis`、端口 `6379`。 |
| 数据库或日志丢失 | 勿随意 `docker volume rm`；`sqlite_data`、`log_data` 删除后需从备份恢复。 |
| 构建很慢或镜像很大 | 确认仓库根 **`.dockerignore`** 已排除 `node_modules`、`__pycache__` 等；不要向构建上下文提交大文件。 |

## 安全提示

- **不要将 `docker/.env` 提交到 Git**（已在 `.dockerignore` 中忽略构建传入，但仍勿入库）。
- 生产环境关闭 **`DJANGO_DEBUG`**，使用强随机 **`DJANGO_SECRET_KEY`**，并正确配置 **`CSRF_TRUSTED_ORIGINS_EXTRA`** 与 `ALLOWED_HOSTS`（后者在 Django `settings` 中配置）。
