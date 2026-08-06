const { request } = require('../../utils/request')

Page({
  data: {
    documents: [], documentCount: 0, chunkCount: 0, questionCount: 0,
    question: '', answer: '', sources: [], loading: false, overviewError: ''
  },
  onShow() { this.loadOverview() },
  loadOverview() {
    request({ path: '/documents' })
      .then(result => {
        const documents = result.items || []
        this.setData({
          documents,
          documentCount: documents.length,
          chunkCount: documents.reduce((total, item) => total + Number(item.chunks || 0), 0),
          overviewError: ''
        })
      })
      .catch(error => this.setData({ overviewError: error.message }))
  },
  openDocuments() { wx.switchTab({ url: '/pages/documents/index' }) },
  chooseFile() { this.openDocuments() },
  onQuestionInput(e) { this.setData({ question: e.detail.value }) },
  askQuestion() {
    const question = this.data.question.trim()
    if (!question) return wx.showToast({ title: '请输入问题', icon: 'none' })
    this.setData({ loading: true, answer: '', sources: [] })
    request({ path: '/chat', method: 'POST', data: { question, top_k: 4 } })
      .then(result => this.setData({
        answer: result.answer,
        sources: result.sources || [],
        questionCount: this.data.questionCount + 1
      }))
      .catch(error => wx.showToast({ title: error.message, icon: 'none' }))
      .finally(() => this.setData({ loading: false }))
  }
})
