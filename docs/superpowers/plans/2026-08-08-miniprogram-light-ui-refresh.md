# Mini Program Light UI Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the homepage and document page with a coherent light visual system while retaining every current workflow.

**Architecture:** Keep the WXML and JavaScript event handlers unchanged. Rewrite only page-scoped WXSS and add stylesheet-contract tests that protect button centering and visual hierarchy.

**Tech Stack:** WeChat Mini Program WXML/WXSS, Node.js built-in test runner, existing CloudBase application.

## Global Constraints

- Preserve login, role handling, CloudBase upload/import, deletion, rebuilding, and RAG behavior.
- Use a cool light-gray background, white surfaces, muted teal as the sole primary accent, and pale mint as a supporting surface.
- Use consistent 10-14rpx visual radii, thin borders, and no decorative shadows.
- Every native button explicitly uses `box-sizing:border-box`, `padding:0`, and flex centering.
- Do not promise local-file browsing outside WeChat's platform capability.

---

### Task 1: Establish Homepage Light Visual System

**Files:**
- Modify: `miniprogram/pages/index/index.wxss`
- Modify: `tests/miniprogram/index-page.test.js`

**Interfaces:**
- Consumes: Existing WXML class names `.composer`, `.ask`, `.shortcut`, `.stats`, `.document-row`, `.empty-button`.
- Produces: Centered native actions and stable shortcut/document-row alignment.

- [ ] **Step 1: Write the failing stylesheet contract test**

```js
test('homepage stylesheet keeps the light workspace hierarchy and centered actions', () => {
  const stylesheet = fs.readFileSync(path.resolve(__dirname, '../../miniprogram/pages/index/index.wxss'), 'utf8')
  assert.match(stylesheet, /\.page\{[\s\S]*background:#f7f9fa/)
  assert.match(stylesheet, /\.composer\{[\s\S]*border:1rpx solid #e4ebed/)
  assert.match(stylesheet, /\.shortcut\{[\s\S]*align-items:center/)
  assert.match(stylesheet, /\.ask,\.empty-button\{[\s\S]*padding:0/)
  assert.match(stylesheet, /\.ask,\.empty-button\{[\s\S]*justify-content:center/)
})
```

- [ ] **Step 2: Run the test and verify it fails**

```powershell
$node='C:\Users\25350\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
& $node --test tests/miniprogram/index-page.test.js
```

Expected: FAIL because a shared native-action rule is not yet present.

- [ ] **Step 3: Rewrite homepage WXSS in readable blocks**

Keep every selector used by `index.wxml`. Use this exact shared-action rule:

```css
.ask,
.empty-button {
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding: 0;
  line-height: 1;
  text-align: center;
}
```

Set `.page` to `background:#f7f9fa`; use `#fff` surfaces with `1rpx solid #e4ebed`; retain `#0f766e` as the primary accent. Give `.shortcut`, `.document-row`, and `.stats` stable flex alignment and use `min-width:0` on truncating children. Do not change `index.wxml` or `index.js`.

- [ ] **Step 4: Run verification**

```powershell
& $node --test tests/miniprogram/index-page.test.js
git diff --check
```

Expected: all homepage tests pass and `git diff --check` has no output.

- [ ] **Step 5: Commit**

```powershell
git add miniprogram/pages/index/index.wxss tests/miniprogram/index-page.test.js
git commit -m "style: refine light knowledge workspace homepage"
```

### Task 2: Refine Document Management Upload and List States

**Files:**
- Modify: `miniprogram/pages/documents/index.wxss`
- Modify: `tests/miniprogram/documents-page.test.js`

**Interfaces:**
- Consumes: Existing WXML class names `.rebuild`, `.upload-panel`, `.upload`, `.item`, `.delete`, `.empty-action`.
- Produces: A restrained light upload panel, scan-friendly document rows, and centered native actions.

- [ ] **Step 1: Write the failing stylesheet contract test**

```js
test('documents stylesheet prioritizes upload and centers every native action', () => {
  const stylesheet = require('node:fs').readFileSync(path.resolve(__dirname, '../../miniprogram/pages/documents/index.wxss'), 'utf8')
  assert.match(stylesheet, /\.upload-panel\{[\s\S]*background:#effaf8/)
  assert.match(stylesheet, /\.item\{[\s\S]*align-items:center/)
  assert.match(stylesheet, /\.rebuild,\.upload,\.delete,\.empty-action\{[\s\S]*padding:0/)
  assert.match(stylesheet, /\.rebuild,\.upload,\.delete,\.empty-action\{[\s\S]*justify-content:center/)
})
```

- [ ] **Step 2: Run the test and verify it fails**

```powershell
& $node --test tests/miniprogram/documents-page.test.js
```

Expected: FAIL because there is no shared native-action normalization rule.

- [ ] **Step 3: Rewrite document page WXSS in readable blocks**

Preserve every WXML class. Use this exact shared-action rule:

```css
.rebuild,
.upload,
.delete,
.empty-action {
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding: 0;
  line-height: 1;
  text-align: center;
}
```

Keep `.upload` as the sole filled teal action, `.rebuild` as a compact outline action, `.delete` visually isolated from metadata, and reuse Task 1's background, border, and radius values. Do not change `documents/index.wxml` or `documents/index.js`.

- [ ] **Step 4: Run full verification and simulator inspection**

```powershell
& $node --test tests/miniprogram/*.test.js
git diff --check
```

Clear all WeChat Developer Tools caches, compile, and inspect both pages in a narrow mobile simulator. Confirm centered labels, upload prominence, no long-name/Delete overlap, and an upload action in the empty state.

- [ ] **Step 5: Commit and push**

```powershell
git add miniprogram/pages/documents/index.wxss tests/miniprogram/documents-page.test.js
git commit -m "style: refine document management workspace"
git push origin feature/wechat-mini-program
```

## Plan Self-Review

- Spec coverage: Task 1 covers the question workspace, shortcuts, statistics/document readability, and homepage actions. Task 2 covers upload hierarchy, rebuild priority, document rows, empty-state action, and mobile inspection.
- Placeholder scan: no TBD, TODO, or undefined interfaces remain.
- Type consistency: only WXSS and Node.js stylesheet tests change; no JavaScript API or data contract changes are introduced.
