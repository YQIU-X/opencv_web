<template>
  <div class="main-layout">
    <LeftSidebar @update-images="updateImages" />
    <div class="content">
      <Workspace :currentImage="currentImage" />
      <BottomGallery :images="allImages" @select-image="updateCurrentImage" />
    </div>
    <RightSidebar @update-settings="updateSettings" />
  </div>
</template>

<script>
import LeftSidebar from './LeftSidebar.vue'
import Workspace from './Workspace.vue'
import RightSidebar from './RightSidebar.vue'
import BottomGallery from './BottomGallery.vue'

export default {
  name: 'MainLayout',
  components: {
    LeftSidebar,
    Workspace,
    RightSidebar,
    BottomGallery
  },
  data () {
    return {
      originalImages: [], // 所有选择的图片
      currentImage: '', // 当前显示的图片路径
      allImages: [] // 用于 BottomGallery 显示的图片
    }
  },
  methods: {
    updateImages (images) {
      this.allImages = images // 更新所有图片列表
      if (images.length > 0) {
        this.currentImage = images[0].src // 将第一个图片显示在 Workspace 中
      }
    },
    updateCurrentImage (imageSrc) {
      this.currentImage = imageSrc // 更新 Workspace 中显示的图片
    },
    updateSettings (settings) {
      if (!this.allImages.length) return // 确保至少有一张图片

      fetch('http://localhost:5000/adjust_image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...settings,
          image: this.allImages[0].src // 使用第一个图片进行调整
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok')
          }
          return response.json()
        })
        .then(data => {
          this.currentImage = `data:image/jpeg;base64,${data.image}`
        })
        .catch(error => {
          console.error('Error updating image:', error)
        })
    }
  }
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
}

.left-sidebar {
  flex: 0 0 200px; /* 固定宽度 */
}

.right-sidebar {
  flex: 0 0 300px; /* 固定宽度 */
}

.content {
  flex: 1; /* 让内容区占据剩余空间 */
  display: flex;
  flex-direction: column;
}

.workspace {
  flex: 1; /* 让工作区占据可用空间 */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000;
  min-height: 200px; /* 设置最小高度 */
  max-height: calc(100vh - 100px); /* 设置最大高度，减去底部栏高度 */
}

.bottom-gallery {
  height: 120px; /* 固定高度 */
  background-color: #1c1c1c;
  overflow-x: auto;
}
</style>
