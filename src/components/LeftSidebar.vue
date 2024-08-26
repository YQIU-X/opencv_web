<template>
  <div class="left-sidebar" @click.stop>
    <div @click="toggleSection('files')" class="sidebar-section">
      <h2>文件</h2>
      <transition name="slide-fade">
        <ul v-if="expandedSection === 'files'">
          <li @click.stop="triggerFileInput">打开照片</li>
          <li>打开文件夹</li>
          <li>覆盖原图</li>
          <li>另存为</li>
        </ul>
      </transition>
    </div>
    <div @click="toggleSection('favorites')" class="sidebar-section">
      <h2>收藏夹</h2>
      <transition name="slide-fade">
        <div v-if="expandedSection === 'favorites'" class="photo-container">
          <div v-for="photo in photos" :key="photo.id" class="photo-item">
            <img :src="photo.src" @click.stop="setCurrentImage(photo.src)" />
            <button @click.stop="removePhoto(photo.id)">删除</button>
          </div>
          <button @click.stop="addPhoto">添加照片</button>
        </div>
      </transition>
    </div>

    <!-- 隐藏的文件输入框 -->
    <input type="file" ref="fileInput" @change="handleFileUpload" multiple style="display: none;" />
  </div>
</template>

<script>
export default {
  name: 'LeftSidebar',
  data () {
    return {
      expandedSection: null,
      photos: [],
      nextPhotoId: 1
    }
  },
  methods: {
    toggleSection (section) {
      this.expandedSection = this.expandedSection === section ? null : section
    },
    triggerFileInput () {
      this.$refs.fileInput.click()
    },
    handleFileUpload (event) {
      const files = event.target.files
      const newPhotos = []

      Array.from(files).forEach(file => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const newPhoto = {
            id: this.nextPhotoId,
            src: e.target.result
          }
          newPhotos.push(newPhoto)
          this.nextPhotoId++

          if (newPhotos.length === files.length) {
            // 将新照片添加到现有的照片列表中
            this.photos = [...this.photos, ...newPhotos]
            // 触发事件，将更新后的照片数组传递给父组件
            this.$emit('update-images', this.photos)
          }
        }
        reader.readAsDataURL(file)
      })
    },
    removePhoto (id) {
      this.photos = this.photos.filter(photo => photo.id !== id)
      // 触发事件，将更新后的照片数组传递给父组件
      this.$emit('update-images', this.photos)
    },
    addPhoto () {
      const examplePhotoSrc = 'https://via.placeholder.com/50'
      this.photos.push({
        id: this.nextPhotoId,
        src: examplePhotoSrc
      })
      this.nextPhotoId++
      // 触发事件，将更新后的照片数组传递给父组件
      this.$emit('update-images', this.photos)
    },
    setCurrentImage (src) {
      this.$emit('update-image', src)
    },
    handleClickOutside (event) {
      if (!this.$el.contains(event.target)) {
        this.expandedSection = null
      }
    }
  },
  mounted () {
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeDestroy () {
    document.removeEventListener('click', this.handleClickOutside)
  }
}
</script>

<style scoped>
.left-sidebar {
  width: 200px;
  padding: 10px;
  background-color: #2c2c2c;
  color: #ffffff;
}

.sidebar-section {
  cursor: pointer;
  margin-bottom: 10px;
}

ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

li {
  padding: 5px 0;
  padding-left: 10px;
}

.photo-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px;
}

.photo-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 50px;
  height: 100px;
}

img {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border: 1px solid #fff;
  margin-bottom: 5px;
}

button {
  background-color: #444;
  color: #fff;
  border: none;
  padding: 5px;
  cursor: pointer;
  font-size: 12px;
}

button:hover {
  background-color: #666;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter, .slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
