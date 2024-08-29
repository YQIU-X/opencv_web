<template>
  <div class="left-sidebar" @click.stop>
    <div @click="toggleSection('files')" class="sidebar-section">
      <h2>文件</h2>
      <transition name="slide-fade">
        <ul v-if="expandedSection === 'files'">
          <li @click.stop="triggerFileInput">打开照片</li>
          <li @click.stop="triggerFolderInput">打开文件夹</li>
          <li @click.stop="overwriteOriginal">覆盖原图</li>
          <li @click.stop="saveAs">另存为</li>
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
  props: ['backendImage'], // 接收从MainLayout传来的backendImage
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
    overwriteOriginal () {
      if (!this.backendImage) {
        console.warn('No image available to overwrite.')
        return
      }
      this.$emit('overwrite-image', this.backendImage)
    },
    processFiles (files) {
      const validExtensions = ['jpg', 'jpeg', 'png', 'gif', 'JPG']

      const newPhotos = []
      const filteredFiles = Array.from(files).filter(file => {
        const fileExtension = file.name.split('.').pop().toLowerCase()
        return validExtensions.includes(fileExtension)
      })

      if (filteredFiles.length === 0) {
        console.warn('No valid image files found.')
        return
      }

      filteredFiles.forEach(file => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const newPhotoSrc = e.target.result

          const photoExists = this.photos.some(photo => photo.src === newPhotoSrc)
          if (!photoExists) {
            const newPhoto = {
              id: this.nextPhotoId,
              src: newPhotoSrc
            }
            newPhotos.push(newPhoto)
            this.nextPhotoId++
          }

          if (newPhotos.length === filteredFiles.length) {
            this.photos = [...this.photos, ...newPhotos]
            this.$emit('update-images', this.photos)
          }
        }
        reader.readAsDataURL(file)
      })
    },
    async saveAs () {
      if (!this.backendImage) {
        console.warn('No image available to save.')
        return
      }

      try {
        // Generate a timestamp for the filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
        const suggestedName = `image-${timestamp}.jpg`

        const opts = {
          suggestedName: suggestedName, // Use the timestamp as the default filename
          types: [{
            description: 'Images',
            accept: { 'image/jpeg': ['.jpg', '.jpeg'] }
          }]
        }

        // Open the file save dialog
        const fileHandle = await window.showSaveFilePicker(opts)
        const writableStream = await fileHandle.createWritable()

        // Convert backendImage to Blob
        const response = await fetch(this.backendImage)
        const blob = await response.blob()

        // Write the file
        await writableStream.write(blob)
        await writableStream.close()
        console.log('File saved successfully.')
      } catch (err) {
        console.error('Error saving file:', err)
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
