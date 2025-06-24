# Node.js、npm、nvm 工具与原理详解

## 0. 新手入门：三者的关系与版本管理

### 他们是什么关系？
- **Node.js** 是 JavaScript 的运行环境，相当于"发动机"。
- **npm** 是 Node.js 自带的包管理器，相当于"加油站"，帮你下载/管理各种功能包。
- **nvm** 是 Node.js 版本管理工具，相当于"发动机切换器"，让你可以随时切换不同版本的 Node.js。

### 为什么要用 nvm？
- 不同项目可能要求不同的 Node.js 版本（比如老项目只能用 16，新项目用 20）。
- nvm 让你可以在一台电脑上随时切换 Node 版本，避免版本冲突。
- nvm 还能帮你升级/降级 Node，适配各种依赖。

### npm 和 Node 的版本关系
- 每个 Node.js 版本自带一个对应的 npm 版本。
- 一般来说，npm 版本和 Node 版本配套升级，但你也可以用 `npm install -g npm@最新版本` 单独升级 npm。

### 实际开发中怎么用？
1. **用 nvm 安装和切换 Node 版本**
   ```bash
   nvm install 20.19.3   # 安装 Node 20.19.3
   nvm use 20.19.3       # 切换到 Node 20.19.3
   node -v               # 查看当前 Node 版本
   npm -v                # 查看当前 npm 版本
   ```
2. **用 npm 管理依赖**
   ```bash
   npm install           # 安装 package.json 里的所有依赖
   npm install <包名>    # 安装新依赖
   npm run dev           # 启动开发服务（如 Vite、Webpack 等）
   ```
3. **团队协作建议**
   - 项目文档里注明推荐的 Node 版本（如 20.19.3），团队成员都用 nvm 切换到同一版本。
   - 遇到依赖报错，优先检查 Node 版本是否一致。
   - package-lock.json 建议提交到 git，保证依赖一致。

### 版本选择建议
- 新项目优先用 Node 最新 LTS 版本（如 20.x），兼容性和安全性最好。
- 老项目如有特殊依赖，可用 nvm 切换到指定旧版本。
- npm 版本一般跟随 Node 自动升级，无需单独管理。

---

## 1. Node.js 简介

Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时，让开发者可以在服务端运行 JS 代码。
- **核心特性**：事件驱动、非阻塞 I/O、高性能、跨平台。
- **应用场景**：Web 服务、命令行工具、前端工程化、实时应用等。

## 2. npm（Node Package Manager）

npm 是 Node.js 的包管理工具，用于安装、管理、发布 JavaScript 包（依赖）。
- **常用命令**：
  - `npm install <包名>`：安装依赖
  - `npm install`：根据 package.json 安装所有依赖
  - `npm uninstall <包名>`：卸载依赖
  - `npm update`：更新依赖
  - `npm run <脚本名>`：运行 package.json 中 scripts 定义的脚本
- **依赖声明**：
  - `dependencies`：生产环境依赖
  - `devDependencies`：开发环境依赖
- **package.json**：项目依赖、元信息、脚本的声明文件
- **package-lock.json**：锁定依赖版本，保证团队环境一致

## 3. nvm（Node Version Manager）

nvm 是 Node.js 版本管理工具，支持多版本 Node 并行安装和切换。
- **常用命令**：
  - `nvm install <版本号>`：安装指定版本 Node.js
  - `nvm use <版本号>`：切换当前 shell 的 Node 版本
  - `nvm ls`：列出本地已安装的 Node 版本
  - `nvm ls-remote`：列出所有可用的 Node 版本
- **原理**：
  - nvm 通过修改 PATH 环境变量，动态切换 node、npm 的实际执行路径。
  - 每个 node 版本独立存储，互不影响。
- **适用场景**：
  - 团队协作时，确保所有人 node 版本一致
  - 兼容不同项目对 node 版本的要求

## 4. 依赖安装与环境一致性

- **开发环境**：建议用 nvm 统一 node 版本，npm 安装依赖，保证 node_modules 与 node 版本兼容。
- **生产/容器环境**：Dockerfile 需指定与开发一致的 node 镜像版本，npm install 只在容器内执行，避免 ABI 不兼容。
- **常见问题**：
  - node_modules 与 node 版本不一致，可能导致二进制包报错或 API 不兼容。
  - package-lock.json 不同步，团队成员依赖不一致。

## 5. 进阶工具

- **yarn/pnpm**：更快的包管理器，兼容 npm 生态。
- **nrm**：npm 源管理工具，快速切换淘宝、官方等镜像。

## 6. 参考链接
- [Node.js 官网](https://nodejs.org/zh-cn/)
- [npm 官方文档](https://docs.npmjs.com/)
- [nvm 官方文档](https://github.com/nvm-sh/nvm)
- [yarn 官网](https://yarnpkg.com/)
- [pnpm 官网](https://pnpm.io/zh/) 