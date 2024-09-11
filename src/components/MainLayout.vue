<template>
  <div class="main-layout">
    <LeftSidebar
      :currentImage="currentImage ? currentImage : {}"
      @upload_images="upload_images"
      @workspace-clicked="handleWorkspaceClick"
    />
    <div class="content">
      <!-- 传递 brushSize 和 selectedColor 到 Workspace -->
      <Workspace
        :Img="currentImage ? currentImage.src : ''"
        :brushSize="paint_size"
        :selectedColor="paint_color"
        @coordinate-clicked="handleCoordinate"
        @draw-clicked="handleDraw"
      />
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
      ref="RightSidebar"
      :Image="currentImage ? currentImage : {}"
      @set-operation="setOperation"
      @apply-Crop="applyCropOperation"
      @cancel-Crop="cancleCrop"
      @update-settings="updateSettings"
      @undo-action="undoAction"
      @next-image="nextImage"
      @confirm-changes="handleConfirmChanges"
      @brush-size-changed="handleBrushSizeChange"
      @brush-color-changed="handleBrushColorChange"
      @update-rotation="handleUpdateRotation"
      @apply-filter="applyFilter"
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
      currentOperation: null, // 记录当前操作类型
      paint_color: null, // 画笔颜色
      paint_size: 10, // 画笔大小
      points: [], // 用来存点
      images: [] // 用来存工作台图片
    }
  },
  methods: {
    handleWorkspaceClick () {
      console.log('工作台按钮被点击了，执行相关逻辑')
      this.isGalleryExpanded = true
      this.images = []
      this.currentOperation = 'workspace'
    },
    applyFilter (filterName) {
      if (!this.currentImage || !this.currentImage.id) {
        console.error('No image selected or image ID missing')
        return
      }
      // 发起POST请求，将图片ID和滤镜名称传递到后端
      fetch('http://localhost:5015/apply_filter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          image_id: this.currentImage.id, // 传递当前图像的ID
          filter: filterName // 传递选中的滤镜名称
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok')
          }
          return response.json()
        })
        .then(data => {
          // 更新当前图片，假设后端返回处理后的图片
          this.currentImage = {
            id: data.id,
            src: `data:image/jpeg;base64,${data.src}`, // 假设后端返回的是base64编码的图片数据
            config: data.config
          }
          this.select_image(this.currentImage) // 更新图片显示
          this.$refs.bottomGallery.updateImages() // 更新底部画廊
        })
        .catch(error => {
          console.error('Error applying filter:', error)
        })
    },
    handleDraw (x, y, scaleX, scaleY, type) {
      console.log('handleDraw')
      console.log(this.currentOperation)

      if (this.currentOperation !== 'paint') return

      if (type === 'dragging') {
        // 当拖动时，将x, y存储到points数组中
        this.points.push({ x, y })
      } else if (type === 'drag-end') {
        console.log('this.paint_color', this.paint_color)
        fetch('http://localhost:5014/draw', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            id: this.currentImage.id,
            points: this.points,
            paint_color: this.paint_color,
            paint_size: this.paint_size,
            scaleX: scaleX,
            scaleY: scaleY,
            type: type
          })
        })
          .then(response => response.json())
          .then(data => {
            this.currentImage = {
              id: data.id,
              src: `data:image/jpeg;base64,${data.src}`,
              config: data.config
            }
            this.select_image(this.currentImage)
            this.points = []
          })
          .catch(error => {
            console.error('Error drawing:', error)
          })
      }
    },
    handleBrushSizeChange (size) {
      console.log('handleBrushSizeChange', size)
      this.paint_size = size
    },
    handleBrushColorChange (color) {
      console.log('handleBrushColorChange', color)
      this.paint_color = color
    },
    handleUpdateRotation (roll, yaw, pitch) {
      fetch('http://localhost:5012/update_rotation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id: this.currentImage.id, // 当前图像的 ID
          roll: roll,
          yaw: yaw,
          pitch: pitch
        })
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
          console.error('Error updating rotation:', error)
        })
    },
    setOperation (operation) {
      this.currentOperation = operation
      if (operation === 'freeCrop' || operation === 'rectCrop' || operation === 'paint') return
      this.isGalleryExpanded = true
      this.tempImage1 = null
      this.tempImage2 = null
    },
    cancleCrop () {
      if (this.currentImage && this.currentOperation) {
        fetch('http://localhost:5010/cancel_crop', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            id: this.currentImage.id,
            currentOperation: this.currentOperation
          })
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
            console.error('Error cancelling crop:', error)
          })
      }
    },
    handleCoordinate (x, y, scaleX, scaleY, type) {
      if ((this.currentOperation === 'freeCrop' || this.currentOperation === 'rectCrop') && this.currentImage) {
        fetch('http://localhost:5001/crop', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            point: { x: x, y: y },
            imageId: this.currentImage.id,
            currentOperation: this.currentOperation,
            scale: { scaleX: scaleX, scaleY: scaleY }
          })
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
            console.error('Error sending coordinates:', error)
          })
      }
    },
    applyCropOperation () {
      if (this.currentImage) {
        fetch('http://localhost:5011/apply_Crop', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            id: this.currentImage.id,
            src: this.currentImage.src
          })
        })
          .then(response => response.json())
          .then(data => {
            console.log('stop')
            this.currentImage = {
              id: data.id,
              src: `data:image/jpeg;base64,${data.src}`,
              config: data.config
            }
            this.select_image(this.currentImage)
            this.$refs.bottomGallery.updateImages()
          })
          .catch(error => {
            console.error('Error applying freeCrop:', error)
          })
      }
    },
    selectTempImage (image) {
      if (this.currentOperation === null) return
      if (this.currentOperation === 'workspace') {
        this.images.push(image)
        return
      }
      if (!this.tempImage1) {
        this.tempImage1 = image
      } else if (!this.tempImage2) {
        if (this.currentOperation === 'histogram-equalization') {
          this.tempImage1 = image
        } else {
          this.tempImage2 = image
        }
      } else {
        this.tempImage1 = image
        this.tempImage2 = null
      }
    },
    handleConfirmChanges () {
      console.log(this.currentOperation)

      if (this.currentOperation === 'workspace' && this.images.length !== 0) {
        console.log('go to the new page')
        const clonedImages = JSON.parse(JSON.stringify(this.images))
        const targetRoute = {
          name: 'ImgGeoTransf',
          query: {
            images: encodeURIComponent(JSON.stringify(clonedImages))
          }
        }

        // 检查当前路由与目标路由是否相同，避免重复导航
        if (this.$route.name !== 'ImgGeoTransf' || this.$route.query.images !== targetRoute.query.images) {
          try {
            this.$router.push(targetRoute) // 执行路由跳转
          } catch (error) {
            if (error.name !== 'NavigationDuplicated') {
              console.error(error)
            }
          }
        }
        return
      }

      if (this.currentOperation === 'image-segmentation' && this.tempImage1) {
        this.applyImageSegmentation()
      }
      if (this.currentOperation === 'style-transfer' && this.tempImage1 && this.tempImage2) {
        this.applyStyleTransfer()
      }
      if ((this.currentOperation === 'image-stitch' && this.tempImage1 && this.tempImage2) ||
       (this.currentOperation === 'histogram-equalization' && this.tempImage1) ||
       (this.currentOperation === 'Identification-photo-production' && this.tempImage1)) {
        console.log('handleConfirmChanges')
        this.applyWUDILE(this.currentOperation)
      }
      this.tempImage1 = null
      this.tempImage2 = null
    },
    applyWUDILE (operation) {
      fetch('http://localhost:5013/administrator', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          Image1: this.tempImage1 ? this.tempImage1.id : null,
          Image2: this.tempImage2 ? this.tempImage2.id : null,
          operation: operation
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
    },
    applyStyleTransfer () {
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
      }
    },
    applyImageSegmentation () {
      if (this.tempImage1) {
        fetch('http://localhost:5009/seg_human', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            seg_img_id: this.tempImage1.id,
            background_img_id: this.tempImage2 ? this.tempImage2.id : null
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
    select_image (image) {
      this.currentImage = image
      this.$refs.RightSidebar.updateConfig()
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
          this.currentImage = {
            id: data.id,
            src: `data:image/jpeg;base64,${data.src}`,
            config: data.config
          }
          this.$refs.bottomGallery.updateImages()
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
      // this.currentOperation = null
      this.isGalleryExpanded = false
    },
    handleKeydown (event) {
    // 检查是否按下了Ctrl（或Command）和Z键
      if ((event.ctrlKey || event.metaKey) && (event.key === 'z' || event.key === 'Z')) {
        event.preventDefault() // 防止默认行为
        this.undoAction() // 调用撤销操作
      }
    },
    undoAction () {
      this.clean()
      // this.currentOperation = null
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
            this.$refs.RightSidebar.updateConfig()
            this.$refs.RightSidebar.toggleSection('')
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
      if (this.currentOperation === 'freeCrop' || this.currentOperation === 'rectCrop' || this.currentOperation === 'paint') {
        return
      }
      const bottomGallery = this.$refs.bottomGallery.$el
      const RightSidebar = this.$refs.RightSidebar ? this.$refs.RightSidebar.$el : null
      const Workspace = this.$refs.Workspace ? this.$refs.Workspace.$el : null
      if ((this.isGalleryExpanded &&
      !bottomGallery.contains(event.target) &&
       (!RightSidebar || !RightSidebar.contains(event.target))
      ) ||
        (!Workspace || !Workspace.contains(event.target))) {
        this.tempImage1 = null
        this.tempImage2 = null
        this.isGalleryExpanded = false
        this.currentOperation = null
      }
    }
  },
  mounted () {
    this.$refs.bottomGallery.updateImages()
    this.paint_color = null
    document.addEventListener('click', this.handleClickOutside)
    document.addEventListener('keydown', this.handleKeydown)
  },
  beforeDestroy () {
    document.removeEventListener('click', this.handleClickOutside)
    document.removeEventListener('keydown', this.handleKeydown)
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
