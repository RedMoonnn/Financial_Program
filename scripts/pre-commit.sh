#!/bin/bash
# Pre-commit hook 脚本
# 在 git commit 前运行代码检查

# 不使用 set -e，因为我们需要收集所有错误
set +e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}运行 pre-commit 检查...${NC}"

# 获取项目根目录
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# 确保用户 bin 目录在 PATH 中
export PATH="$HOME/.local/bin:$PATH"

# 检查是否有变更的文件
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$CHANGED_FILES" ]; then
    echo -e "${YELLOW}没有暂存的文件，跳过检查${NC}"
    exit 0
fi

ERRORS=0

# 检查 Python 文件
PYTHON_FILES=$(echo "$CHANGED_FILES" | grep -E '\.py$' || true)
if [ -n "$PYTHON_FILES" ]; then
    echo -e "${GREEN}检查 Python 文件...${NC}"

    # 检查 ruff 是否安装（检查多个可能的位置）
    RUFF_CMD=""
    if command -v ruff &> /dev/null; then
        RUFF_CMD="ruff"
    elif [ -f "$HOME/.local/bin/ruff" ]; then
        RUFF_CMD="$HOME/.local/bin/ruff"
    fi

    if [ -z "$RUFF_CMD" ]; then
        echo -e "${YELLOW}ruff 未安装，跳过 Python 检查${NC}"
        echo -e "${YELLOW}安装命令: pip install --user ruff${NC}"
    else
        # 运行 ruff check（只检查暂存的 Python 文件）
        echo "运行 ruff check..."
        RUFF_CHECK_OUTPUT=$($RUFF_CMD check backend/ --fix 2>&1)
        RUFF_CHECK_EXIT=$?
        if [ $RUFF_CHECK_EXIT -ne 0 ]; then
            echo "$RUFF_CHECK_OUTPUT"
            echo -e "${RED}ruff check 失败，请修复错误后重试${NC}"
            ERRORS=$((ERRORS + 1))
        fi

        # 运行 ruff format（只检查暂存的 Python 文件）
        echo "运行 ruff format..."
        RUFF_FORMAT_OUTPUT=$($RUFF_CMD format backend/ --check 2>&1)
        RUFF_FORMAT_EXIT=$?
        if [ $RUFF_FORMAT_EXIT -ne 0 ]; then
            echo "$RUFF_FORMAT_OUTPUT"
            echo -e "${RED}ruff format 失败，运行 '$RUFF_CMD format backend/' 格式化代码${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    fi
fi

# 检查前端文件
FRONTEND_FILES=$(echo "$CHANGED_FILES" | grep -E '\.(ts|tsx|js|jsx)$' || true)
if [ -n "$FRONTEND_FILES" ]; then
    echo -e "${GREEN}检查前端文件...${NC}"

    cd frontend

    # 检查是否有 node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}node_modules 不存在，跳过前端检查${NC}"
        echo -e "${YELLOW}运行 'npm install' 安装依赖${NC}"
    else
        # 检查是否有 eslint
        if [ -f "node_modules/.bin/eslint" ]; then
            echo "运行 eslint --fix..."

            # 运行 lint:fix (npm 脚本) 或者直接调用 eslint --fix
            if npm run | grep -q "lint:fix"; then
                ESLINT_OUTPUT=$(npm run lint:fix 2>&1)
            else
                ESLINT_OUTPUT=$(npx eslint src/ --ext .ts,.tsx,.js,.jsx --fix 2>&1)
            fi

            ESLINT_EXIT=$?

            # 检查是否有文件被修改（ESLint 修复了文件）
            # 注意：这里假设用户在 commit 前已将所有修改暂存。如果有原本未暂存的修改，这里也会触发。
            # 这是为了防止 "修复了但未提交" 的情况。
            if ! git diff --quiet src/; then
                echo "$ESLINT_OUTPUT"
                echo -e "${YELLOW}⚠️  ESLint 自动修复了一些代码。${NC}"
                echo -e "${RED}❌ 请运行 'git add .' 将修复后的代码加入暂存区，然后重新提交。${NC}"
                ERRORS=$((ERRORS + 1))
            elif [ $ESLINT_EXIT -ne 0 ]; then
                echo "$ESLINT_OUTPUT"
                echo -e "${RED}eslint 检查失败（无法自动修复），请手动修复错误后重试${NC}"
                ERRORS=$((ERRORS + 1))
            else
                echo -e "${GREEN}ESLint 检查通过${NC}"
            fi
        else
            echo -e "${YELLOW}eslint 未安装，跳过前端检查${NC}"
        fi
    fi

    cd ..
fi

# 如果有错误，阻止提交
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ Pre-commit 检查失败，请修复上述错误后重试${NC}"
    echo -e "${YELLOW}提示: 可以使用 --no-verify 跳过检查（不推荐）${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Pre-commit 检查通过${NC}"
exit 0
