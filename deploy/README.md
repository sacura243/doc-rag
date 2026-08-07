# HTTPS deployment

This provider-neutral template runs the API behind Caddy. Caddy obtains and renews the TLS certificate for `API_DOMAIN` automatically.

1. On a Linux server, install Docker and copy the repository.
2. Copy `deploy/.env.production.example` to `deploy/.env.production` and fill the values locally. Never commit that file.
3. Ensure `config.toml` exists at the repository root and contains the RAG provider configuration. Keep it out of Git.
4. Point the domain's DNS A record to the server and allow inbound TCP ports 80 and 443.
5. Start the stack from the repository root:

   ```sh
   docker compose -f deploy/docker-compose.yml up -d --build
   ```

6. Verify `https://<API_DOMAIN>/api/v1/health` returns `{"status":"ok"}`.

Before production release, set `ENVIRONMENT` to `production` in `miniprogram/config.js`, put the same HTTPS URL in `production.apiBaseUrl`, and add the domain to WeChat's request合法域名. Real WeChat login also requires the AppID/AppSecret and an admin OpenID on the server; do not send those secrets in chat.

Run the release preflight before uploading the mini program:

```sh
node scripts/check_release.js
```
