# 生产部署说明

本文档用于部署公网演示或内部生产环境。当前版本仍使用 Mock ACME，不会申请真实 Let's Encrypt 证书。

## 部署边界

- 可以用于公网演示证书申请流程、订单管理、Mock 签发和证书下载。
- 不应用于真实证书签发业务。
- 不应保存客户 SSH 密码、root 密钥、云账号主密钥或 DNS Provider 主密钥。

## 必填环境变量

生产环境必须显式配置：

```bash
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://user:password@postgres/1yuanssl
ENCRYPTION_KEY=<strong-random-secret>
ADMIN_USERNAME=<admin-user>
ADMIN_PASSWORD=<strong-admin-password>
ADMIN_API_TOKEN=<strong-random-api-token>
ACME_MODE=mock
ALLOWED_HOSTS=ssl.example.com
CORS_ORIGINS=https://ssl.example.com
```

启动保护会拒绝以下配置：

- `DEBUG=true`
- 默认 `ENCRYPTION_KEY`
- 默认管理员密码或 API token
- 默认本地 `CORS_ORIGINS`
- 默认本地 `ALLOWED_HOSTS`

## 反向代理

建议用 Nginx、Caddy 或云负载均衡终止 HTTPS，并转发到容器内部服务。

必须保留以下路径：

- `/api/v1/*` 转发到后端
- `/.well-known/acme-challenge/*` 转发到后端
- 其他路径转发到前端

建议启用：

- HTTPS 强制跳转
- HSTS
- 请求体大小限制
- 访问日志和错误日志
- 后端健康检查 `/api/v1/health`

## 数据库

- 生产环境建议 PostgreSQL。
- SQLite 仅适合本地开发或临时演示。
- 定期备份数据库。
- 数据库账号使用最小权限。

## 私钥和证书材料

- `ENCRYPTION_KEY` 必须使用强随机值，且不能提交到 Git。
- 私钥和证书只通过 API 下载，不要增加静态文件目录暴露。
- 下载接口已经需要管理员认证，但公网环境仍应配合 HTTPS 和访问日志。

## 运维检查

上线前检查：

- 管理员默认密码和 token 已修改。
- `APP_ENV=production` 且 `DEBUG=false`。
- `CORS_ORIGINS` 只允许正式前端域名。
- `ALLOWED_HOSTS` 只包含正式域名。
- 已配置 HTTPS。
- 已配置数据库备份。
- 已配置日志采集和错误告警。
- 已确认 `ACME_MODE=mock` 的业务边界。

## 常用验证

```bash
curl https://ssl.example.com/api/v1/health
curl -X POST https://ssl.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<admin-user>","password":"<strong-admin-password>"}'
```

登录成功后，使用返回的 `access_token` 访问受保护 API：

```bash
curl https://ssl.example.com/api/v1/certificates/orders \
  -H "Authorization: Bearer <access-token>"
```
