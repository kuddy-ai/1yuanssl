/**
 * 系统设置页面
 */

import React, { useEffect, useState } from 'react'
import {
  Alert,
  Button,
  Card,
  Descriptions,
  Space,
  Tag,
  Typography,
  message,
} from 'antd'
import {
  CloudServerOutlined,
  ReloadOutlined,
  SafetyCertificateOutlined,
  SecurityScanOutlined,
} from '@ant-design/icons'
import { systemApi } from '../api/system'
import type { HealthStatus } from '../types/system'

const { Title, Paragraph, Text } = Typography

const Settings: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(false)

  const loadHealth = async () => {
    setLoading(true)
    try {
      const data = await systemApi.getHealth()
      setHealth(data)
    } catch (error) {
      message.error('加载系统状态失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHealth()
  }, [])

  const isHealthy = health?.status === 'healthy'
  const isDatabaseHealthy = health?.database === 'healthy'

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>
          系统设置
        </Title>
      </Space>

      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Card
          title={
            <Space>
              <CloudServerOutlined />
              <span>运行状态</span>
            </Space>
          }
          extra={
            <Button icon={<ReloadOutlined />} onClick={loadHealth} loading={loading}>
              刷新
            </Button>
          }
          loading={loading && !health}
        >
          {health ? (
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="服务状态">
                <Tag color={isHealthy ? 'green' : 'red'}>{health.status}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="数据库">
                <Tag color={isDatabaseHealthy ? 'green' : 'red'}>{health.database}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="服务名">{health.service}</Descriptions.Item>
              <Descriptions.Item label="版本">{health.version}</Descriptions.Item>
              <Descriptions.Item label="运行模式">{health.mode}</Descriptions.Item>
            </Descriptions>
          ) : (
            <Alert type="warning" showIcon message="暂未获取到系统状态" />
          )}
        </Card>

        <Card
          title={
            <Space>
              <SafetyCertificateOutlined />
              <span>ACME 配置</span>
            </Space>
          }
        >
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="当前实现">
              Mock ACME 客户端
            </Descriptions.Item>
            <Descriptions.Item label="证书签发">
              不会请求真实 Let's Encrypt API
            </Descriptions.Item>
            <Descriptions.Item label="验证方式">
              HTTP-01 与 DNS-01 均为 MVP 模拟流程
            </Descriptions.Item>
          </Descriptions>
        </Card>

        <Card
          title={
            <Space>
              <SecurityScanOutlined />
              <span>安全边界</span>
            </Space>
          }
        >
          <Paragraph>
            当前版本不保存 SSH 密码、root 密钥、云账号主密钥或 DNS Provider 主密钥。
          </Paragraph>
          <Paragraph style={{ marginBottom: 0 }}>
            <Text type="secondary">
              证书和私钥材料仅通过 API 读取；私钥内容不会通过静态文件路径暴露。
            </Text>
          </Paragraph>
        </Card>
      </Space>
    </div>
  )
}

export default Settings
