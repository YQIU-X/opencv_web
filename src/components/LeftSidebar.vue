<template>
  <div class="left-sidebar" @click.stop>
    <div @click="toggleSection('files')" class="sidebar-section">
      <h2>文件</h2>
      <transition name="slide-fade">
        <ul v-if="expandedSection === 'files'">
          <li @click.stop="triggerFileInput">打开照片</li>
          <li @click.stop="triggerFolderInput">打开文件夹</li>
          <li @click.stop="saveAs">另存为</li>
        </ul>
      </transition>
    </div>
    <div @click="toggleSection('operations')" class="sidebar-section">
      <h2>操作</h2>
      <transition name="slide-fade">
        <ul v-if="expandedSection === 'operations'">
          <li @click.stop="setOperation('style-transfer')">样式迁移</li>
          <li @click.stop="setOperation('image-segmentation')">图片分割</li>
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
  props: {
    currentImage: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      expandedSection: null,
      operation: null // 记录当前操作类型
    }
  },
  methods: {
    setOperation (operation) {
      this.operation = operation
      this.$emit('set-operation', operation)
    },
    applyStyleTransfer () {
      this.$emit('apply-style-transfer')
    },
    applyImageSegmentation () {
      this.$emit('apply-image-segmentation')
    },
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
      const formData = new FormData()

      Array.from(files).forEach(file => {
        formData.append('images', file)
      })

      fetch('http://localhost:5005/upload_images', {
        method: 'POST',
        body: formData
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Failed to upload images')
          }
          return response.json()
        })
        .then(data => {
          console.log('Received img from backend:', data.first_image)
          this.$emit('upload_images', {
            first_image: data.first_image,
            config: data.config
          })
        })
        .catch(error => {
          console.error('Error uploading images:', error)
        })
    },
    async saveAs () {
      if (!this.currentImage) return
      try {
        const defaultFileName = `${this.currentImage.id}.jpeg`
        const options = {
          suggestedName: defaultFileName,
          types: [{
            description: 'JPEG Image',
            accept: { 'image/jpeg': ['.jpeg', '.jpg'] }
          }]
        }
        const fileHandle = await window.showSaveFilePicker(options)
        const writableStream = await fileHandle.createWritable()
        const base64Response = await fetch(this.currentImage.src)
        const blob = await base64Response.blob()
        await writableStream.write(blob)
        await writableStream.close()
        console.log('Image saved successfully.')
      } catch (error) {
        console.error('Error saving image:', error)
      }
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
