/**
 * 主布局组件
 */

import React from 'react'
import { Button, Layout, Menu, Space, Typography } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  LogoutOutlined,
  SafetyCertificateOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { authSession } from '../auth/session'

const { Header, Sider, Content } = Layout
const { Title } = Typography

interface MainLayoutProps {
  children: React.ReactNode
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const selectedKey = location.pathname.startsWith('/certificates') ? '/certificates' : location.pathname

  const handleLogout = () => {
    authSession.clearToken()
    navigate('/login', { replace: true })
  }

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/certificates',
      icon: <SafetyCertificateOutlined />,
      label: '证书管理',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} style={{ background: '#fff' }}>
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <Title level={4} style={{ margin: 0 }}>
            1yuanssl
          </Title>
          <p style={{ fontSize: '12px', color: '#999', margin: '8px 0 0 0' }}>
            SSL 证书管理系统
          </p>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px' }}>
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Title level={3} style={{ margin: '16px 0' }}>
              Let's Encrypt 证书管理
            </Title>
            <Button icon={<LogoutOutlined />} onClick={handleLogout}>
              退出
            </Button>
          </Space>
        </Header>
        <Content style={{ padding: '24px', background: '#f0f2f5', minHeight: '280px' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
