<template>
  <div class="bottom-gallery" @click.stop="hideContextMenu">
    <div
      v-for="image in Images"
      :key="image.id"
      class="thumbnail-wrapper"
      @click="selectImage(image)"
      @contextmenu.prevent="showContextMenu($event, image)"
    >
      <img
        :src="image.src"
        :class="{'selected': image.id === selectedImage.id}"
        class="thumbnail"
      />
    <div v-if="currentOperation === 'style-transfer' && (tempImage1 && image.id === tempImage1.id || tempImage2 && image.id === tempImage2.id)"
        class="overlay">
      <span>{{ tempImage1 && image.id === tempImage1.id ? 'content image' : 'style image' }}</span>
    </div>
     <div v-if="currentOperation === 'image-segmentation' && (tempImage1 && image.id === tempImage1.id || tempImage2 && image.id === tempImage2.id)"
          class="overlay">
        <span>{{ tempImage1 && image.id === tempImage1.id ? 'human image' : 'backg image' }}</span>
      </div>
      <div v-if="currentOperation === 'image-stitch' && (tempImage1 && image.id === tempImage1.id || tempImage2 && image.id === tempImage2.id)"
          class="overlay">
        <span>{{ tempImage1 && image.id === tempImage1.id ? 'lefttop image' : 'rightdown image' }}</span>
      </div>
      <div v-if="currentOperation === 'histogram-equalization' && (tempImage1 && image.id === tempImage1.id || tempImage2 && image.id === tempImage2.id)"
          class="overlay">
        <span>{{ tempImage1 && image.id === tempImage1.id ? 'selected image' : '' }}</span>
      </div>
      <div v-if="currentOperation === 'Identification-photo-production' && (tempImage1 && image.id === tempImage1.id || tempImage2 && image.id === tempImage2.id)"
          class="overlay">
        <span>{{ tempImage1 && image.id === tempImage1.id ? 'selected image' : '' }}</span>
      </div>
    </div>
    <div v-if="contextMenuVisible" :style="{ top: `${contextMenuY}px`, left: `${contextMenuX}px` }" class="context-menu">
      <ul>
        <li @click="removeImage(contextMenuImage.id)">移除</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BottomGallery',
  props: {
    selectedImage: {
      type: Object,
      default: () => ({
        id: '',
        src: '',
        config: {}
      })
    },
    currentOperation: { // 从 MainLayout 传递的操作
      type: String,
      default: ''
    },
    tempImage1: {
      type: Object,
      default: () => ({
        id: '',
        src: '',
        config: {}
      })
    },
    tempImage2: {
      type: Object,
      default: () => ({
        id: '',
        src: '',
        config: {}
      })
    }
  },
  data () {
    return {
      Images: [],
      contextMenuVisible: false,
      contextMenuX: 0,
      contextMenuY: 0,
      contextMenuImage: null
    }
  },
  methods: {
    updateImages () {
      fetch('http://localhost:5006/load_images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          return response.json()
        })
        .then(data => {
          if (data && data.images) {
            this.Images = data.images.map(image => ({
              id: image.id,
              src: `data:image/jpeg;base64,${image.img64}`,
              config: image.config
            }))

            if (this.Images.length > 0 && this.selectedImage == null) {
              this.selectImage(this.Images[0])
            }
          }
        })
        .catch(error => {
          console.error('erro update:', error)
        })
    },
    selectImage (image) {
      this.$emit('select-image', image)
    },
    removeImage (imageId) {
      this.$emit('remove-image', imageId)
      this.hideContextMenu()
      fetch('http://localhost:5002/remove_image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: imageId })
      })
        .then(response => response.json())
        .then(() => {
          this.updateImages()
        })
        .catch(error => {
          console.error('移除图片时出错:', error)
        })
    },
    showContextMenu (event, image) {
      this.contextMenuX = event.clientX
      this.contextMenuY = event.clientY
      this.contextMenuImage = image
      this.contextMenuVisible = true
    },
    hideContextMenu () {
      this.contextMenuVisible = false
    }
  }
}
</script>

<style scoped>
.bottom-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  grid-gap: 10px;
  padding: 10px;
  background-color: #1c1c1c;
  overflow-x: auto; /* 启用水平滚动 */
  justify-content: center;
  height: 120px;
  transition: height 0.3s ease;
  overflow-y: auto; /* 启用竖向滚动（如果需要） */
}

/* 自定义滚动条样式 */
.bottom-gallery::-webkit-scrollbar {
  width: 6px; /* 竖向滚动条的宽度 */
  height: 6px; /* 横向滚动条的高度 */
}

.bottom-gallery::-webkit-scrollbar-thumb {
  background-color: #4a4a4a; /* 滚动条的颜色 */
  border-radius: 3px; /* 滚动条圆角 */
}

.bottom-gallery::-webkit-scrollbar-track {
  background-color: #1c1c1c; /* 滚动条轨道背景色 */
}

.thumbnail-wrapper {
  position: relative;
  width: 100px; /* 确保缩略图容器的宽度与图片一致 */
  height: 100px; /* 确保缩略图容器的高度与图片一致 */
}

.thumbnail {
  width: 100%; /* 确保图片占满容器 */
  height: 100%; /* 确保图片占满容器 */
  object-fit: cover;
  transition: border 0.3s ease;
  box-sizing: border-box;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.5);
  display: flex;
  justify-content: center; /* 使蒙版内容居中 */
  align-items: center;
  pointer-events: none; /* 确保蒙版不会干扰点击事件 */
}

.overlay span {
  position: relative;
  font-size: 14px;
  font-weight: bold;
  color: black;
  text-transform: uppercase;
  white-space: normal; /* 允许换行 */
  padding: 0 10px; /* 适当的内边距以防文字贴边 */
}

.thumbnail.selected {
  border: 5px solid white;
}

.context-menu {
  position: absolute;
  background-color: #333;
  color: white;
  border-radius: 5px;
  padding: 5px;
  z-index: 1000;
}

.context-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.context-menu li {
  padding: 5px 10px;
  cursor: pointer;
}

.context-menu li:hover {
  background-color: #555;
}

/*蒙版*/
.expanded-gallery {
  height: 600px;
}

.thumbnail-wrapper {
  position: relative;
  width: 100px; /* 确保缩略图容器的宽度与图片一致 */
  height: 100px; /* 确保缩略图容器的高度与图片一致 */
}

.thumbnail {
  width: 100%; /* 确保图片占满容器 */
  height: 100%; /* 确保图片占满容器 */
  object-fit: cover;
  transition: border 0.3s ease;
  box-sizing: border-box;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.5);
  display: flex;
  justify-content: center; /* 使蒙版内容居中 */
  align-items: center;
  pointer-events: none; /* 确保蒙版不会干扰点击事件 */
}

.overlay span {
  position: relative;
  font-size: 14px;
  font-weight: bold;
  color: black;
  text-transform: uppercase;
  white-space: normal; /* 允许换行 */
  padding: 0 10px; /* 适当的内边距以防文字贴边 */
}

.thumbnail.selected {
  border: 5px solid white;
}

.context-menu {
  position: absolute;
  background-color: #333;
  color: white;
  border-radius: 5px;
  padding: 5px;
  z-index: 1000;
}

.context-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.context-menu li {
  padding: 5px 10px;
  cursor: pointer;
}

.context-menu li:hover {
  background-color: #555;
}
</style>
