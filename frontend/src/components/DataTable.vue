<template>
  <table class="data-table">
    <thead>
      <tr>
        <th>代码</th>
        <th>名称</th>
        <th>主力净流入</th>
        <th>涨跌幅</th>
        <th>最新价</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in rows" :key="row.code" @click="$emit('row-click', row)">
        <td>{{ row.code }}</td>
        <td>{{ row.name }}</td>
        <td>{{ row.main_flow_net_amount }}</td>
        <td>{{ row.change_percentage }}</td>
        <td>{{ row.latest_price }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
const props = defineProps({
  rows: { type: Array, default: () => [] }
});
</script>

<style scoped>
.data-table { width: 100%; border-collapse: collapse; margin: 24px 0; }
.data-table th, .data-table td { border: 1px solid #eee; padding: 8px 12px; text-align: center; }
.data-table tr:hover { background: #f0f6ff; cursor: pointer; }
</style> 