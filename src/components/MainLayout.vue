<template>
  <div class="main-layout">
    <LeftSidebar
      :currentImage="currentImage ? currentImage : {}"
      @upload_images="upload_images"
      @set-operation="setOperation"
    />
    <div class="content">
      <Workspace :Img="currentImage ? currentImage.src : ''"/>
      <BottomGallery
        ref="bottomGallery"
        :selectedImage="currentImage ? currentImage : {}"
        :tempImage1="tempImage1 ? tempImage1 : {}"
        :tempImage2="tempImage2 ? tempImage2 : {}"
        :currentOperation="currentOperation"
        @select-image="select_image"
        @remove-image="removeImage"
        :class="{ 'expanded-gallery': isGalleryExpanded }"
      />
    </div>
    <RightSidebar
      :temprature="currentImage ? currentImage.config.temprature : 0"
      :hue="currentImage ? currentImage.config.hue : 0"
      :exposure="currentImage ? currentImage.config.exposure : 0"
      :contrast="currentImage ? currentImage.config.contrast : 0"
      :sharpen="currentImage ? currentImage.config.sharpen : 0"
      :saturation="currentImage ? currentImage.config.saturation : 0"
      :Image="currentImage ? currentImage : null"
      @update-settings="updateSettings"
      @undo-action="undoAction"
      @next-image="nextImage"
    />
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
      currentImage: null, // {id, src 64, config}
      isGalleryExpanded: false, // 控制BottomGallery的高度
      tempImage1: null, // 存储第一张图片
      tempImage2: null, // 存储第二张图片
      currentOperation: null // 记录当前操作类型
    }
  },
  methods: {
    setOperation (operation) {
      this.currentOperation = operation
      this.isGalleryExpanded = true
    },
    selectTempImage (image) {
      console.log('selectTempImage')
      console.log(this.currentOperation)
      if (!this.tempImage1) {
        this.tempImage1 = image
      } else if (!this.tempImage2) {
        this.tempImage2 = image
        if (this.currentOperation === 'style-transfer') {
          this.applyStyleTransfer()
        }
        // this.currentOperation = null // 重置操作类型
      } else {
        this.tempImage1 = image
        this.tempImage2 = null
      }
    },
    async applyStyleTransfer () {
      if (this.tempImage1 && this.tempImage2) {
        // 将 tempImage1 和 tempImage2 传递到后端进行样式迁移
        fetch('http://localhost:5008/style_migration', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content_id: this.tempImage1.id,
            style_id: this.tempImage2.id
          })
        })
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok')
            }
            return response.json()
          })
          .then(data => {
            this.currentImage = {
              id: data.id,
              src: `data:image/jpeg;base64,${data.src}`,
              config: data.config
            }
            this.select_image(this.currentImage)
            this.$refs.bottomGallery.updateImages()
            this.clean()
          })
          .catch(error => {
            console.error('Error updating image:', error)
          })
        // this.clean()
      }
    },
    applyImageSegmentation () {
      if (this.tempImage1) {
        // 将 tempImage1 传递到后端进行图片分割
        this.clean()
      }
    },
    upload_images (data) { // get the current image
      if (data.first_image !== null && data.first_image !== undefined) {
        this.currentImage = {
          id: 1,
          src: `data:image/jpeg;base64,${data.first_image}`,
          config: data.config
        }
        this.select_image(this.currentImage)
      }
      this.$refs.bottomGallery.updateImages()
    },
    freshCurrentImage (img64, newConfig) {
      this.currentImage.src = img64
      this.currentImage.config = newConfig
      this.$refs.bottomGallery.updateImages()
    },
    select_image (image) {
      this.currentImage = image
      if (this.currentOperation) {
        console.log('this.currentOperation: ', this.currentOperation)
        this.selectTempImage(this.currentImage)
      }
    },
    updateSettings (settings) {
      if (!this.currentImage) return

      fetch('http://localhost:5000/adjust_image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...settings,
          image_id: this.currentImage.id
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok')
          }
          return response.json()
        })
        .then(data => {
          const base64Image = `data:image/jpeg;base64,${data.image}`
          this.freshCurrentImage(base64Image, data.config)
        })
        .catch(error => {
          console.error('Error updating image:', error)
        })
    },
    removeImage (imgId) {
      if (this.currentImage && this.currentImage.id === imgId) {
        this.currentImage = null
      }
    },
    clean () {
      this.tempImage1 = null
      this.tempImage2 = null
      this.currentOperation = null
      this.isGalleryExpanded = false
    },
    undoAction () {
      this.tempImage1 = null
      this.tempImage2 = null
      this.currentOperation = null
      this.isGalleryExpanded = false
      if (this.currentImage && this.currentImage.id) {
        fetch('http://localhost:5004/undo_action', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ id: this.currentImage.id })
        })
          .then(response => response.json())
          .then(data => {
            this.currentImage = {
              id: data.id,
              src: `data:image/jpeg;base64,${data.src}`,
              config: data.config
            }
            this.select_image(this.currentImage)
            this.$refs.bottomGallery.updateImages()
          })
          .catch(error => {
            console.error('Error in undoAction:', error)
          })
      }
    },
    nextImage () {
      if (this.currentImage && this.currentImage.id) {
        fetch('http://localhost:5007/next_image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ id: this.currentImage.id })
        })
          .then(response => response.json())
          .then(data => {
            this.currentImage = {
              id: data.id,
              src: `data:image/jpeg;base64,${data.src}`,
              config: data.config
            }
            this.select_image(this.currentImage)
          })
          .catch(error => {
            console.error('Error in nextImage:', error)
          })
      }
    },
    handleClickOutside (event) {
      const bottomGallery = this.$refs.bottomGallery.$el
      const leftSidebar = this.$refs.leftSidebar ? this.$refs.leftSidebar.$el : null

      if (this.isGalleryExpanded && !bottomGallery.contains(event.target) && (!leftSidebar || !leftSidebar.contains(event.target))) {
        this.clean()
      }
    }
  },
  mounted () {
    this.$refs.bottomGallery.updateImages()
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeDestroy () {
    document.removeEventListener('click', this.handleClickOutside)
  }
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 98vh;
  background-color: #000; /* 设置背景颜色为黑色，消除白色边框的视觉效果 */
  border: none; /* 确保没有边框 */
  outline: none; /* 确保没有轮廓 */
  margin: 0; /* 确保没有外边距 */
  padding: 0; /* 确保没有内边距 */
}
.left-sidebar {
  flex: 0 0 150px; /* 固定宽度 */
}

.right-sidebar {
  flex: 0 0 300px; /* 固定宽度 */
}

.content {
  flex: 1; /* 使内容占据剩余空间 */
  display: flex;
  flex-direction: column;
}

.workspace {
  flex: 1; /* 使工作区占用可用空间 */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000; /* 设置工作区背景色 */
  min-height: 200px; /* 设置最小高度 */
  max-height: calc(100vh - 100px); /* 设置最大高度，减去底部栏的高度 */
}

.bottom-gallery {
  height: 120px; /* 默认高度 */
  transition: height 0.3s ease; /* 过渡效果 */
}

.expanded-gallery {
  height: 600px; /* 伸长后的高度 */
}
</style>
