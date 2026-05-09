/**
 * 应用入口组件
 */

import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import MainLayout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CertificateList from './pages/CertificateList'
import CertificateCreate from './pages/CertificateCreate'
import CertificateDetail from './pages/CertificateDetail'
import Settings from './pages/Settings'

const App: React.FC = () => {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/certificates" element={<CertificateList />} />
          <Route path="/certificates/create" element={<CertificateCreate />} />
          <Route path="/certificates/:id" element={<CertificateDetail />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </MainLayout>
    </Router>
  )
}

export default App
