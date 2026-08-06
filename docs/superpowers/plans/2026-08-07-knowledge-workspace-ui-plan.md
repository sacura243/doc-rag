# Knowledge Workspace UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task with verification checkpoints.

**Goal:** 将知答库小程序首页改造成知识库工作台，并把资料上传入口提升为首屏可见的主要操作。

**Architecture:** 保持原生微信小程序页面和现有 FastAPI 接口不变。首页负责资料摘要、问答和快捷入口；资料页负责上传、删除和重建。沿用当前请求封装、管理员角色判断和来源数据结构，采用 WeUI 的微信原生视觉原则而不复制第三方代码。

**Tech Stack:** Native WeChat Mini Program WXML/WXSS/JavaScript, FastAPI, Node built-in test runner, pytest.

## Global Constraints

- 首页必须在首屏展示管理员可用的“上传资料”入口。
- 上传只允许 TXT/PDF/DOCX，单文件最大 10 MB，一次最多 5 个文件。
- 普通成员可以查看资料和提问，但不能上传、删除或重建。
- 问答回答必须保留来源资料名、页码和证据片段；不得泄露服务器路径。
- 本地默认 API 为 `http://127.0.0.1:8010/api/v1`，正式环境才切换 HTTPS 和真实微信登录。
- 卡片圆角不超过 8px；主色使用青绿色，背景保持白色和浅灰，不使用大面积渐变。

---

### Task 1: Homepage data and navigation contract

**Files:**
- Modify: `miniprogram/pages/index/index.js`
- Modify: `miniprogram/utils/request.js` only if error payload handling is needed
- Test: `tests/miniprogram/index-page.test.js`

**Interfaces:**
- Consumes `GET /documents` returning `{items: [{id, name, chunks}]}` and `POST /chat` returning `{answer, sources}`.
- Produces page methods `loadOverview`, `openDocuments`, `chooseFile` and state fields `documents`, `documentCount`, `chunkCount`, `sources`, `overviewError`.

- [x] **Step 1: Write failing tests for overview and shortcut state.** Extend the Node page test with a mocked `/documents` response and assert `loadOverview` computes document and chunk totals, and `openDocuments` calls `wx.switchTab` with `pages/documents/index`.
- [x] **Step 2: Run the focused test and verify it fails because the methods/state do not exist.**

Run: `node --test tests/miniprogram/index-page.test.js`

Expected: FAIL with a missing `loadOverview` or `openDocuments` behavior.
- [x] **Step 3: Implement the smallest page state and methods.** Keep the existing `askQuestion` behavior, add overview loading on `onShow`, preserve returned sources, and make upload shortcut call `wx.switchTab` to the documents page.
- [x] **Step 4: Run the focused test and all mini-program syntax checks.**

Run: `node --test tests/miniprogram/index-page.test.js` and `node --check` for every `miniprogram/**/*.js` file.
- [x] **Step 5: Commit the homepage data contract.**

```powershell
git add miniprogram/pages/index/index.js tests/miniprogram/index-page.test.js
git commit -m "feat: add knowledge workspace homepage state"
```

### Task 2: Redesign the homepage layout

**Files:**
- Modify: `miniprogram/pages/index/index.wxml`
- Modify: `miniprogram/pages/index/index.wxss`

**Interfaces:**
- Consumes the state from Task 1: `documentCount`, `chunkCount`, `questionCount`, `documents`, `answer`, `sources`, `loading`, and `overviewError`.
- Produces a first viewport with a welcome block, question composer, two shortcut actions, overview stats, recent documents, answer, and citations.

- [x] **Step 1: Add WXML sections with stable dimensions.** Use one full-width page flow, a compact header, a restrained welcome band, a textarea, icon+text action buttons, stats, recent document rows, and citation rows. Keep upload visible without scrolling on common phone heights.
- [x] **Step 2: Add WXSS for the white/teal workspace visual system.** Use 8px-or-less visual corners, consistent spacing, text wrapping for long document names, disabled/loading states, and no decorative gradients.
- [ ] **Step 3: Run WXML/JS syntax checks and inspect the compiled page in WeChat Developer Tools.** Confirm no text overlap at desktop simulator and narrow phone widths.
- [x] **Step 4: Commit the homepage visual redesign.**

```powershell
git add miniprogram/pages/index/index.wxml miniprogram/pages/index/index.wxss
git commit -m "feat: redesign knowledge workspace homepage"
```

### Task 3: Make the documents page a clear secondary management screen

**Files:**
- Modify: `miniprogram/pages/documents/index.js`
- Modify: `miniprogram/pages/documents/index.wxml`
- Modify: `miniprogram/pages/documents/index.wxss`
- Test: `tests/miniprogram/documents-page.test.js`

**Interfaces:**
- Consumes the existing document list/upload/delete/rebuild APIs and `isAdmin` role state.
- Produces an obvious upload panel, supported-file hint, progress state, error state, empty state, document list, delete action, and rebuild action.

- [x] **Step 1: Add failing tests for empty state and upload progress state transitions.** Test that invalid files are rejected before `wx.uploadFile`, and that a successful two-file sequence ends at 100% and refreshes the list.
- [x] **Step 2: Run the focused tests and verify the new assertions fail.**
- [x] **Step 3: Implement the page transition and state updates.** Keep the existing sequential upload, map API errors to Chinese text, and prevent duplicate upload/rebuild taps while busy.
- [x] **Step 4: Redesign the WXML/WXSS with a clear upload panel and compact file rows.** Ensure members see the list but not admin controls.
- [x] **Step 5: Run focused tests and mini-program syntax checks.**
- [x] **Step 6: Commit the secondary page redesign.**

```powershell
git add miniprogram/pages/documents tests/miniprogram/documents-page.test.js
git commit -m "feat: improve document management page"
```

### Task 4: Integration verification and handoff

**Files:**
- Modify: `README_MINIPROGRAM.md` if the visible flow or configuration changes
- Modify: `progress.md` and `task_plan.md`

**Interfaces:**
- Consumes the finished mini-program pages and existing local API.
- Produces a verified local development flow and a concise handoff checklist.

- [x] **Step 1: Run backend API tests.**

Run: `D:\tools\Python\python.exe -m pytest tests/api -q`

Expected: all tests pass; the known Chroma Python 3.14 deprecation warning may remain.
- [x] **Step 2: Run all mini-program tests and JS syntax checks.**

Run: `node --test tests/miniprogram/*.test.js` plus `node --check` for every JavaScript file under `miniprogram`.
- [x] **Step 3: Verify the live health endpoint.**

Run: `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8010/api/v1/health`

Expected body: `{"status":"ok"}`.
- [x] **Step 4: Update the progress log with test counts and the remaining user-side compile check.**
- [ ] **Step 5: Commit the final documentation checkpoint.**

```powershell
git add README_MINIPROGRAM.md progress.md task_plan.md
git commit -m "docs: record knowledge workspace UI verification"
```
