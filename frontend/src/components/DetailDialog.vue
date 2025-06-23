<template>
  <div class="dialog-mask" @click.self="$emit('close')">
    <div class="dialog-box">
      <h2>详情：{{ row.name }} ({{ row.code }})</h2>
      <div class="detail-row"><b>主力净流入：</b>{{ row.main_flow_net_amount }}</div>
      <div class="detail-row"><b>涨跌幅：</b>{{ row.change_percentage }}</div>
      <div class="detail-row"><b>最新价：</b>{{ row.latest_price }}</div>
      <div class="detail-row"><b>周期：</b>{{ row.period }}</div>
      <div class="ai-advice">
        <b>AI投资建议：</b>
        <div class="advice-content">{{ advice }}</div>
      </div>
      <button class="close-btn" @click="$emit('close')">关闭</button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  row: { type: Object, required: true },
  advice: { type: String, default: '' }
});
</script>

<style scoped>
.dialog-mask {
  position: fixed; left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.2); z-index: 1000; display: flex; align-items: center; justify-content: center;
}
.dialog-box {
  background: #fff; border-radius: 8px; padding: 32px; min-width: 340px; max-width: 90vw; box-shadow: 0 2px 16px #aaa;
}
.detail-row { margin-bottom: 8px; }
.ai-advice { margin: 16px 0; background: #f6f8fa; border-radius: 6px; padding: 12px; }
.advice-content { color: #2d3a4b; font-size: 1.1em; }
.close-btn { margin-top: 12px; padding: 6px 18px; border: none; background: #5470c6; color: #fff; border-radius: 4px; cursor: pointer; }
.close-btn:hover { background: #3556a3; }
</style> 