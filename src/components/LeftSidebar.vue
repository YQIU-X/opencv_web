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
    <input type="file" ref="folderInput" @change="handleFolderUpload" webkitdirectory style="display: none;" />

    <!-- 左下角按钮 -->
    <div class="bottom-button">
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
      // 省略处理文件的代码
    },
    handleButtonClick () {
      this.$emit('workspace-clicked') // 触发事件，向父组件发送信号
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
