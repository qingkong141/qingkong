<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { authApi } from '@yunpan/shared-api'

const authStore = useAuthStore()
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showOldPw = ref(false)
const showNewPw = ref(false)
const showConfirmPw = ref(false)
const msg = ref('')
const error = ref('')
const loading = ref(false)
const avatarUploading = ref(false)
const avatarMsg = ref('')

async function changePassword() {
  error.value = ''
  msg.value = ''
  if (!oldPassword.value || !newPassword.value || !confirmPassword.value) {
    error.value = '请填写所有字段'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = '两次新密码不一致'
    return
  }
  if (newPassword.value.length < 6) {
    error.value = '新密码至少 6 位'
    return
  }
  loading.value = true
  try {
    await authApi.changePassword({ oldPassword: oldPassword.value, newPassword: newPassword.value })
    msg.value = '密码修改成功'
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (e: any) {
    error.value = e?.message || '修改失败'
  } finally {
    loading.value = false
  }
}

async function uploadAvatar(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) { avatarMsg.value = '只能上传图片'; return }
  if (file.size > 5 * 1024 * 1024) { avatarMsg.value = '图片不能超过 5MB'; return }
  avatarUploading.value = true
  avatarMsg.value = ''
  try {
    await authApi.uploadAvatar(file)
    await authStore.fetchUser()
    avatarMsg.value = '头像更新成功'
  } catch (e: any) {
    avatarMsg.value = e?.message || '上传失败'
  } finally {
    avatarUploading.value = false
    input.value = ''
  }
}

onMounted(() => authStore.fetchUser())

function fmtSize(b: number) {
  if (!b) return '0 B'
  const u = ['B', 'KB', 'MB', 'GB']
  let i = 0, s = b
  while (s >= 1024 && i < u.length - 1) { s /= 1024; i++ }
  return `${s.toFixed(i ? 1 : 0)} ${u[i]}`
}
</script>

<template>
  <div class="profile-page">
    <div class="page-head">
      <h1 class="page-title">个人设置</h1>
    </div>

    <div class="cards">
      <!-- 头像 -->
      <div class="card">
        <h2 class="card-title">头像</h2>
        <div class="avatar-row">
          <div class="avatar-preview">
            <img v-if="authStore.user?.avatar" :src="authStore.user.avatar + '?t=' + authStore.avatarStamp" class="avatar-img" />
            <span v-else class="avatar-letter">{{ authStore.user?.username?.charAt(0).toUpperCase() }}</span>
          </div>
          <label class="upload-btn">
            {{ avatarUploading ? '上传中...' : '更换头像' }}
            <input type="file" accept="image/*" hidden @change="uploadAvatar" />
          </label>
        </div>
        <p v-if="avatarMsg" class="amsg">{{ avatarMsg }}</p>
      </div>

      <!-- 基本信息 -->
      <div class="card">
        <h2 class="card-title">基本信息</h2>
        <div class="info-row">
          <span class="info-label">用户名</span>
          <span class="info-val">{{ authStore.user?.username }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">邮箱</span>
          <span class="info-val">{{ authStore.user?.email }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">存储用量</span>
          <span class="info-val">{{ fmtSize(authStore.user?.storageUsed || 0) }} / {{ fmtSize(authStore.user?.storageQuota || 0) }}</span>
        </div>
      </div>

      <!-- 修改密码 -->
      <div class="card">
        <h2 class="card-title">修改密码</h2>
        <div class="field">
          <label>原密码</label>
          <div class="pw-wrap"><input v-model="oldPassword" :type="showOldPw ? 'text' : 'password'" placeholder="输入原密码" /><button type="button" class="pw-toggle" tabindex="-1" @click="showOldPw = !showOldPw"><svg v-if="showOldPw" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg><svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg></button></div>
        </div>
        <div class="field">
          <label>新密码</label>
          <div class="pw-wrap"><input v-model="newPassword" :type="showNewPw ? 'text' : 'password'" placeholder="至少 6 位" /><button type="button" class="pw-toggle" tabindex="-1" @click="showNewPw = !showNewPw"><svg v-if="showNewPw" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg><svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg></button></div>
        </div>
        <div class="field">
          <label>确认新密码</label>
          <div class="pw-wrap"><input v-model="confirmPassword" :type="showConfirmPw ? 'text' : 'password'" placeholder="再次输入" /><button type="button" class="pw-toggle" tabindex="-1" @click="showConfirmPw = !showConfirmPw"><svg v-if="showConfirmPw" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg><svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg></button></div>
        </div>
        <p v-if="error" class="err">{{ error }}</p>
        <p v-if="msg" class="msg">{{ msg }}</p>
        <button class="btn" :disabled="loading" @click="changePassword">
          {{ loading ? '修改中...' : '修改密码' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page { max-width: 500px; margin: 0 auto; }
.page-head { margin-bottom: 20px; }
.page-title { font-size: 17px; font-weight: 700; color: var(--text-1); margin: 0; }

.cards { display: flex; flex-direction: column; gap: 16px; }
.card { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; }
.card-title { font-size: 14px; font-weight: 600; color: var(--text-1); margin: 0 0 16px; }

.info-row { display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border); }
.info-row:last-child { border-bottom: none; }
.info-label { font-size: 13px; color: var(--text-2); width: 80px; flex-shrink: 0; }
.info-val { font-size: 13px; color: var(--text-1); font-weight: 500; }

.field { margin-bottom: 14px; }
.field label { display: block; font-size: 12px; font-weight: 600; color: var(--text-2); margin-bottom: 4px; }
.field input {
  width: 100%; height: 38px; padding: 0 12px; border: 1.5px solid var(--border); border-radius: 9px;
  font-size: 13px; color: var(--text-1); background: var(--bg-surface); outline: none; box-sizing: border-box;
  transition: border-color .15s;
}
.field input:focus { border-color: var(--accent); }

.err { font-size: 12px; color: #ef4444; margin: 0 0 12px; }
.msg { font-size: 12px; color: #16a34a; margin: 0 0 12px; }

.btn {
  width: 100%; height: 40px; border: none; border-radius: 10px;
  background: var(--accent); color: #fff; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn:hover { opacity: .9; }
.btn:disabled { opacity: .5; cursor: not-allowed; }

.pw-wrap { position: relative; width: 100% }
.pw-wrap input { width: 100%; padding-right: 36px !important }
.pw-toggle { position: absolute; right: 1px; top: 1px; bottom: 1px; width: 34px; background: none; border: none; color: #a1a1aa; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: color .15s }
.pw-toggle:hover { color: #71717a }

/* 头像 */
.avatar-row { display: flex; align-items: center; gap: 16px; }
.avatar-preview { width: 64px; height: 64px; border-radius: 14px; overflow: hidden; background: var(--bg-page); display: flex; align-items: center; justify-content: center; flex-shrink: 0 }
.avatar-img { width: 100%; height: 100%; object-fit: cover }
.avatar-letter { font-size: 24px; font-weight: 700; color: var(--accent) }
.upload-btn { height: 34px; padding: 0 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 12px; cursor: pointer; display: inline-flex; align-items: center; color: var(--text-2); transition: all .12s }
.upload-btn:hover { border-color: var(--accent); color: var(--accent) }
.amsg { font-size: 12px; color: var(--text-3); margin: 10px 0 0 }
</style>
