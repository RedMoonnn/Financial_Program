# 东方财富数据采集与分析平台 - 前端

基于 React + TypeScript + Vite + Ant Design 构建的现代化前端应用。

## 技术栈

- **React 18** - 用户界面库
- **TypeScript** - 类型安全的 JavaScript
- **Vite** - 快速构建工具
- **Ant Design** - UI 组件库
- **ECharts** - 数据可视化图表
- **Axios** - HTTP 客户端
- **React Router** - 路由管理

## 开发环境

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 功能特性

- 📊 多级 Tab 资金流数据展示
- 📈 ECharts 图表可视化
- 🔄 手动数据采集更新
- 💬 AI 智能对话助手
- 📋 历史报告管理
- 👤 用户中心管理

## 项目结构

```
src/
├── components/     # 通用组件
├── pages/         # 页面组件
├── auth.ts        # 认证工具
├── store.ts       # 状态管理
├── App.tsx        # 主应用
└── main.tsx       # 入口文件
```

## 开发说明

- 使用 Vite 代理配置，API 请求自动转发到后端
- 支持热重载和快速开发
- 集成 TypeScript 类型检查
- 使用 Ant Design 组件库保持 UI 一致性
