<template>
  <div class="workspace"
       @mousedown="handleMouseDown">
    <img :src="Img" alt="当前图片" ref="image" draggable="false" />
  </div>
</template>

<script>
export default {
  name: 'Workspace',
  props: {
    Img: {
      type: String,
      default: null
    }
  },
  data () {
    return {
      clickTimeout: null, // 用于检测双击定时器
      laskClickTime: 0 // 上一次点击时间
    }
  },
  methods: {
    handleMouseDown (event) {
      if (event.button !== 0) return // 仅处理左键点击

      const currentTime = new Date().getTime()
      const timeSinceLastClick = currentTime - this.lastClickTime

      if (timeSinceLastClick < 300) {
        clearTimeout(this.clickTimeout) // 如果在300ms内再次点击，取消之前的单击事件
        this.lastClickTime = 0 // 重置点击时间
      } else {
        this.lastClickTime = currentTime

        this.clickTimeout = setTimeout(() => {
          console.log('Single click detected')
          this.sendCoordinates(event)
        }, 300) // 延迟300ms后判断为单击事件
      }
    }
    // sendCoordinates (event) {
    //   const img = this.$refs.image
    //   const rect = img.getBoundingClientRect()

    //   // 计算鼠标点击的坐标相对于图片的位置
    //   const x = event.clientX - rect.left
    //   const y = event.clientY - rect.top

    //   // 发送坐标到后端
    //   fetch('http://localhost:5001/click_coordinates', {
    //     method: 'POST',
    //     headers: {
    //       'Content-Type': 'application/json'
    //     },
    //     body: JSON.stringify({ x, y })
    //   })
    //     .then(response => response.json())
    //     .then(data => {
    //       console.log('Coordinates sent successfully:', data)
    //     })
    //     .catch(error => {
    //       console.error('Error sending coordinates:', error)
    //     })
    // }
  }
}
</script>

<style scoped>
.workspace {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000000;
}
img {
  max-width: 100%;
  max-height: 100%;
}
</style>
