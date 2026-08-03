# GitHub 上传步骤（照着做，5 分钟搞定）

本地仓库已经初始化并提交好了（分支名 main），你只需要：

## 第 1 步：注册/登录 GitHub

打开 https://github.com 注册账号（有就跳过），记下你的用户名。

## 第 2 步：新建远程仓库

1. 打开 https://github.com/new
2. Repository name 填：`doc-rag`
3. 选 **Public**（简历上要给别人看，选 Public）
4. 其他都不用动，直接点 **Create repository**

## 第 3 步：把本地代码推上去

回到本地，打开 PowerShell，执行：

```powershell
cd D:\Pythonstudy\PythonProject\doc-rag
git remote add origin https://github.com/你的用户名/doc-rag.git
git branch -M main
git push -u origin main
```

第一次 push 会弹出 GitHub 登录窗口（或让你输入用户名 + 密码/Token），登录一次就好。

## 第 4 步：验证

浏览器打开 `https://github.com/你的用户名/doc-rag`，能看到代码就成功了。

---

## 以后更新代码

改完代码后执行：
```powershell
cd D:\Pythonstudy\PythonProject\doc-rag
git add -A
git commit -m "更新说明"
git push
```

---

## 注意

- `config.toml`（含密钥）、`chroma_db/`、`models/`、`test_resume/`、`test_output/` 已被 .gitignore 排除，**不会传到 GitHub**，密钥不会泄露。
- 上传后记得在 README 顶部加一行项目演示截图/说明，简历里放上 `github.com/你的用户名/doc-rag` 链接即可。