const { request } = require('../../utils/request')

const MAX_FILE_BYTES = 10 * 1024 * 1024
const SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.docx']

function validateFile(file) {
  const name = String(file && file.name || '').toLowerCase()
  const extension = SUPPORTED_EXTENSIONS.find(item => name.endsWith(item))
  if (!extension) return '仅支持 TXT、PDF、DOCX 文件'
  if (Number(file.size || 0) > MAX_FILE_BYTES) return '文件超过 10 MB'
  return ''
}

function formatUploadError(statusCode, payload) {
  if (statusCode === 413) return '文件超过 10 MB'
  if (statusCode === 415) return '仅支持 TXT、PDF、DOCX 文件'
  if (statusCode === 422) return '文件为空或一次上传过多'
  if (payload && typeof payload.detail === 'string' && payload.detail) return payload.detail
  return '上传失败，请稍后重试'
}

Page({
  data: { items: [], isAdmin: false, uploading: false, uploadProgress: 0, rebuilding: false, errorMessage: '' },

  onShow() {
    const user = getApp().globalData.user
    this.setData({ isAdmin: Boolean(user && user.role === 'admin'), errorMessage: '' })
    this.loadDocuments()
  },

  loadDocuments() {
    request({ path: '/documents' })
      .then(data => this.setData({ items: data.items || [], errorMessage: '' }))
      .catch(error => this.setData({ errorMessage: error.message }))
  },

  deleteDocument(e) {
    wx.showModal({
      title: '删除资料',
      content: '删除后将无法检索该资料，是否继续？',
      success: result => {
        if (!result.confirm) return
        request({ path: `/documents/${encodeURIComponent(e.currentTarget.dataset.id)}`, method: 'DELETE' })
          .then(() => {
            wx.showToast({ title: '已删除', icon: 'success' })
            this.loadDocuments()
          })
          .catch(error => this.setData({ errorMessage: error.message }))
      }
    })
  },

  chooseFile() {
    if (this.data.uploading) return
    wx.chooseMessageFile({
      count: 5,
      type: 'file',
      extension: ['txt', 'pdf', 'docx'],
      success: ({ tempFiles }) => this.uploadFiles(tempFiles || [])
    })
  },

  uploadSingle(file) {
    const app = getApp()
    if (app.globalData.transport === 'cloud-container') {
      return new Promise((resolve, reject) => {
        let fileID = ''
        const cleanup = () => {
          if (!fileID || !wx.cloud || !wx.cloud.deleteFile) return
          wx.cloud.deleteFile({ fileList: [fileID], success: () => {} })
        }
        wx.cloud.uploadFile({
          cloudPath: `documents/${Date.now()}-${file.name}`,
          filePath: file.path,
          success: uploadResult => {
            fileID = uploadResult.fileID
            wx.cloud.getTempFileURL({
              fileList: [fileID],
              success: urlResult => {
                const item = (urlResult.fileList || []).find(entry => entry.fileID === fileID)
                if (!item || !item.tempFileURL) {
                  cleanup()
                  return reject(new Error('Cloud storage URL unavailable'))
                }
                request({
                  path: '/documents/import-url',
                  method: 'POST',
                  data: { url: item.tempFileURL, filename: file.name }
                }).then(result => { cleanup(); resolve(result) }).catch(error => { cleanup(); reject(error) })
              },
              fail: () => { cleanup(); reject(new Error('Cloud storage URL unavailable')) }
            })
          },
          fail: () => reject(new Error('Cloud storage upload failed'))
        })
      })
    }
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: `${app.globalData.apiBaseUrl}/documents`,
        filePath: file.path,
        name: 'files',
        header: { Authorization: `Bearer ${wx.getStorageSync('accessToken') || ''}` },
        success: response => {
          let payload = response.data
          if (typeof payload === 'string') {
            try { payload = JSON.parse(payload) } catch { payload = {} }
          }
          if (response.statusCode >= 200 && response.statusCode < 300) return resolve(payload)
          reject(new Error(formatUploadError(response.statusCode, payload)))
        },
        fail: () => reject(new Error('无法连接知识库服务'))
      })
    })
  },

  uploadFiles(files) {
    const invalid = (files || []).map(validateFile).find(Boolean)
    if (invalid) {
      this.setData({ errorMessage: invalid })
      return wx.showToast({ title: invalid, icon: 'none' })
    }
    if (!files || !files.length) return

    this.setData({ uploading: true, uploadProgress: 0, errorMessage: '' })
    const uploadNext = index => {
      if (index >= files.length) {
        this.setData({ uploading: false, uploadProgress: 100 })
        wx.showToast({ title: '资料导入完成', icon: 'success' })
        return this.loadDocuments()
      }
      this.uploadSingle(files[index])
        .then(() => {
          this.setData({ uploadProgress: Math.round(((index + 1) / files.length) * 100) })
          uploadNext(index + 1)
        })
        .catch(error => {
          this.setData({ uploading: false, errorMessage: error.message })
          wx.showToast({ title: error.message, icon: 'none' })
        })
    }
    uploadNext(0)
  },

  rebuildDocuments() {
    if (this.data.rebuilding) return
    this.setData({ rebuilding: true, errorMessage: '' })
    request({ path: '/documents/rebuild', method: 'POST' })
      .then(() => {
        wx.showToast({ title: '索引重建完成', icon: 'success' })
        this.loadDocuments()
      })
      .catch(error => this.setData({ errorMessage: error.message }))
      .finally(() => this.setData({ rebuilding: false }))
  }
})

module.exports = { validateFile, formatUploadError }
