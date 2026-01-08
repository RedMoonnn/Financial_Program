#!/bin/bash
# MySQL 初始化脚本：允许远程连接
# 此脚本会在 MySQL 容器首次启动时自动执行（数据目录为空时）
# 从环境变量读取密码并设置远程访问权限

set -e

# 等待 MySQL 启动
until mysqladmin ping -h localhost --silent; do
    sleep 1
done

# 从环境变量读取配置
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-$MYSQL_ROOT_PASSWORD}"

if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
    echo "错误: MYSQL_ROOT_PASSWORD 环境变量未设置"
    exit 1
fi

echo "正在设置 MySQL 远程访问权限..."

mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<EOF
-- 创建或更新用户，允许从任何主机连接（使用 caching_sha2_password，MySQL 8.0 默认）
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO '${MYSQL_USER}'@'%' WITH GRANT OPTION;

-- 创建 root@'%' 允许远程访问（使用 caching_sha2_password，MySQL 8.0 默认）
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- 创建 mysql@'%' 用户（使用 caching_sha2_password，MySQL 8.0 默认）
CREATE USER IF NOT EXISTS 'mysql'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'mysql'@'%' WITH GRANT OPTION;

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示用户信息
SELECT User, Host, plugin FROM mysql.user WHERE User IN ('${MYSQL_USER}', 'root', 'mysql') AND Host='%';
EOF

echo "MySQL 用户 '${MYSQL_USER}' 和 root 已设置远程访问权限"
