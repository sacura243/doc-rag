# Cloud Container Mini Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Route the production mini program through CloudBase container calls and CloudBase temporary file URLs so the app works without purchasing a custom domain.

**Architecture:** Keep the FastAPI REST contract under `/api/v1`. Add a transport-aware mini-program client: development uses the existing LAN `wx.request`, production JSON calls use `wx.cloud.callContainer`, and production uploads use `wx.cloud.uploadFile` + `wx.cloud.getTempFileURL` followed by an authenticated JSON import request. The backend downloads only HTTPS temporary URLs with bounded size/time, then reuses the existing upload validation and ingestion pipeline.

**Tech Stack:** FastAPI, httpx, Python standard library, WeChat Mini Program CloudBase APIs, Node.js test runner, pytest.

## Global Constraints

- Production CloudBase environment ID is `prod-d6gkf5lgbb9d67abc` and service name is `knowledge-api`.
- Production login path remains `/auth/wechat`; development login remains available only in development configuration.
- Supported files remain `.txt`, `.pdf`, `.docx`, maximum 10 MB per file and 5 files per selection.
- Never commit or print AppSecret, JWT secret, or Xunfei credentials.
- Preserve the existing LAN development transport.

---

### Task 1: Add CloudBase runtime configuration and client transport

**Files:**
- Modify: `miniprogram/config.js`
- Modify: `miniprogram/app.js`
- Modify: `miniprogram/utils/request.js`
- Test: `tests/miniprogram/runtime-config.test.js`
- Test: `tests/miniprogram/app-login.test.js`
- Test: `tests/miniprogram/request.test.js`

**Interfaces:**
- `runtimeConfig.transport`, `runtimeConfig.cloudEnv`, and `runtimeConfig.cloudService` configure production.
- `request({path, method, data})` resolves parsed response data for both transports.

- [ ] Write tests for production CloudBase fields and `wx.cloud.init({env})`.
- [ ] Run `node --test tests/miniprogram/runtime-config.test.js tests/miniprogram/app-login.test.js tests/miniprogram/request.test.js`; verify the new transport assertions fail before implementation.
- [ ] Implement `wx.cloud.init({env: runtimeConfig.cloudEnv})` in `onLaunch` when transport is `cloud-container`.
- [ ] Implement `wx.cloud.callContainer({config:{env}, service, path, method, data, header})` in `request.js`; preserve status/detail error mapping.
- [ ] Run the focused Node tests and verify they pass.
- [ ] Commit `feat: add cloud container mini program transport`.

### Task 2: Add secure backend import-from-URL endpoint

**Files:**
- Modify: `api/services/files.py`
- Modify: `api/routers/documents.py`
- Modify: `api/schemas.py`
- Test: `tests/api/test_documents.py`

**Interfaces:**
- `POST /api/v1/documents/import-url` accepts JSON `{url, filename}` and returns the same ingestion result as normal upload.
- `save_remote_upload(url, filename, upload_dir)` downloads an HTTPS URL with a 10 MB cap and returns a validated local path.

- [ ] Write failing tests for successful download/import, non-HTTPS rejection, oversized response rejection, and member authorization rejection.
- [ ] Run the focused tests and verify expected failures.
- [ ] Implement bounded streaming download with `httpx.Client(timeout=30, follow_redirects=False)`, reject redirects and non-HTTPS URLs, validate the filename extension, and clean partial files on failure.
- [ ] Reuse `ingest_files` and delete the local temporary file after ingestion attempt.
- [ ] Run focused API tests and verify they pass.
- [ ] Commit `feat: support cloud storage URL document imports`.

### Task 3: Replace production file upload flow

**Files:**
- Modify: `miniprogram/pages/documents/index.js`
- Test: `tests/miniprogram/documents-page.test.js`

**Interfaces:**
- `uploadSingle(file)` uses the existing multipart endpoint in development and CloudBase storage/import flow in production.

- [ ] Write failing Node tests covering cloud upload, temporary URL exchange, authenticated import, and cleanup.
- [ ] Run the focused tests and verify expected failures.
- [ ] Implement `wx.cloud.uploadFile`, `wx.cloud.getTempFileURL`, `request({path:'/documents/import-url', method:'POST', data:{url, filename}})`, and `wx.cloud.deleteFile` with cleanup in both success and failure paths.
- [ ] Preserve sequential progress, format/size validation, and existing user-facing error mapping.
- [ ] Run all mini-program tests and verify they pass.
- [ ] Commit `feat: upload documents through cloud storage`.

### Task 4: Production configuration and release verification

**Files:**
- Modify: `miniprogram/config.js`
- Modify: `deploy/README.md`
- Modify: `docs/PRODUCTION_RELEASE_CHECKLIST.md`
- Test: `tests/miniprogram/runtime-config.test.js`

- [ ] Set production transport to `cloud-container`, environment ID to `prod-d6gkf5lgbb9d67abc`, and service to `knowledge-api`.
- [ ] Update release docs to state that request/upload legal domains are unnecessary for CloudBase SDK calls, while the cloud-generated URL remains test-only for direct HTTP access.
- [ ] Run `node scripts/check_release.js`, all Node tests, all pytest tests, and `git diff --check`.
- [ ] Commit `feat: release mini program through cloud container` and push the deployment branch.

### Task 5: Manual cloud and real-device acceptance

- [ ] In WeChat Developer Tools, enable CloudBase for environment `prod-d6gkf5lgbb9d67abc` and compile the production configuration.
- [ ] Verify real `wx.login`, member read/query permissions, admin upload/delete/rebuild, and upload cleanup.
- [ ] Test empty/oversized/unsupported files, API failure, expired token, and offline recovery.
- [ ] Test on one iOS and one Android device, then adjust only verified layout issues.
