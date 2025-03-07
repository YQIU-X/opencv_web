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
    <!-- 隐藏的文件输入框 -->
    <input type="file" ref="fileInput" @change="handleFileUpload" multiple style="display: none;" />
    <!-- 用于选择文件夹的文件输入框 -->
    <input type="file" ref="folderInput" @change="handleFolderUpload" webkitdirectory style="display: none;" />

    <!-- 左下角按钮 -->
    <div class="bottom-button">
      <button @click="goToMeitu">跳转至MEITU</button>
      <button @click="handleButtonClick">工作台</button>
    </div>
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
      expandedSection: null
    }
  },
  methods: {
    goToMeitu () {
      window.open('https://pc.meitu.com/toolbox', '_blank') // 打开新页面
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
    },
    handleButtonClick () {
      this.$emit('workspace-clicked') // 触发事件，向父组件发送信号
    }

  }
}
</script>

<style scoped>
.sidebar-section h2 {
  text-align: center; /* 使标题水平居中 */
}

.left-sidebar {
  width: 200px;
  padding: 10px;
  background-color: #2c2c2c;
  color: #ffffff;
  position: relative;
}

.sidebar-section {
  cursor: pointer;
  margin-bottom: 10px;
}

ul {
  margin: 0;
  padding: 0;
  list-style: none;
  border: 5px solid #0c0606cc; /* 增加黑色外框 */
  border-radius: 12px; /* 可选：增加圆角 */
}

li {
  padding: 5px 0;
  padding-left: 10px;
}

.bottom-button {
  position: absolute;
  bottom: 10px;
  left: 0;
  width: 100%;
}

button {
  background-color: #4a4a4a;
  color: white;
  border: none;
  padding: 10px 0;
  width: 100%;
  cursor: pointer;
  font-size: 14px;
}

button:hover {
  background-color: #6a6a6a;
}
</style>
