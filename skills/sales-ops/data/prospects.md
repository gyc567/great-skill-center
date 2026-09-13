# 潜在客户追踪表

## 格式说明
| 字段 | 说明 |
|------|------|
| `###-公司名` | 报告编号-公司名 |
| `status` | new / qualified / outreach / followup / won / lost |
| `ramp_score` | 1.0-5.0 |
| `last_touch` | YYYY-MM-DD |

## 示例
```
###-acme-corp
status: qualified
ramp_score: 4.2
last_touch: 2026-09-13
archetype: Fast-Growth Fintech
outreach_channels: email, linkedin
```

## 使用方法
- 运行 `/sales-ops qualify 公司名` 生成评估报告
- 运行 `/sales-ops outreach ###` 生成外展文案
- 运行 `/sales-ops followup` 查看待跟进客户
