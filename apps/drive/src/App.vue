<script setup lang="ts">
import AppToast from './components/AppToast.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
</script>

<template>
  <router-view />
  <AppToast />
  <ConfirmDialog />
</template>
