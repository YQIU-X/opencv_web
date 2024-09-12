<template>
  <div class="right-sidebar">
    <h3 class="image-title">直方图</h3>
    <div class="histogram-section">
      <div class="image-container">
        <img :src="histogramImage" alt="直方图" class="histogram-img" />
      </div>
    </div>
    <!-- 按钮行 -->
  <div class="action-container">
    <div class="button-wrapper">
      <div class="button-row">
        <button @click="selectButton(1)" :class="{'connected-button': true, 'selected': selectedButton === 1}">
          <img src="../assets/dataIcon.png" alt="按钮1" class="button-icon4" />
        </button>
        <button @click="selectButton(2)" :class="{'connected-button': true, 'selected': selectedButton === 2}">
          <img src="../assets/crop.png" alt="按钮2" class="button-icon4" />
        </button>
        <button @click="selectButton(3)" :class="{'connected-button': true, 'selected': selectedButton === 3}">
          <img src="../assets/filter.png" alt="按钮3" class="button-icon4" />
        </button>
        <button @click="selectButton(4)" :class="{'connected-button': true, 'selected': selectedButton === 4}">
          <img src="../assets/bergerIcon.png" alt="按钮4" class="button-icon4" />
        </button>
      </div>
    </div>

    <div class="divider"></div>

    <!-- 根据 currentPage 显示不同的内容 -->
    <div v-if="currentPage === 1">
      <h3>白平衡</h3>
      <div class="slider-container">
        <label>色温</label>
        <input type="range" min="-100" max="100" v-model="temperature" @change="emitChanges" class="range-input" />
        <input type="number" min="-100" max="100" v-model="temperature" @change="emitChanges" class="number-input" />
      </div>
      <div class="slider-container">
        <label>色调</label>
        <input type="range" min="-90" max="90" v-model="hue" @change="emitChanges" class="range-input" />
        <input type="number" min="-90" max="90" v-model="hue" @change="emitChanges" class="number-input" />
      </div>
      <h3>色调</h3>
      <div class="slider-container">
        <label>曝光</label>
        <input type="range" min="-100" max="100" v-model="exposure" @change="emitChanges" class="range-input" />
        <input type="number" min="-100" max="100" v-model="exposure" @change="emitChanges" class="number-input" />
      </div>
      <div class="slider-container">
        <label>对比</label>
        <input type="range" min="-10" max="10" v-model="contrast" @change="emitChanges" class="range-input" />
        <input type="number" min="-10" max="10" v-model="contrast" @change="emitChanges" class="number-input" />
      </div>
      <h3>偏好</h3>
      <div class="slider-container">
        <label>锐化</label>
        <input type="range" min="0" max="100" v-model="sharpen" @change="emitChanges" class="range-input" />
        <input type="number" min="0" max="100" v-model="sharpen" @change="emitChanges" class="number-input" />
      </div>
      <div class="slider-container">
        <label>饱和</label>
        <input type="range" min="-50" max="50" v-model="saturation" @change="emitChanges" class="range-input" />
        <input type="number" min="-50" max="50" v-model="saturation" @change="emitChanges" class="number-input" />
      </div>
    </div>

<!-- 第二个页面的内容 -->
<div v-if="currentPage === 2">
  <div class="toggle-section" :class="{ expanded: expandedSection === 'rectCrop' }">
    <h4 @click.stop="toggleSection('rectCrop')">矩形裁剪</h4>
    <div v-if="expandedSection === 'rectCrop'" class="section-content">
      <div class="button-row">
        <button @click="cancelCrop">取消</button>
        <button @click="applyCrop">应用</button>
      </div>
    </div>
  </div>

  <div class="toggle-section" :class="{ expanded: expandedSection === 'freeCrop' }">
    <h4 @click.stop="toggleSection('freeCrop')">自由裁剪</h4>
    <div v-if="expandedSection === 'freeCrop'" class="section-content">
      <div class="button-row">
        <button @click="cancelCrop">取消</button>
        <button @click="applyCrop">应用</button>
      </div>
    </div>
  </div>

  <div class="toggle-section" :class="{ expanded: expandedSection === 'rotate' }">
    <h4 @click.stop="toggleSection('rotate')">图片旋转</h4>
    <div v-if="expandedSection === 'rotate'" class="section-content">
      <div class="slider-container vertical-slider">
<div class="slider-item">
  <label>Roll</label>
  <input type="range" min="-180" max="180" v-model="roll" @change="emitRotationChanges('roll')" />
  <input type="number" min="-180" max="180" v-model="roll" @change="emitRotationChanges('roll')" class="number-input" />
</div>
<div class="slider-item">
  <label>Yaw</label>
  <input type="range" min="-300" max="300" v-model="yaw" @change="emitRotationChanges('yaw')" />
  <input type="number" min="-300" max="300" v-model="yaw" @change="emitRotationChanges('yaw')" class="number-input" />
</div>
<div class="slider-item">
  <label>Pitch</label>
  <input type="range" min="-300" max="300" v-model="pitch" @change="emitRotationChanges('pitch')" />
  <input type="number" min="-300" max="300" v-model="pitch" @change="emitRotationChanges('pitch')" class="number-input" />
</div>
      </div>
      <div class="button-row">
        <button @click="cancelCrop">取消</button>
        <button @click="applyCrop">应用</button>
      </div>
    </div>
  </div>

  <!-- <div class="toggle-section" :class="{ expanded: expandedSection === 'resize' }"> -->
    <!-- <h4 @click.stop="toggleSection('resize')">调整大小</h4> -->
    <!-- <div v-if="expandedSection === 'resize'" class="section-content"> -->
      <!-- <button @click="performAction('resize')">操作按钮</button> -->
      <!-- <input type="range" v-model="resizeSlider" @input="emitZoneChanges" /> -->
    <!-- </div> -->
  <!-- </div> -->
</div>

<!-- 第三个页面的内容 -->
<div v-if="currentPage === 3">
  <div class="circle-container">
    <div
      v-for="(color, index) in circleColors"
      :key="index"
      :style="{ backgroundColor: color.color, backgroundImage: color.pattern ? 'url(' + color.pattern + ')' : '' }"
      :class="['color-circle', { 'selected-circle': selectedColor === color.name }]"
      @click="selectBrushColor(color)"
    >
      <span v-if="color.name === 'none'" class="slash">/</span>
    </div>
  </div>

  <div class="brush-size-container">
    <input type="range" id="brush-size" min="1" max="100" v-model="brushSize" @input="emitBrushSizeChange" />
    <span class="brush-size-value">{{ brushSize }}px</span>
  </div>

  <!-- 新增的滤镜按钮部分 -->
  <div class="filter-buttons-container">
    <div class="filter-button-row">
      <button @click="applyFilter('relief')" class="filter-button">浮雕</button>
      <button @click="applyFilter('grayscale')" class="filter-button">黑白</button>
    </div>
    <div class="filter-button-row">
      <button @click="applyFilter('pencil')" class="filter-button">简笔画</button>
      <button @click="applyFilter('stylization')" class="filter-button">水彩画</button>
    </div>
    <div class="filter-button-row">
      <button @click="applyFilter('fresh')" class="filter-button">鲜食滤镜</button>
      <button @click="applyFilter('obscure')" class="filter-button">模糊滤镜</button>
    </div>
    <div class="filter-button-row">
      <button @click="applyFilter('Glamorous')" class="filter-button">冷艳滤镜</button>
      <button @click="applyFilter('nostalgia')" class="filter-button">怀旧滤镜</button>
    </div>
  </div>
</div>

    <!-- 第四个页面的内容 -->
    <div v-if="currentPage === 4">
      <!-- 添加十个按钮 -->
    <div v-if="currentPage === 4">
      <!-- 手动添加十个按钮 -->
      <div class="button-container">
        <button class="extra-button" @click.stop="setOperation('style-transfer')">样式迁移</button>
        <button class="extra-button" @click.stop="setOperation('image-segmentation')">实例分割</button>
        <button class="extra-button" @click.stop="setOperation('image-stitch')">图像拼接</button>
        <button class="extra-button" @click.stop="setOperation('generate-puzzles')">生成拼图</button>
        <button class="extra-button" @click.stop="setOperation('histogram-equalization')">直方图均衡</button>
        <button class="extra-button" @click.stop="setOperation('Identification-photo-production')">证件照制作</button>
        <button class="extra-button" @click.stop="setOperation('stacks-mean')">图像堆栈<br>均值</button>
        <button class="extra-button" @click.stop="setOperation('stacks-max')">图象堆栈<br>最大值</button>
        <button class="extra-button">按钮 9</button>
        <button class="extra-button">按钮 10</button>
      </div>
    </div>
    </div>
    <div class="bottom-button-row">
      <button @click="$emit('undo-action')" class="bottom-button">撤回</button>
      <button @click="confirmChanges" class="bottom-button">确定</button>
      <button @click="$emit('next-image')" class="bottom-button">下一张</button>
    </div>
  </div>
</div>
</template>

<script>
export default {
  name: 'RightSidebar',
  props: {
    // temperature: {
    //   type: Number,
    //   default: 0
    // },
    // hue: {
    //   type: Number,
    //   default: 0
    // },
    // exposure: {
    //   type: Number,
    //   default: 0
    // },
    // contrast: {
    //   type: Number,
    //   default: 0
    // },
    // sharpen: {
    //   type: Number,
    //   default: 0
    // },
    // saturation: {
    //   type: Number,
    //   default: 0
    // },
    Image: {
      type: Object,
      default: null
    }
  },
  data () {
    return {
      selectedButton: 1,
      histogramImage: '',
      currentPage: 1,
      expandedSection: '', // 二区域当前展开的部分
      temperature: 0,
      hue: 0,
      exposure: 0,
      contrast: 0,
      sharpen: 0,
      saturation: 0,
      roll: 0,
      yaw: 0,
      pitch: 0,
      selectedColor: 'none',
      brushSize: 10,
      circleColors: [
        { name: 'none', color: 'transparent' }, // No color
        { name: 'red', color: 'red' },
        { name: 'green', color: 'green' },
        { name: 'blue', color: 'blue' },
        { name: 'yellow', color: 'yellow' },
        { name: 'black', color: 'black' },
        { name: 'white', color: 'white' },
        { name: 'recovery', color: 'transparent', pattern: require('../assets/repair.png') },
        { name: 'mosaic', color: 'transparent', pattern: require('../assets/OIP-C.jpg') } // Mosaic brush with a pattern
      ]
    }
  },
  watch: {
    currentPage (newVal) {
      if (newVal !== 2) {
        this.expandedSection = null
        this.$emit('set-operation', null)
      }
    },
    Image: {
      immediate: true,
      handler (newImage) {
        if (newImage && newImage.id) {
          this.fetchHistogram(newImage.id)
        }
      },
      deep: true
    }
  },
  methods: {
    applyFilter (filterName) {
      console.log(`Applying filter: ${filterName}`)
      this.$emit('apply-filter', filterName) // 向父组件发送应用滤镜的事件
    },
    selectBrushColor (color) {
      this.selectedColor = color.name
      if (this.selectedColor !== 'none') {
        console.log('selectBrushColor', color.name)
        this.setOperation('paint') // 若所选颜色不是 'none'，则将操作设置为 'paint'
      }
      this.$emit('brush-color-changed', color.name) // Emit event for the parent component
    },
    emitBrushSizeChange () {
      this.$emit('brush-size-changed', this.brushSize) // Emit brush size change event
    },
    selectButton (buttonNumber) {
      this.selectedButton = buttonNumber // 设置当前选中的按钮
      this.currentPage = buttonNumber // 根据选中的按钮更新 currentPage
      this.selectedColor = 'none'
      this.brushSize = 10
      this.setOperation(null)
      this.$nextTick(() => {
        this.$emit('brush-color-changed', this.selectedColor)
        this.$emit('brush-size-changed', this.brushSize)
      })
    },
    // ---------------------------二区域
    toggleSection (section) { // 在 toggleSection 方法中，判断是否是 freeCrop 操作，并调用 setFreeCropOperation 方法。
      this.expandedSection = this.expandedSection === section ? null : section
      if (section === 'freeCrop') {
        this.setOperation('freeCrop')
      } else if (section === 'rectCrop') {
        this.setOperation('rectCrop')
      }
    },
    emitRotationChanges (changed) {
      if (changed === 'roll') {
        this.yaw = 0
        this.pitch = 0
      } else if (changed === 'yaw') {
        this.roll = 0
        this.pitch = 0
      } else if (changed === 'pitch') {
        this.roll = 0
        this.yaw = 0
      }
      this.$emit('update-rotation', this.roll, this.yaw, this.pitch)
    },
    applyRotation () {
      this.$emit('apply-rotation', this.roll) // 通知父组件应用旋转
      this.roll = 0 // 恢复初始角度
    },
    // 应用
    applyCrop () {
      this.$emit('apply-Crop')
      this.roll = 0 // 恢复初始角度
      this.yaw = 0
      this.pitch = 0
    },
    // 取消
    cancelCrop () {
      this.roll = 0 // 恢复初始角度
      this.yaw = 0
      this.pitch = 0
      this.$emit('cancel-Crop')
    },
    // selectZone (zone) {
    //   this.selectedZone = zone
    //   this.$emit('zone-selected', zone) // 触发一个事件，通知父组件或其他逻辑
    // },
    // ---------------------------四区域
    setOperation (operation) {
      if (operation !== 'paint') {
        this.paint_color = 'none'
      }
      this.$emit('set-operation', operation)
    },
    emitChanges () {
      this.$emit('update-settings', {
        temperature: this.temperature,
        hue: this.hue,
        exposure: this.exposure,
        contrast: this.contrast,
        sharpen: this.sharpen,
        saturation: this.saturation
      })
    },
    fetchHistogram (id) {
      fetch('http://localhost:5003/fetch_histogram', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: id })
      })
        .then(response => response.json())
        .then(data => {
          this.histogramImage = `data:image/jpeg;base64,${data.image}`
        })
        .catch(error => {
          console.error('Error fetching histogram:', error)
        })
    },

    // ---------------------------底部
    confirmChanges () {
      this.$emit('confirm-changes')
    },
    emitUndoAction () {
      this.$emit('undo-action')
    },
    emitNextImage () {
      this.$emit('next-image')
    },
    updateConfig () {
      this.$nextTick(() => {
        if (this.Image && this.Image.config) {
          this.temperature = this.Image.config.temperature || 0
          this.hue = this.Image.config.hue || 0
          this.exposure = this.Image.config.exposure || 0
          this.contrast = this.Image.config.contrast || 0
          this.sharpen = this.Image.config.sharpen || 0
          this.saturation = this.Image.config.saturation || 0
        }
      })
    }
  }
}
</script>

<style scoped>
.image-container {
  border: 4px solid #0c0606cc;
  padding: 3px;
  background-color: #2c2c2c;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  border-radius: 8px;
  margin-bottom: 20px;
  max-width: 300px;
}

.action-container {
  border: 4px solid #0c0606cc;
  padding: 3px;
  background-color: #2c2c2c;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  border-radius: 8px;
  margin-top: 20px;
  padding-top: 5%;
  margin-bottom: 20px;
  max-width: 300px;
}

.divider {
  width: 100%;
  height: 10px;
  background-color: #000000b9;
  margin: 10px 0;
  border-radius: 5px;
}

.right-sidebar {
  width: 300px;
  padding: 10px;
  background-color: #2c2c2c;
  color: #ffffff;
  position: relative;
}

.image-title {
  margin: 0;
  margin-bottom: 10px;
  text-align: left;
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
  padding: 12px 0;
  background-color: #3a3a3a;
  border: 1px solid #2c2c2c;
  color: #ffffff;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s ease, border-color 0.3s ease, padding 0.3s ease;
  border-radius: 8px;
  margin: 0 5px;
}

.connected-button.selected,
.connected-button:hover {
  background-color: #000000 !important; /* 悬停和选中时的背景颜色设置为黑色 */
  border-color: #000000 !important; /* 悬停和选中时的边框颜色设置为黑色 */
}

.button-icon1 {
  width: 25px; /* 设置图标宽度 */
  height: 25px; /* 设置图标高度 */
}

.button-icon4 {
  width: 30px; /* 设置图标宽度 */
  height: 30px; /* 设置图标高度 */
}

.slider-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.slider-container label {
  flex: 0 0 50px; /* Set a fixed width for the label */
  font-size: 1em;
  margin-right: 0px;
  margin-left: 10px;
}

h3{
  margin: 0;
  display: flex;
  justify-content: center; /* 水平居中标题 */
  align-items: center; /* 垂直居中标题 */
  height: 50px; /* 设置固定高度来保持一致性 */
}

.slider-container input[type="range"] {
  flex: 1; /* Take up the remaining space */
  margin-right: 10px; /* Space between slider and value */
}

.number-input {
  width: 40px;
  text-align: center;
}

.slider-container span {
  flex: 0 0 30px; /* Set a fixed width for the value */
  font-size: 0.9em;
  text-align: right;
}

.button-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px; /* 增加按钮之间的间距 */
  justify-content: space-between;
}

.extra-button {
  flex: 1 1 45%; /* 设置每个按钮占据45%的宽度，保持两排并列 */
  padding: 10px;
  background-color: #3a3a3a;
  color: #ffffff;
  border: 1px solid #2c2c2c;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.extra-button:hover {
  background-color: #4a4a4a;
}

.bottom-button-row {
  position: absolute;
  bottom: 0;
  width: 95%; /* 确保按钮占据侧边栏的全部宽度 */
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  background-color: #2c2c2c; /* 设置背景色，以区分按钮和其他部分 */
}

.bottom-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.bottom-button {
  flex: 1;
  padding: 10px;
  background-color: #3a3a3a;
  color: #ffffff;
  border: 1px solid #2c2c2c;
  cursor: pointer;
  text-align: center;
  transition: background-color 0.3s ease;
}

.bottom-button:not(:last-child) {
  margin-right: 10px;
}

.bottom-button:hover {
  background-color: #4a4a4a;
}

/* 标题内容样式 */
.toggle-section {
  margin-bottom: 10px;
}

.toggle-section.expanded {
  border: 4px solid #0c0606cc; /* 展开时的边框颜色 */
  border-radius: 8px; /* 圆角 */
}

.toggle-section h4 {
  cursor: pointer;
  margin: 0;
  padding: 10px;
  background-color: transparent; /* 背景色与侧边栏一致 */
  color: #ffffff; /* 文字颜色 */
  border: 1px solid #2c2c2c; /* 标题的边框 */
  border-bottom: none; /* 去掉底部边框，以避免与内容分割线重叠 */
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.section-content {
  padding: 10px;
  padding-left: 30px; /* 内容缩进 */
  background-color: #2c2c2c;
  border: none; /* 去掉边框 */
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

/* 自由裁剪的按钮行 */
.button-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.button-row button {
  flex: 1;
  padding: 10px;
  background-color: #3a3a3a;
  color: #ffffff;
  border: 1px solid #2c2c2c;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border-radius: 8px;
}

.button-row button:not(:last-child) {
  margin-right: 10px; /* 按钮之间的间距 */
}

.button-row button:hover {
  background-color: #4a4a4a;
}

/*roll yaw pitch */
.vertical-slider {
  display: flex;
  flex-direction: column;
}

.slider-item {
  display: flex;
  align-items: center; /* 垂直居中 */
  margin-bottom: 20px;
}

.slider-item label {
  margin-right: 5px; /* 标签与滑动条之间的间距 */
  display: inline-block;
  min-width: 50px; /* 让标签宽度一致 */
}

.button-row {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}
/*颜色 */
.circle-container {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
}

.color-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 2px solid #ffffff;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.slash {
  color: #ffffff;
  font-size: 20px;
  line-height: 30px;
}

.selected-circle {
  border: 2px solid #ffcc00; /* Highlight color when selected */
}

/* Mosaic brush specific style, showing as a light gray circle with a pattern */
.color-circle[style*="mosaic-pattern.png"] {
  background-image: url('../assets/OIP-C.jpg'); /* Mosaic texture */
}

/* 大小滑动条 */
.brush-size-container {
  margin-top: 20px;
  display: flex;
  align-items: center;
}

.brush-size-container label {
  font-size: 14px;
  margin-right: 10px; /* 在标签和滑动条之间添加一些间距 */
}

.brush-size-container input[type="range"] {
  flex: 1; /* 让滑动条占据剩余的空间 */
  margin-right: 10px;
}

.brush-size-value {
  font-size: 14px;
  white-space: nowrap; /* 防止换行 */
}
/*滤镜 */
.filter-buttons-container {
  margin-top: 20px;
}

.filter-button-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.filter-button {
  flex: 1;
  padding: 10px;
  background-color: #3a3a3a;
  color: #ffffff;
  border: 1px solid #2c2c2c;
  cursor: pointer;
  text-align: center;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.filter-button:not(:last-child) {
  margin-right: 10px;
}

.filter-button:hover {
  background-color: #4a4a4a;
}

</style>
