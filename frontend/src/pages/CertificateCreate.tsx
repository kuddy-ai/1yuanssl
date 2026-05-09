/**
 * 创建证书订单页面
 */

import React, { useMemo } from 'react'
import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  Select,
  Space,
  Switch,
  Typography,
  message,
} from 'antd'
import { ArrowLeftOutlined, SafetyCertificateOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { certificateApi } from '../api/certificates'
import {
  CertificateType,
  ChallengeType,
  type CertificateOrderCreate,
} from '../types/certificate'

const { Title, Text } = Typography
const { TextArea } = Input

interface CertificateCreateForm {
  domainsText: string
  email: string
  cert_type: CertificateType
  challenge_type: ChallengeType
  auto_renew: boolean
}

const CertificateCreate: React.FC = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm<CertificateCreateForm>()
  const challengeType = Form.useWatch('challenge_type', form)

  const helpText = useMemo(() => {
    if (challengeType === ChallengeType.DNS_01) {
      return '提交后在详情页查看需要添加的 DNS TXT 记录。'
    }
    return '提交后在详情页查看 HTTP-01 token 和验证地址。'
  }, [challengeType])

  const normalizeDomains = (value: string) => {
    return value
      .split(/[\n,，\s]+/)
      .map((item) => item.trim())
      .filter(Boolean)
  }

  const handleSubmit = async (values: CertificateCreateForm) => {
    const domains = normalizeDomains(values.domainsText)
    const payload: CertificateOrderCreate = {
      domains,
      email: values.email,
      cert_type: values.cert_type,
      challenge_type: values.challenge_type,
      auto_renew: values.auto_renew,
    }

    try {
      const res = await certificateApi.create(payload)
      if (res.success) {
        message.success('证书订单已创建')
        navigate(`/certificates/${res.data.id}`)
      }
    } catch (error) {
      message.error('创建证书订单失败')
    }
  }

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/certificates')}>
          返回
        </Button>
        <Title level={4} style={{ margin: 0 }}>
          新建证书订单
        </Title>
      </Space>

      <Card>
        <Form<CertificateCreateForm>
          form={form}
          layout="vertical"
          initialValues={{
            cert_type: CertificateType.SINGLE,
            challenge_type: ChallengeType.HTTP_01,
            auto_renew: true,
          }}
          onFinish={handleSubmit}
          style={{ maxWidth: 760 }}
        >
          <Form.Item
            label="域名"
            name="domainsText"
            rules={[
              { required: true, message: '请输入至少一个域名' },
              {
                validator: (_, value?: string) => {
                  const domains = normalizeDomains(value || '')
                  if (domains.length === 0) {
                    return Promise.reject(new Error('请输入至少一个域名'))
                  }
                  if (domains.some((domain) => domain.length > 255)) {
                    return Promise.reject(new Error('域名长度不能超过 255 个字符'))
                  }
                  return Promise.resolve()
                },
              },
            ]}
            extra="支持换行、空格或逗号分隔多个域名。泛域名示例：*.example.com"
          >
            <TextArea rows={4} placeholder="example.com&#10;www.example.com" />
          </Form.Item>

          <Form.Item
            label="联系邮箱"
            name="email"
            rules={[
              { required: true, message: '请输入联系邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input placeholder="admin@example.com" />
          </Form.Item>

          <Form.Item label="证书类型" name="cert_type" rules={[{ required: true }]}>
            <Select
              options={[
                { label: '单域名证书', value: CertificateType.SINGLE },
                { label: '泛域名证书', value: CertificateType.WILDCARD },
                { label: '多域名证书', value: CertificateType.MULTI },
              ]}
            />
          </Form.Item>

          <Form.Item label="验证方式" name="challenge_type" rules={[{ required: true }]}>
            <Select
              options={[
                { label: 'HTTP-01', value: ChallengeType.HTTP_01 },
                { label: 'DNS-01', value: ChallengeType.DNS_01 },
              ]}
            />
          </Form.Item>

          <Alert
            type="info"
            showIcon
            message={helpText}
            style={{ marginBottom: 24 }}
          />

          <Form.Item label="自动续期" name="auto_renew" valuePropName="checked">
            <Switch checkedChildren="开启" unCheckedChildren="关闭" />
          </Form.Item>

          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SafetyCertificateOutlined />}
            >
              创建订单
            </Button>
            <Button onClick={() => navigate('/certificates')}>取消</Button>
          </Space>

          <div style={{ marginTop: 24 }}>
            <Text type="secondary">
              当前版本使用 Mock ACME 客户端，创建订单不会请求真实 Let's Encrypt。
            </Text>
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default CertificateCreate
