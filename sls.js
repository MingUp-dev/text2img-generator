// 腾讯云云函数入口文件
// 使用CommonJS格式
const express = require('express')
const path = require('path')
const app = express()

// 环境变量
process.env.NODE_ENV = process.env.NODE_ENV || 'production'
const RELEASE_ENV = process.env.NODE_ENV === 'production'

// 处理POST请求，解析JSON
app.use(express.json())

// 静态文件服务
app.use(express.static(path.join(__dirname)))

// 设置CORS
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*')
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization')
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }
  
  next()
})

// 返回API路径中间件
app.use('/api/*', (req, res, next) => {
  // 确保包含正确的CORS头
  res.header('Access-Control-Allow-Origin', '*')
  next()
})

// 确保根路径能正确响应
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'))
})

// 路由到server.js中定义的API
const createDynamicRoutes = async () => {
  try {
    // 使用动态导入加载ES模块
    const serverModule = await import('./server.js')
    const serverApp = serverModule.default
    
    // 合并API路由
    app.use('/', serverApp)
    console.log('成功加载API路由')
  } catch (err) {
    console.error('加载API路由失败:', err)
    
    // 如果无法加载路由，返回错误处理中间件
    app.use('/api/*', (req, res) => {
      res.status(500).json({
        success: false,
        message: '服务器配置错误，无法加载API路由'
      })
    })
  }
}

// 在腾讯云函数环境中初始化路由
if (RELEASE_ENV) {
  createDynamicRoutes().catch(err => {
    console.error('初始化路由失败:', err)
  })
} else {
  // 本地开发环境
  createDynamicRoutes().then(() => {
    app.listen(5001, () => {
      console.log('本地开发服务器运行在端口 5001')
    })
  }).catch(err => {
    console.error('启动本地服务器失败:', err)
  })
}

// 腾讯云函数入口
module.exports = app 