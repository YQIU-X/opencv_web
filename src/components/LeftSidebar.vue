<template>
  <div class="left-sidebar" @click.stop>
    <div @click="toggleSection('files')" class="sidebar-section">
      <h2>文件</h2>
      <transition name="slide-fade">
        <ul v-if="expandedSection === 'files'">
          <li @click.stop="triggerFileInput">打开照片</li>
          <li @click.stop="triggerFolderInput">打开文件夹</li>
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
      expandedSection: null
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
