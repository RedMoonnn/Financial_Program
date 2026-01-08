#!/bin/bash
# 手动设置 MySQL 远程用户脚本
# 如果数据已存在，使用此脚本手动创建用户
# 用法: ./scripts/setup-mysql-user.sh

set -e

# 从 .env 文件读取环境变量（如果存在）
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

MYSQL_PASSWORD="${MYSQL_PASSWORD:-123456}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_ROOT_PASSWORD="${MYSQL_PASSWORD}"

echo "正在创建 MySQL 用户 '$MYSQL_USER' 和 root 并允许远程访问..."

docker compose exec -T mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<EOF
-- 创建或更新用户，允许从任何主机连接（使用 mysql_native_password 兼容 HeidiSQL 等客户端）
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED WITH mysql_native_password BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO '${MYSQL_USER}'@'%' WITH GRANT OPTION;

-- 创建 root@'%' 允许远程访问（使用 mysql_native_password 兼容 HeidiSQL 等客户端）
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- 创建 mysql@'%' 用户（使用 mysql_native_password 兼容 HeidiSQL 等客户端）
CREATE USER IF NOT EXISTS 'mysql'@'%' IDENTIFIED WITH mysql_native_password BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'mysql'@'%' WITH GRANT OPTION;

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示用户信息
SELECT User, Host, plugin FROM mysql.user WHERE User IN ('${MYSQL_USER}', 'root', 'mysql') AND Host='%';
EOF

echo "完成！用户 '$MYSQL_USER' 和 root 已创建并允许远程访问"
