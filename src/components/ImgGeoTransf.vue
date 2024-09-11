<template>
  <div class="container">
    <ul class="image-list">
      <li
        v-for="(image, index) in images"
        :key="index"
        :ref="'image-' + index"
        :style="{
          top: image.top + 'px',
          left: image.left + 'px',
          width: image.width + 'px',
          height: image.height + 'px',
          position: 'absolute',
          transform: 'rotate(' + image.rotation + 'deg)',
          border: '2px solid #000',
          boxSizing: 'border-box',
          zIndex: image.zIndex
        }"
        @mousedown="initDrag($event, index)"
        @contextmenu.prevent="showContextMenu($event, index)"
      >
        <img
          :src="image.src"
          alt="Image"
          @load="setImageOriginalSize(index, $event)"
          :style="{ width: image.width + 'px', height: image.height + 'px' }"
        />

        <!-- 等比例缩放 (右下角) -->
        <div class="resize-handle" @mousedown.stop="initResize($event, index, 'proportional')" />
        <!-- 水平方向缩放 (右边) -->
        <div class="resize-handle-right" @mousedown.stop="initResize($event, index, 'horizontal')" />
        <!-- 垂直方向缩放 (下边) -->
        <div class="resize-handle-bottom" @mousedown.stop="initResize($event, index, 'vertical')" />
        <!-- 旋转手柄 (顶部中心) -->
        <div class="rotate-handle" @mousedown.stop="initRotate($event, index)" />

        <!-- 如果顶点编辑模式启用，则显示四个角的顶点 -->
        <div
          v-if="image.editingVertices"
          class="vertex-handle top-left"
          :style="{ top: image.topLeft.y + 'px', left: image.topLeft.x + 'px' }"
          @mousedown.stop="initVertexDrag($event, index, 'topLeft')"
        ></div>
        <div
          v-if="image.editingVertices"
          class="vertex-handle top-right"
          :style="{ top: image.topRight.y + 'px', left: image.topRight.x + 'px' }"
          @mousedown.stop="initVertexDrag($event, index, 'topRight')"
        ></div>
        <div
          v-if="image.editingVertices"
          class="vertex-handle bottom-left"
          :style="{ top: image.bottomLeft.y + 'px', left: image.bottomLeft.x + 'px' }"
          @mousedown.stop="initVertexDrag($event, index, 'bottomLeft')"
        ></div>
        <div
          v-if="image.editingVertices"
          class="vertex-handle bottom-right"
          :style="{ top: image.bottomRight.y + 'px', left: image.bottomRight.x + 'px' }"
          @mousedown.stop="initVertexDrag($event, index, 'bottomRight')"
        ></div>

      </li>
    </ul>

    <!-- 右键菜单 -->
    <div v-if="contextMenuVisible" :style="{ top: contextMenuY + 'px', left: contextMenuX + 'px' }" class="context-menu">
      <ul>
        <li @click="bringToFront(selectedImageIndex)">置于顶层</li>
        <li @click="sendToBack(selectedImageIndex)">置于底层</li>
        <li @click="toggleVertexEdit(selectedImageIndex)">编辑顶点</li>
      </ul>
    </div>
  </div>
</template>

<script>

export default {
  data () {
    return {
      images: [], // 存储图片的数组，每个元素代表一张图片，包含图片的位置信息、大小、旋转角度等
      draggedImageIndex: null, // 当前正在拖动的图片索引，当用户拖动图片时，记录该图片的索引

      editingVertices: false, // 用于控制顶点编辑状态，决定是否显示图片的顶点编辑手柄

      resizing: false, // 用于指示是否正在进行图片的缩放操作
      rotating: false, // 用于指示是否正在进行图片的旋转操作
      dragging: false, // 用于指示是否正在进行图片的拖动操作
      resizeType: null, // 指示当前的缩放类型，可以是等比例缩放（proportional）、水平缩放（horizontal）或垂直缩放（vertical）

      vertexType: null, // 当前拖动的顶点类型

      offsetX: 0, // 用于记录拖动开始时鼠标相对图片左侧的偏移量，确保图片跟随鼠标拖动
      offsetY: 0, // 用于记录拖动开始时鼠标相对图片顶部的偏移量
      startX: 0, // 用于记录鼠标点击时的初始X坐标，便于计算拖动或缩放的位移
      startY: 0, // 用于记录鼠标点击时的初始Y坐标
      initialWidth: 0, // 用于存储图片在缩放开始时的初始宽度
      initialHeight: 0, // 用于存储图片在缩放开始时的初始高度
      initialRotation: 0, // 用于记录图片的初始旋转角度，便于旋转操作时计算旋转角度
      aspectRatio: 1, // 图片的宽高比，用于在等比例缩放时保持图片比例不变
      history: [], // 存储操作历史的数组，用于实现撤销功能，每次操作后保存当前状态
      undoIndex: -1, // 当前撤销的历史状态索引，表示可以撤销到的历史操作步骤

      contextMenuVisible: false, // 控制右键菜单的显示状态，决定是否显示右键菜单
      contextMenuX: 0, // 右键菜单的X坐标，决定菜单的横向位置
      contextMenuY: 0, // 右键菜单的Y坐标，决定菜单的纵向位置
      selectedImageIndex: null // 记录当前右键选中的图片的索引，便于在右键菜单中对该图片进行操作
    }
  },
  created () {
    const imagesData = this.$route.query.images
    if (imagesData) {
      const decodedImages = JSON.parse(decodeURIComponent(imagesData))
      this.images = decodedImages.map((image, idx) => ({
        ...image,
        top: 0,
        left: 0,
        rotation: 0, // 初始旋转角度
        zIndex: idx + 1, // 初始化 zIndex

        topLeft: { x: 0, y: 0 },
        topRight: { x: image.width, y: 0 },
        bottomLeft: { x: 0, y: image.height },
        bottomRight: { x: image.width, y: image.height },
        editingVertices: false // 初始化编辑顶点状态为 false
      }))
    } else {
      const storedImages = localStorage.getItem('storedImages')
      if (storedImages) {
        this.images = JSON.parse(storedImages)
      }
    }
    window.addEventListener('keydown', this.handleKeydown)
    window.addEventListener('click', this.hideContextMenu)
    window.addEventListener('click', this.handleGlobalClick)
  },
  beforeDestroy () {
    window.removeEventListener('keydown', this.handleKeydown)
    window.removeEventListener('click', this.hideContextMenu)
  },
  methods: {
    // 切换顶点编辑状态，用于开启或关闭顶点编辑模式
    toggleVertexEdit (index) {
      // 切换当前图片的顶点编辑状态
      this.$set(this.images[index], 'editingVertices', !this.images[index].editingVertices)
      console.log(this.images[index].editingVertices)
      // 隐藏右键菜单
      this.hideContextMenu()
    },

    // 初始化顶点拖动，用户点击顶点手柄时调用，准备进行顶点拖动操作
    initVertexDrag (event, index, vertex) {
      this.saveHistory() // 保存当前状态，用于撤销
      this.draggedImageIndex = index // 记录当前被拖动图片的索引
      this.vertexType = vertex // 记录正在拖动的顶点类型（四个顶点之一）
      this.startX = event.clientX // 记录鼠标开始拖动时的 X 坐标
      this.startY = event.clientY // 记录鼠标开始拖动时的 Y 坐标
      window.addEventListener('mousemove', this.dragVertex) // 监听鼠标移动事件，执行拖动操作
      window.addEventListener('mouseup', this.stopDragOrResize) // 监听鼠标松开事件，停止拖动
    },

    // 顶点拖动逻辑，用户在拖动顶点时动态更新图片的宽高和位置
    dragVertex (event) {
      if (this.draggedImageIndex !== null) {
        const image = this.images[this.draggedImageIndex]
        const dx = event.clientX - this.startX // 鼠标X方向移动的距离
        const dy = event.clientY - this.startY // 鼠标Y方向移动的距离

        // 根据顶点类型调整顶点位置
        switch (this.vertexType) {
          case 'topLeft':
            image.topLeft.x += dx
            image.topLeft.y += dy
            break
          case 'topRight':
            image.topRight.x += dx
            image.topRight.y += dy
            break
          case 'bottomLeft':
            image.bottomLeft.x += dx
            image.bottomLeft.y += dy
            break
          case 'bottomRight':
            image.bottomRight.x += dx
            image.bottomRight.y += dy
            break
        }

        // 更新鼠标起始坐标
        this.startX = event.clientX
        this.startY = event.clientY

        // 确保Vue的响应式更新
        this.$set(this.images, this.draggedImageIndex, image)
      }
    },
    // 当用户点击全局区域时，隐藏右键菜单
    handleGlobalClick (event) {
      this.hideContextMenu()
    },

    // 初始化图片拖动，用户按住图片开始拖动时触发
    initDrag (event, index) {
      if (this.resizing || this.rotating) {
        return // 如果正在缩放或旋转，则不允许拖动
      }
      this.saveHistory() // 保存当前状态，用于撤销
      this.draggedImageIndex = index // 记录当前拖动的图片索引
      const image = this.images[index]
      this.startX = event.clientX // 记录鼠标按下时的 X 坐标
      this.startY = event.clientY // 记录鼠标按下时的 Y 坐标
      this.offsetX = event.clientX - image.left // 计算鼠标相对图片左侧的偏移量
      this.offsetY = event.clientY - image.top // 计算鼠标相对图片顶部的偏移量
      this.dragging = true // 设置拖动状态为 true
      window.addEventListener('mousemove', this.dragImage) // 监听鼠标移动事件，执行拖动操作
      window.addEventListener('mouseup', this.stopDragOrResize) // 监听鼠标松开事件，停止拖动
    },

    // 图片拖动逻辑，用户拖动图片时更新图片的位置
    dragImage (event) {
      if (this.dragging && this.draggedImageIndex !== null) {
        const image = this.images[this.draggedImageIndex]
        // 更新图片的 left 和 top 属性，实现拖动效果
        image.left = event.clientX - this.offsetX
        image.top = event.clientY - this.offsetY
        this.$set(this.images, this.draggedImageIndex, image)
      }
    },

    // 初始化图片缩放操作，根据用户点击的缩放手柄类型开始缩放
    initResize (event, index, type) {
      this.saveHistory() // 保存当前状态，用于撤销
      this.draggedImageIndex = index // 记录当前正在缩放的图片索引
      this.resizeType = type // 记录当前缩放的类型（等比例、水平、垂直）
      const image = this.images[index]
      this.startX = event.clientX // 记录鼠标按下时的 X 坐标
      this.startY = event.clientY // 记录鼠标按下时的 Y 坐标
      this.initialWidth = image.width // 记录初始宽度
      this.initialHeight = image.height // 记录初始高度
      this.aspectRatio = image.aspectRatio // 记录宽高比
      this.resizing = true // 设置缩放状态为 true
      window.addEventListener('mousemove', this.resizeImage) // 监听鼠标移动事件，执行缩放操作
      window.addEventListener('mouseup', this.stopDragOrResize) // 监听鼠标松开事件，停止缩放
    },

    // 图片缩放逻辑，根据缩放类型（等比例、水平、垂直）动态调整图片的大小
    resizeImage (event) {
      if (this.resizing && this.draggedImageIndex !== null) {
        const image = this.images[this.draggedImageIndex]
        const dx = event.clientX - this.startX // 计算 X 方向的移动量
        const dy = event.clientY - this.startY // 计算 Y 方向的移动量
        // 根据缩放类型调整图片的宽高
        if (this.resizeType === 'proportional') {
          image.width = Math.max(this.initialWidth + dx, 20)
          image.height = image.width / this.aspectRatio // 保持宽高比不变
        } else if (this.resizeType === 'horizontal') {
          image.width = Math.max(this.initialWidth + dx, 20)
        } else if (this.resizeType === 'vertical') {
          image.height = Math.max(this.initialHeight + dy, 20)
        }
        this.$set(this.images, this.draggedImageIndex, image) // 更新图片属性
      }
    },

    // 初始化图片旋转操作，当用户点击旋转手柄时调用
    initRotate (event, index) {
      this.saveHistory() // 保存当前状态，用于撤销
      this.draggedImageIndex = index // 记录当前旋转的图片索引
      const image = this.images[index]
      this.startX = event.clientX // 记录鼠标按下时的 X 坐标
      this.startY = event.clientY // 记录鼠标按下时的 Y 坐标
      this.initialRotation = image.rotation // 记录初始旋转角度
      this.rotating = true // 设置旋转状态为 true
      window.addEventListener('mousemove', this.rotateImage) // 监听鼠标移动事件，执行旋转操作
      window.addEventListener('mouseup', this.stopDragOrResize) // 监听鼠标松开事件，停止旋转
    },

    // 图片旋转逻辑，根据鼠标的移动动态更新图片的旋转角度
    rotateImage (event) {
      if (this.rotating && this.draggedImageIndex !== null) {
        const image = this.images[this.draggedImageIndex]

        // 获取图片的中心点坐标
        const imageElement = this.$refs[`image-${this.draggedImageIndex}`][0]
        const rect = imageElement.getBoundingClientRect()
        const centerX = rect.left + rect.width / 2
        const centerY = rect.top + rect.height / 2

        // 计算鼠标相对中心点的角度
        const dx = event.clientX - centerX
        const dy = event.clientY - centerY
        const angle = Math.atan2(dy, dx) * (180 / Math.PI) + 90

        // 更新图片的旋转角度
        image.rotation = angle
        this.$set(this.images, this.draggedImageIndex, image) // 更新图片属性
      }
    },

    // 停止拖动、缩放或旋转操作，移除事件监听器
    stopDragOrResize () {
      this.dragging = false // 结束拖动
      this.resizing = false // 结束缩放
      this.rotating = false // 结束旋转
      this.draggedImageIndex = null // 清除拖动的图片索引
      // 移除鼠标事件监听器
      window.removeEventListener('mousemove', this.dragImage)
      window.removeEventListener('mousemove', this.resizeImage)
      window.removeEventListener('mousemove', this.rotateImage)
      window.removeEventListener('mouseup', this.stopDragOrResize)
    },

    // 显示右键菜单，记录当前右键选中的图片索引并显示菜单
    showContextMenu (event, index) {
      this.selectedImageIndex = index // 记录选中的图片索引
      this.contextMenuX = event.clientX // 记录右键点击的 X 坐标
      this.contextMenuY = event.clientY // 记录右键点击的 Y 坐标
      this.contextMenuVisible = true // 显示右键菜单
    },

    // 隐藏右键菜单
    hideContextMenu () {
      this.contextMenuVisible = false
    },

    // 将选中的图片置于顶层，更新 zIndex
    bringToFront (index) {
      const maxZIndex = Math.max(...this.images.map(image => image.zIndex)) // 获取当前最大的 zIndex
      this.images[index].zIndex = maxZIndex + 1 // 将选中的图片 zIndex 设置为最大值
      this.hideContextMenu() // 隐藏右键菜单
    },

    // 将选中的图片移到底层，更新 zIndex
    sendToBack (index) {
      const minZIndex = Math.min(...this.images.map(image => image.zIndex)) // 获取当前最小的 zIndex
      this.images[index].zIndex = Math.max(minZIndex - 1, 0) // 将选中的图片 zIndex 设置为最小值
      this.hideContextMenu() // 隐藏右键菜单
    },

    // 设置图片的原始大小，根据图片加载后的自然宽高设置缩放后的宽高
    setImageOriginalSize (index, event) {
      const img = event.target // 获取图片元素
      const image = this.images[index]
      const scaleFactor = 0.5 // 缩放比例
      image.width = img.naturalWidth * scaleFactor // 根据比例设置图片宽度
      image.height = img.naturalHeight * scaleFactor // 根据比例设置图片高度
      image.aspectRatio = img.naturalWidth / img.naturalHeight // 记录宽高比
      this.$set(this.images, index, image) // 更新图片属性
      image.topLeft = { x: 0, y: 0 }
      image.topRight = { x: image.width, y: 0 }
      image.bottomLeft = { x: 0, y: image.height }
      image.bottomRight = { x: image.width, y: image.height }

      // 更新 Vue 响应式数据
      this.$set(this.images, index, image)
    },

    // 保存操作历史，用于实现撤销功能
    saveHistory () {
      const snapshot = JSON.parse(JSON.stringify(this.images)) // 深拷贝当前图像状态
      this.history.push(snapshot) // 将当前状态推入历史记录中
      this.undoIndex = this.history.length - 1 // 更新撤销索引
    },

    // 键盘事件监听，Ctrl + Z 触发撤销操作
    handleKeydown (event) {
      if ((event.ctrlKey && event.key === 'z') || (event.ctrlKey && event.key === 'Z')) {
        this.undo() // 执行撤销操作
      }
    },

    // 撤销操作，回到上一个历史状态
    undo () {
      if (this.undoIndex > 0) {
        this.undoIndex-- // 回退撤销索引
        this.images = JSON.parse(JSON.stringify(this.history[this.undoIndex])) // 恢复上一个状态
      }
    }
  }
}
</script>

<style scoped>
/* 样式部分保持不变 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: auto;
}

body {
  background-color: white;
}

.container {
  position: relative;
  min-height: 100vh;
  padding: 20px;
}

.image-list {
  position: relative;
  width: 100%;
  height: 100%;
}

.image-list li {
  list-style-type: none;
  cursor: move;
  position: absolute;
  border: 2px solid #000;
  box-sizing: border-box;
}

.image-list img {
  padding: 0;
  background-color: transparent;
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
}

.resize-handle {
  width: 10px;
  height: 10px;
  background-color: #000;
  position: absolute;
  right: -5px;
  bottom: -5px;
  cursor: se-resize;
  border-radius: 50%;
}

.resize-handle-right {
  width: 10px;
  height: 100%;
  background-color: #000;
  position: absolute;
  right: -5px;
  top: 0;
  cursor: e-resize;
  border-radius: 50%;
}

.resize-handle-bottom {
  width: 100%;
  height: 10px;
  background-color: #000;
  position: absolute;
  bottom: -5px;
  cursor: s-resize;
  border-radius: 50%;
}

.rotate-handle {
  width: 10px;
  height: 10px;
  background-color: #000;
  position: absolute;
  top: -20px; /* 距离顶部中心一点 */
  left: 50%;  /* 水平居中 */
  transform: translateX(-50%);  /* 精确水平居中对齐 */
  cursor: pointer;
  border-radius: 50%;
}

/* 右键菜单样式 */
.context-menu {
  position: absolute;
  background-color: #fff;
  border: 1px solid #ccc;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  padding: 10px;
}

.context-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.context-menu ul li {
  padding: 8px 12px;
  cursor: pointer;
}

.context-menu ul li:hover {
  background-color: #f0f0f0;
}

.vertex-handle {
  width: 10px;
  height: 10px;
  background-color: red;
  position: absolute;
  cursor: pointer;
  border-radius: 50%;
}

.top-left {
  top: -5px;
  left: -5px;
}

.top-right {
  top: -5px;
  right: -5px;
}

.bottom-left {
  bottom: -5px;
  left: -5px;
}

.bottom-right {
  bottom: -5px;
  right: -5px;
}

</style>
