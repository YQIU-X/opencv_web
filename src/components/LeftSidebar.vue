<template>
  <div class="left-sidebar" @click.stop>
    <div @click="toggleSection('files')" class="sidebar-section">
      <h2>文件</h2>
      <transition name="slide-fade">
        <ul v-if="expandedSection === 'files'">
          <li @click.stop="triggerFileInput">打开照片</li>
          <li @click.stop="triggerFolderInput">打开文件夹</li>
          <li>覆盖原图</li>
          <li>另存为</li>
        </ul>
      </transition>
    </div>
    <!-- 隐藏的文件输入框 -->
    <input type="file" ref="fileInput" @change="handleFileUpload" multiple style="display: none;" />
    <!-- 用于选择文件夹的文件输入框 -->
    <input type="file" ref="folderInput" @change="handleFolderUpload" webkitdirectory style="display: none;" />
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
    triggerFolderInput () {
      this.$refs.folderInput.click()
    },
    handleFileUpload (event) {
      this.processFiles(event.target.files)
    },
    handleFolderUpload (event) {
      this.processFiles(event.target.files)
    },
    processFiles (files) {
      const validExtensions = ['jpg', 'jpeg', 'png', 'gif', 'JPG'] // 可根据需要修改

      const newPhotos = []
      const filteredFiles = Array.from(files).filter(file => {
        // 获取文件扩展名并转为小写
        const fileExtension = file.name.split('.').pop().toLowerCase()
        // 只处理有效扩展名的文件
        return validExtensions.includes(fileExtension)
      })

      // 如果没有有效的文件，则直接返回
      if (filteredFiles.length === 0) {
        console.warn('No valid image files found.')
        return
      }

      // 使用 filteredFiles 处理文件
      filteredFiles.forEach(file => {
        console.log(`Processing file: ${file.name}`) // 输出文件名到控制台

        const reader = new FileReader()
        reader.onload = (e) => {
          const newPhotoSrc = e.target.result
          console.log(`File loaded: ${file.name}`) // 文件加载成功后输出文件名

          const photoExists = this.photos.some(photo => photo.src === newPhotoSrc)
          if (!photoExists) {
            const newPhoto = {
              id: this.nextPhotoId,
              src: newPhotoSrc
            }
            newPhotos.push(newPhoto)
            this.nextPhotoId++
          }

          // 检查是否所有筛选后的文件都已处理
          if (newPhotos.length === filteredFiles.length) {
            this.photos = [...this.photos, ...newPhotos]
            this.$emit('update-images', this.photos)
          }
        }
        reader.readAsDataURL(file)
      })
    }
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

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter, .slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>

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

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter, .slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
