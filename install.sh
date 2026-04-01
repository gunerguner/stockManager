#!/bin/bash

# StockManager 自动化安装脚本
# 自动化完成 stockManager 项目的完整部署流程

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 项目路径（默认当前目录）
PROJECT_DIR="${1:-$(pwd)}"
APP_DIR=""
FRONT_DIR=""
ENV_FILE=""
ENV_EXAMPLE_FILE=""
REQUIREMENTS_FILE=""
VENV_DIR=""

echo "=========================================="
echo "  StockManager 自动化安装脚本"
echo "=========================================="
echo ""
log_info "项目目录：$PROJECT_DIR"
log_info "安装入口目录：$PROJECT_DIR"
echo ""

# 自动识别项目目录（兼容在仓库根目录或上级目录执行）
if [ -f "$PROJECT_DIR/manage.py" ]; then
    APP_DIR="$PROJECT_DIR"
elif [ -f "$PROJECT_DIR/stockManager/manage.py" ]; then
    APP_DIR="$PROJECT_DIR/stockManager"
else
    log_error "未找到 manage.py，请在项目根目录执行，或传入正确项目路径"
    exit 1
fi

FRONT_DIR="$APP_DIR/front"
ENV_FILE="$APP_DIR/stockManager/.env"
ENV_EXAMPLE_FILE="$APP_DIR/stockManager/.env.example"
REQUIREMENTS_FILE="$APP_DIR/requirements.txt"
VENV_DIR="$APP_DIR/.venv"

log_info "项目目录：$APP_DIR"
log_info "前端目录：$FRONT_DIR"

# ===========================================
# 辅助函数
# ===========================================

# 获取 Python 命令（兼容 python 和 python3）
get_python_cmd() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        echo "python"
    else
        echo ""
    fi
}

# 获取 pip 命令（兼容 pip 和 pip3）
get_pip_cmd() {
    # 使用 python -m pip 更可靠，避免 python 和 pip 版本不一致
    echo "$PYTHON_CMD -m pip"
}

# 创建并激活 venv
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        log_info "正在创建 Python 虚拟环境：$VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
    else
        log_success "Python 虚拟环境已存在：$VENV_DIR"
    fi

    # 激活虚拟环境（让后续 python/pip 命令走 venv）
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"

    PYTHON_CMD="python"
    PIP_CMD=$(get_pip_cmd)
    log_success "已激活虚拟环境：$VENV_DIR"
}

# 安装 Homebrew
install_homebrew() {
    if ! command -v brew &> /dev/null; then
        log_info "正在安装 Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        # 根据芯片架构添加 PATH
        if [ "$(uname -m)" = "arm64" ]; then
            export PATH="/opt/homebrew/bin:$PATH"
        else
            export PATH="/usr/local/bin:$PATH"
        fi
        log_success "Homebrew 安装完成"
    else
        log_success "Homebrew 已安装"
    fi

    # 设置 Homebrew 国内镜像源
    log_info "正在设置 Homebrew 镜像源..."
    export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
    export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.ustc.edu.cn/homebrew-core.git"
    export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"

    # 重新设置 brew 和 core 远程
    cd "$(brew --repo)"
    git remote set-url origin https://github.com/Homebrew/brew.git 2>/dev/null || true

    # 临时设置环境变量用于当前会话
    log_success "Homebrew 镜像源已配置"
}

# 安装 nvm
install_nvm() {
    if [ ! -d "$HOME/.nvm" ]; then
        log_info "正在安装 nvm..."
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        log_success "nvm 安装完成"
    else
        log_success "nvm 已安装"
    fi

    # 加载 nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
}

# 安装指定版本的 Node.js
install_node_version() {
    local version=$1
    # 检查当前 nvm 是否已安装该版本
    if nvm ls "$version" &> /dev/null; then
        log_success "Node.js $version 已安装"
    else
        log_info "正在安装 Node.js $version..."
        nvm install "$version"
    fi
    nvm use "$version"
    log_success "Node.js $version 已激活：$(node -v)"
}

# ===========================================
# 第 1 步：检查并安装系统依赖
# ===========================================
echo ""
echo "=========================================="
echo "  步骤 1: 检查系统依赖"
echo "=========================================="

# 检查 Python
PYTHON_CMD=$(get_python_cmd)
if [ -z "$PYTHON_CMD" ]; then
    log_error "Python 未安装，请先安装 Python (版本 >= 3.11)"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    log_error "Python 版本需要 >= 3.11，当前版本：$PYTHON_VERSION"
    exit 1
fi
log_success "Python 版本：$PYTHON_VERSION ($PYTHON_CMD)"

# 创建并切换到 venv
setup_venv

# 检查 git
if ! command -v git &> /dev/null; then
    install_homebrew
    brew install git
fi
log_success "git 已安装：$(git --version)"

# 检查 redis
if ! command -v redis-server &> /dev/null; then
    install_homebrew
    brew install redis
fi
log_success "redis 已安装：$(redis-server --version | head -1)"

# ===========================================
# 第 2 步：安装 Node.js 和 pnpm (使用 nvm)
# ===========================================
echo ""
echo "=========================================="
echo "  步骤 2: 安装 Node.js 和 pnpm"
echo "=========================================="

# 安装 nvm
install_nvm

# 安装 Node.js 20
install_node_version 20

# 检查 Node.js 版本
NODE_VERSION=$(node -v 2>/dev/null | cut -d'v' -f2)
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
if [ "$NODE_MAJOR" -lt 20 ]; then
    log_error "Node.js 版本需要 >= 20，当前版本：$NODE_VERSION"
    exit 1
fi
log_success "Node.js 版本：$NODE_VERSION"

# 安装 pnpm
if ! command -v pnpm &> /dev/null; then
    log_info "正在安装 pnpm..."
    npm install -g pnpm
fi
log_success "pnpm 已安装：$(pnpm -v)"

# 设置 npm/pnpm 国内镜像源
log_info "正在设置 npm/pnpm 镜像源..."
npm config set registry https://registry.npmmirror.com
pnpm config set registry https://registry.npmmirror.com
log_success "npm/pnpm 镜像源已配置 (npmmirror)"

# ===========================================
# 第 3 步：拉取最新代码
# ===========================================
echo ""
echo "=========================================="
echo "  步骤 3: 更新代码"
echo "=========================================="

GIT_ROOT=$(git -C "$APP_DIR" rev-parse --show-toplevel 2>/dev/null || true)
if [ -n "$GIT_ROOT" ] && [ -d "$GIT_ROOT/.git" ]; then
    log_info "正在拉取最新代码..."
    git -C "$GIT_ROOT" pull --ff-only
    log_success "代码更新完成"
else
    log_error "当前目录不是 Git 仓库，无法 pull 最新代码"
    exit 1
fi

# ===========================================
# 第 4 步：安装 Python 依赖
# ===========================================
echo ""
echo "=========================================="
echo "  步骤 4: 安装 Python 依赖"
echo "=========================================="

if [ -f "$REQUIREMENTS_FILE" ]; then
    log_info "正在安装 Python 依赖..."
    $PIP_CMD install --upgrade pip
    $PIP_CMD install -r "$REQUIREMENTS_FILE"
    log_success "Python 依赖安装完成"
else
    log_error "未找到 requirements.txt 文件：$REQUIREMENTS_FILE"
    exit 1
fi

# ===========================================
# 第 5 步：安装前端依赖并构建
# ===========================================
echo ""
echo "=========================================="
echo "  步骤 5: 安装前端依赖并构建"
echo "=========================================="

if [ -d "$FRONT_DIR" ]; then
    log_info "正在安装前端依赖 (pnpm install)..."
    cd "$FRONT_DIR"
    pnpm install

    log_info "正在构建前端 (pnpm run build)..."
    pnpm run build
    cd "$APP_DIR"
    log_success "前端构建完成"
else
    log_error "前端目录不存在：$FRONT_DIR"
    exit 1
fi

# ===========================================
# 第 6 步：创建 .env 文件
# ===========================================
echo ""
echo "=========================================="
echo "  步骤 6: 创建 .env 配置文件"
echo "=========================================="

if [ -f "$ENV_FILE" ]; then
    log_success ".env 文件已存在"
elif [ -f "$ENV_EXAMPLE_FILE" ]; then
    log_info "正在从 .env.example 复制创建 .env 文件..."
    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"

    # 生成 Django SECRET KEY 并更新到 .env 文件
    DJANGO_SECRET_KEY=$($PYTHON_CMD -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    sed -i.bak "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY|" "$ENV_FILE"
    rm -f "$ENV_FILE.bak"

    log_success ".env 文件已创建：$ENV_FILE"
else
    log_info "正在创建 .env 文件..."

    # 生成 Django SECRET KEY
    DJANGO_SECRET_KEY=$($PYTHON_CMD -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

    # 创建 .env 文件
    cat > "$ENV_FILE" << EOF
# Django SECRET KEY (生产环境必须修改为随机值)
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

# Django 调试模式
DJANGO_DEBUG=true

# Redis URL（可选，默认为 redis://127.0.0.1:6379/1）
REDIS_URL=redis://127.0.0.1:6379/1
EOF

    log_success ".env 文件已创建：$ENV_FILE"
fi

# ===========================================
# 第 7 步：数据库迁移
# ===========================================
echo ""
echo "=========================================="
echo "  步骤 7: 数据库迁移"
echo "=========================================="

cd "$APP_DIR"

log_info "正在执行 makemigrations..."
$PYTHON_CMD manage.py makemigrations

log_info "正在执行 migrate..."
$PYTHON_CMD manage.py migrate

log_success "数据库迁移完成"

# ===========================================
# 第 8 步：创建超级用户
# ===========================================
echo ""
echo "=========================================="
echo "  步骤 8: 创建超级用户"
echo "=========================================="

SUPERUSER_COUNT=$($PYTHON_CMD manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(is_superuser=True).count())")
if [ "$SUPERUSER_COUNT" -gt 0 ]; then
    log_warn "检测到已存在超级用户，跳过创建步骤"
else
    log_info "将进入交互式创建超级用户流程，请按提示输入用户名、邮箱和密码"
    $PYTHON_CMD manage.py createsuperuser
    log_success "超级用户创建完成"
fi

# ===========================================
# 第 9 步：启动 Redis
# ===========================================
echo ""
echo "=========================================="
echo "  步骤 9: 启动 Redis 服务器"
echo "=========================================="

if pgrep -x "redis-server" > /dev/null; then
    log_success "Redis 服务器已运行"
else
    OS_NAME="$(uname -s)"
    log_info "正在启动 Redis 服务器 (系统: $OS_NAME)..."

    if [ "$OS_NAME" = "Darwin" ] && command -v brew &> /dev/null; then
        brew services start redis || true
    elif [ "$OS_NAME" = "Linux" ]; then
        redis-server --daemonize yes || true
    fi

    # 兜底启动方式（兼容不支持 --daemonize 的环境）
    if ! pgrep -x "redis-server" > /dev/null; then
        nohup redis-server > /tmp/redis-server.log 2>&1 &
    fi

    sleep 2
    if pgrep -x "redis-server" > /dev/null; then
        log_success "Redis 服务器已启动"
    else
        log_warn "Redis 启动失败，请手动检查（日志: /tmp/redis-server.log）"
    fi
fi

# ===========================================
# 完成
# ===========================================
echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""
log_success "所有步骤已完成"
echo ""
echo "启动项目:"
echo "  cd $APP_DIR"
echo "  $PYTHON_CMD manage.py runserver"
echo ""
echo "或使用后台启动:"
echo "  nohup $PYTHON_CMD manage.py runserver > server.log 2>&1 &"
echo ""
echo "访问地址：http://127.0.0.1:8000"
echo "管理后台：http://127.0.0.1:8000/admin"
echo ""
