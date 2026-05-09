/**
 * 证书列表页面
 */

import React, { useEffect, useState } from 'react'
import { Card, Table, Button, Tag, Space, Typography, Popconfirm, Select, message } from 'antd'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'
import { certificateApi } from '../api/certificates'
import { OrderStatus } from '../types/certificate'
import type { CertificateOrder } from '../types/certificate'

const { Title } = Typography

const CertificateList: React.FC = () => {
  const navigate = useNavigate()
  const [orders, setOrders] = useState<CertificateOrder[]>([])
  const [loading, setLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState<OrderStatus | undefined>()

  useEffect(() => {
    loadOrders()
  }, [statusFilter])

  const loadOrders = async () => {
    setLoading(true)
    try {
      const res = await certificateApi.list(statusFilter ? { status: statusFilter } : undefined)
      if (res.success) {
        setOrders(res.data)
      }
    } catch (error) {
      message.error('加载证书列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (orderId: number) => {
    try {
      const res = await certificateApi.delete(orderId)
      if (res.success) {
        message.success('删除成功')
        loadOrders()
      }
    } catch (error) {
      message.error('删除失败')
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

  const statusOptions = [
    { label: '待处理', value: OrderStatus.PENDING },
    { label: '验证中', value: OrderStatus.VALIDATING },
    { label: '已签发', value: OrderStatus.ISSUED },
    { label: '失败', value: OrderStatus.FAILED },
    { label: '已过期', value: OrderStatus.EXPIRED },
    { label: '续期中', value: OrderStatus.RENEWING },
  ]

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '域名',
      dataIndex: 'domains',
      key: 'domains',
      render: (domains: string[]) => domains.join(', '),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
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
      title: '自动续期',
      dataIndex: 'auto_renew',
      key: 'auto_renew',
      render: (auto: boolean) => auto ? '是' : '否',
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
          <Popconfirm
            title="确定删除此订单吗？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card
        title={<Title level={4}>证书订单列表</Title>}
        extra={
          <Space>
            <Select<OrderStatus>
              allowClear
              placeholder="按状态筛选"
              value={statusFilter}
              options={statusOptions}
              onChange={setStatusFilter}
              style={{ width: 140 }}
            />
            <Button icon={<ReloadOutlined />} onClick={loadOrders}>刷新</Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/certificates/create')}>
              新建订单
            </Button>
          </Space>
        }
      >
        <Table
          dataSource={orders}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  )
}

export default CertificateList
