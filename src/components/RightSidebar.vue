<template>
  <div class="right-sidebar">
    <h3 class="image-title">直方图</h3>
    <div class="histogram-section">
      <div class="image-container">
        <img :src="histogramImage" alt="直方图" class="histogram-img" />
      </div>
    </div>
    <!-- Add a row of connected buttons here -->
    <div class="button-row">
      <button @click="saveSettings" class="connected-button">1</button>
      <button @click="saveSettings" class="connected-button">2</button>
      <button @click="saveSettings" class="connected-button">3</button>
      <button @click="saveSettings" class="connected-button">4</button>
    </div>
    <div>
      <label>色温</label>
      <input type="range" min="-100" max="100" v-model="temprature" @input="emitChanges" />
      <span>{{ temprature }}</span>
    </div>
    <div>
      <label>色调</label>
      <input type="range" min="-90" max="90" v-model="hue" @input="emitChanges" />
      <span>{{ hue }}</span>
    </div>
    <div>
      <label>曝光</label>
      <input type="range" min="-100" max="100" v-model="exposure" @input="emitChanges" />
      <span>{{ exposure }}</span>
    </div>
    <div>
      <label>对比</label>
      <input type="range" min="-50" max="50" v-model="contrast" @input="emitChanges" />
      <span>{{ contrast }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RightSidebar',
  props: {
    selectedImage: {
      type: String,
      default: ''
    },
    backendImage: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      histogramImage: '',
      temprature: 0,
      hue: 0,
      exposure: 0,
      contrast: 0
    }
  },
  watch: {
    backendImage: {
      immediate: true,
      handler (newImage) {
        this.fetchHistogram(newImage)
      }
    }
  },
  methods: {
    fetchHistogram (imageData) {
      fetch('http://localhost:5003/upload_image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData })
      })
        .then(response => response.json())
        .then(data => {
          this.histogramImage = `data:image/jpeg;base64,${data.image}`
        })
        .catch(error => {
          console.error('Error fetching histogram:', error)
        })
    },
    emitChanges () {
      // 发送更新设置的请求
      this.$emit('update-settings', {
        temprature: this.temprature,
        hue: this.hue,
        exposure: this.exposure,
        contrast: this.contrast
      })
    },
    resetSettings () {
      // 重置所有设置为初始值
      this.temprature = 0
      this.hue = 0
      this.exposure = 0
      this.contrast = 0
      this.emitChanges()
    },
    applySettings () {
      // 应用当前设置
      this.emitChanges()
    },
    saveSettings () {
      // 保存当前设置
      console.log('Settings saved!')
    }
  }
}
</script>

<style scoped>
.right-sidebar {
  width: 300px;
  padding: 10px;
  background-color: #191515;
  color: #ffffff;
  position: relative; /* 使内部绝对定位的元素相对于此元素定位 */
}

.image-title {
  margin: 0;
  margin-bottom: 10px; /* 添加与下方图片的间距 */
  text-align: right; /* 将标题右对齐 */
}

.histogram-section {
  margin-bottom: 20px;
}

.histogram-img {
  width: 100%;
  height: auto;
  max-width: 300px;
  max-height: 200px;
}

.button-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.connected-button {
  flex: 1;
  padding: 10px 0;
  background-color: #3a3a3a;
  border: 1px solid #2c2c2c;
  color: #ffffff;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.connected-button:not(:last-child) {
  border-right: none; /* Remove border between buttons */
}

.connected-button:hover {
  background-color: #2c2c2c;
}

.right-sidebar div {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.right-sidebar label {
  width: 80px;
}

.right-sidebar input[type="range"] {
  flex: 1;
  margin: 0 10px;
}

.right-sidebar span {
  width: 40px;
  text-align: right;
}
</style>
