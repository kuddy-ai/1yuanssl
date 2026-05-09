/**
 * Dashboard 页面
 */

import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Button, Space, Typography } from 'antd'
import {
  SafetyCertificateOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'
import { certificateApi } from '../api/certificates'
import type { CertificateStats, CertificateOrder, OrderStatus } from '../types/certificate'

const { Title } = Typography

const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const [stats, setStats] = useState<CertificateStats | null>(null)
  const [recentOrders, setRecentOrders] = useState<CertificateOrder[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [statsRes, ordersRes] = await Promise.all([
        certificateApi.getStats(),
        certificateApi.list({ limit: 10 }),
      ])

      if (statsRes.success) {
        setStats(statsRes.data)
      }
      if (ordersRes.success) {
        setRecentOrders(ordersRes.data)
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: OrderStatus) => {
    const colors: Record<OrderStatus, string> = {
      pending: 'blue',
      validating: 'orange',
      issued: 'green',
      failed: 'red',
      expired: 'default',
      renewing: 'purple',
    }
    return colors[status] || 'default'
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '域名',
      dataIndex: 'domains',
      key: 'domains',
      render: (domains: string[]) => domains.join(', '),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: OrderStatus) => (
        <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: '验证方式',
      dataIndex: 'challenge_type',
      key: 'challenge_type',
    },
    {
      title: '过期时间',
      dataIndex: 'not_after',
      key: 'not_after',
      render: (date?: string) => date ? dayjs(date).format('YYYY-MM-DD') : '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: CertificateOrder) => (
        <Space>
          <Button type="link" onClick={() => navigate(`/certificates/${record.id}`)}>
            详情
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Title level={4}>仪表盘</Title>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="证书总数"
              value={stats?.total || 0}
              prefix={<SafetyCertificateOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="已签发"
              value={stats?.issued || 0}
              valueStyle={{ color: '#3f8600' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="申请失败"
              value={stats?.failed || 0}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="即将过期"
              value={stats?.expiring || 0}
              valueStyle={{ color: '#faad14' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近订单 */}
      <Card title="最近申请记录" extra={<Button onClick={() => navigate('/certificates')}>查看全部</Button>}>
        <Table
          dataSource={recentOrders}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={false}
        />
      </Card>
    </div>
  )
}

export default Dashboard
