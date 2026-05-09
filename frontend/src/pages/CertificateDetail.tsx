/**
 * 证书订单详情页面
 */

import React, { useEffect, useState } from 'react'
import {
  Alert,
  Button,
  Card,
  Descriptions,
  Empty,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
  message,
} from 'antd'
import {
  ArrowLeftOutlined,
  CheckCircleOutlined,
  CloudDownloadOutlined,
  ReloadOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons'
import { useNavigate, useParams } from 'react-router-dom'
import dayjs from 'dayjs'
import { certificateApi } from '../api/certificates'
import type { AcmeChallenge, CertificateOrder, OrderStatus } from '../types/certificate'
import { ChallengeType, OrderStatus as OrderStatusEnum } from '../types/certificate'

const { Title, Paragraph, Text } = Typography

const statusColors: Record<OrderStatus, string> = {
  pending: 'blue',
  validating: 'orange',
  issued: 'green',
  failed: 'red',
  expired: 'default',
  renewing: 'purple',
}

const CertificateDetail: React.FC = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const orderId = Number(id)
  const [order, setOrder] = useState<CertificateOrder | null>(null)
  const [challenges, setChallenges] = useState<AcmeChallenge[]>([])
  const [loading, setLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const loadData = async () => {
    if (!Number.isFinite(orderId)) {
      message.error('无效的订单 ID')
      navigate('/certificates')
      return
    }

    setLoading(true)
    try {
      const [orderRes, challengeRes] = await Promise.all([
        certificateApi.get(orderId),
        certificateApi.getChallenges(orderId),
      ])

      if (orderRes.success) {
        setOrder(orderRes.data)
      }
      if (challengeRes.success) {
        setChallenges(challengeRes.data)
      }
    } catch (error) {
      message.error('加载订单详情失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [orderId])

  const runAction = async (action: 'validate' | 'issue') => {
    setActionLoading(action)
    try {
      const res =
        action === 'validate'
          ? await certificateApi.validate(orderId)
          : await certificateApi.issue(orderId)

      if (res.success) {
        message.success(action === 'validate' ? '验证已触发' : '证书已签发')
        await loadData()
      }
    } catch (error) {
      message.error(action === 'validate' ? '触发验证失败' : '签发证书失败')
    } finally {
      setActionLoading(null)
    }
  }

  const downloadFile = async (fileType: 'fullchain' | 'privkey' | 'cert') => {
    setActionLoading(fileType)
    try {
      const content = await certificateApi.download(orderId, fileType)
      const blob = new Blob([content], { type: 'application/x-pem-file;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `cert-${orderId}-${fileType}.pem`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch (error) {
      message.error('下载证书文件失败')
    } finally {
      setActionLoading(null)
    }
  }

  const challengeColumns = [
    {
      title: '域名',
      dataIndex: 'domain',
      key: 'domain',
    },
    {
      title: '类型',
      dataIndex: 'challenge_type',
      key: 'challenge_type',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: AcmeChallenge['status']) => (
        <Tag color={status === 'valid' ? 'green' : status === 'invalid' ? 'red' : 'blue'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: '验证信息',
      key: 'value',
      render: (_: unknown, challenge: AcmeChallenge) => {
        if (challenge.challenge_type === ChallengeType.DNS_01) {
          return (
            <Space direction="vertical" size={2}>
              <Text code>{challenge.dns_txt_name || '-'}</Text>
              <Text copyable code>
                {challenge.dns_txt_value || '-'}
              </Text>
            </Space>
          )
        }

        return (
          <Space direction="vertical" size={2}>
            <Text code>/.well-known/acme-challenge/{challenge.token || '-'}</Text>
            <Text copyable code>
              {challenge.key_authorization || '-'}
            </Text>
          </Space>
        )
      },
    },
    {
      title: '验证时间',
      dataIndex: 'validated_at',
      key: 'validated_at',
      render: (date?: string) => (date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'),
    },
  ]

  if (loading && !order) {
    return (
      <Card>
        <Spin />
      </Card>
    )
  }

  if (!order) {
    return (
      <Card>
        <Empty description="订单不存在" />
      </Card>
    )
  }

  const canValidate = order.status === OrderStatusEnum.PENDING
  const canIssue =
    order.status === OrderStatusEnum.PENDING || order.status === OrderStatusEnum.VALIDATING
  const canDownload = order.status === OrderStatusEnum.ISSUED

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/certificates')}>
          返回
        </Button>
        <Title level={4} style={{ margin: 0 }}>
          证书订单 #{order.id}
        </Title>
        <Tag color={statusColors[order.status]}>{order.status.toUpperCase()}</Tag>
      </Space>

      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Card
          title="订单信息"
          extra={
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
                刷新
              </Button>
              <Button
                icon={<CheckCircleOutlined />}
                onClick={() => runAction('validate')}
                loading={actionLoading === 'validate'}
                disabled={!canValidate}
              >
                触发验证
              </Button>
              <Button
                type="primary"
                icon={<SafetyCertificateOutlined />}
                onClick={() => runAction('issue')}
                loading={actionLoading === 'issue'}
                disabled={!canIssue}
              >
                签发证书
              </Button>
            </Space>
          }
        >
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="域名">{order.domains.join(', ')}</Descriptions.Item>
            <Descriptions.Item label="邮箱">{order.email}</Descriptions.Item>
            <Descriptions.Item label="证书类型">{order.cert_type}</Descriptions.Item>
            <Descriptions.Item label="验证方式">{order.challenge_type}</Descriptions.Item>
            <Descriptions.Item label="自动续期">{order.auto_renew ? '是' : '否'}</Descriptions.Item>
            <Descriptions.Item label="ACME 订单">
              {order.acme_order_url || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="生效时间">
              {order.not_before ? dayjs(order.not_before).format('YYYY-MM-DD HH:mm') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="过期时间">
              {order.not_after ? dayjs(order.not_after).format('YYYY-MM-DD HH:mm') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {dayjs(order.created_at).format('YYYY-MM-DD HH:mm')}
            </Descriptions.Item>
            <Descriptions.Item label="更新时间">
              {dayjs(order.updated_at).format('YYYY-MM-DD HH:mm')}
            </Descriptions.Item>
          </Descriptions>

          {order.error_message && (
            <Alert
              type="error"
              showIcon
              message="错误信息"
              description={order.error_message}
              style={{ marginTop: 16 }}
            />
          )}
        </Card>

        <Card title="验证信息">
          <Paragraph type="secondary">
            HTTP-01 需要目标域名可以访问下方路径；DNS-01 需要添加对应 TXT 记录。
          </Paragraph>
          <Table
            dataSource={challenges}
            columns={challengeColumns}
            rowKey="id"
            pagination={false}
            loading={loading}
          />
        </Card>

        <Card title="证书下载">
          <Space>
            <Button
              icon={<CloudDownloadOutlined />}
              disabled={!canDownload}
              loading={actionLoading === 'fullchain'}
              onClick={() => downloadFile('fullchain')}
            >
              fullchain.pem
            </Button>
            <Button
              icon={<CloudDownloadOutlined />}
              disabled={!canDownload}
              loading={actionLoading === 'cert'}
              onClick={() => downloadFile('cert')}
            >
              cert.pem
            </Button>
            <Button
              danger
              icon={<CloudDownloadOutlined />}
              disabled={!canDownload}
              loading={actionLoading === 'privkey'}
              onClick={() => downloadFile('privkey')}
            >
              privkey.pem
            </Button>
          </Space>
          {!canDownload && (
            <Paragraph type="secondary" style={{ marginTop: 16, marginBottom: 0 }}>
              证书签发后可下载证书链、证书和私钥文件。
            </Paragraph>
          )}
        </Card>
      </Space>
    </div>
  )
}

export default CertificateDetail
