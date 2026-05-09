/**
 * 管理员登录页面
 */

import React, { useState } from 'react'
import { Button, Card, Form, Input, Typography, message } from 'antd'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { useLocation, useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { authSession } from '../auth/session'
import type { LoginRequest } from '../types/auth'

const { Title, Paragraph } = Typography

const Login: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [loading, setLoading] = useState(false)
  const from = (location.state as { from?: string } | null)?.from || '/'

  const handleSubmit = async (values: LoginRequest) => {
    setLoading(true)
    try {
      const res = await authApi.login(values)
      if (res.success) {
        authSession.setToken(res.data.access_token)
        message.success('登录成功')
        navigate(from, { replace: true })
      }
    } catch (error) {
      message.error('用户名或密码错误')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f0f2f5',
        padding: 24,
      }}
    >
      <Card style={{ width: 380 }}>
        <Title level={3} style={{ marginBottom: 8 }}>
          1yuanssl
        </Title>
        <Paragraph type="secondary">管理员登录</Paragraph>

        <Form<LoginRequest> layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input prefix={<UserOutlined />} autoComplete="username" />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} autoComplete="current-password" />
          </Form.Item>

          <Button type="primary" htmlType="submit" loading={loading} block>
            登录
          </Button>
        </Form>
      </Card>
    </div>
  )
}

export default Login
