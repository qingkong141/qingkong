<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@yunpan/shared-api'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPw = ref(false)
const showConfirmPw = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleRegister() {
  error.value = ''
  if (!username.value || !email.value || !password.value) {
    error.value = '请填写所有字段'
    return
  }
  if (password.value !== confirmPassword.value) {
    error.value = '两次密码不一致'
    return
  }
  if (password.value.length < 6) {
    error.value = '密码至少 6 位'
    return
  }
  loading.value = true
  try {
    await authApi.register({ username: username.value, email: email.value, password: password.value })
    success.value = true
  } catch (e: any) {
    error.value = e?.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-wrap">
      <div class="login-card">
        <div class="brand">
          <div class="brand-icon"><img src="/logo/logo.svg" alt="臻橙云盘" class="brand-logo-img" /></div>
          <h1>臻橙云盘</h1>
          <p v-if="!success" class="brand-sub">注册新账户，等待管理员审核</p>
        </div>

        <!-- 注册成功 -->
        <div v-if="success" class="success-box">
          <div class="success-icon">✅</div>
          <h2>注册成功</h2>
          <p>你的账户已提交，请等待管理员审核通过后即可登录。</p>
          <button class="btn" @click="router.push('/login')">返回登录</button>
        </div>

        <!-- 注册表单 -->
        <div v-else class="form">
          <div class="field">
            <label>用户名</label>
            <input v-model="username" type="text" placeholder="请输入用户名" autocomplete="off" :class="{ 'has-error': error }" />
          </div>
          <div class="field">
            <label>邮箱</label>
            <input v-model="email" type="email" placeholder="your@email.com" autocomplete="off" :class="{ 'has-error': error }" />
          </div>
          <div class="field">
            <label>密码</label>
            <div class="pw-wrap"><input v-model="password" :type="showPw ? 'text' : 'password'" placeholder="至少 6 位密码" autocomplete="new-password" :class="{ 'has-error': error }" /><button type="button" class="pw-toggle" tabindex="-1" @click="showPw = !showPw"><svg v-if="showPw" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg><svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg></button></div>
          </div>
          <div class="field">
            <label>确认密码</label>
            <div class="pw-wrap"><input v-model="confirmPassword" :type="showConfirmPw ? 'text' : 'password'" placeholder="再次输入密码" autocomplete="new-password" :class="{ 'has-error': error }" @keyup.enter="handleRegister" /><button type="button" class="pw-toggle" tabindex="-1" @click="showConfirmPw = !showConfirmPw"><svg v-if="showConfirmPw" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg><svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg></button></div>
          </div>

          <p v-if="error" class="err">{{ error }}</p>

          <button class="btn btn-primary" :disabled="loading" @click="handleRegister">
            {{ loading ? '注册中...' : '注册' }}
          </button>

          <p class="switch">已有账户？<router-link to="/login">去登录</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page, #f9fafb);
  padding: 20px;
}

.login-wrap { width: 100%; max-width: 400px; }

.login-card {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 8px 32px rgba(0,0,0,.06);
}

.brand { text-align: center; margin-bottom: 28px; }
.brand h1 { margin: 0 0 6px; font-size: 20px; font-weight: 600; color: var(--text-1); }
.brand-sub { font-size: 13px; color: var(--text-3, #9ca3af); margin: 0; }

.brand-icon {
  width: 48px; height: 48px;
  background: linear-gradient(135deg, var(--accent), var(--accent-end));
  border-radius: 12px; display: inline-flex; align-items: center; justify-content: center;
  margin-bottom: 16px; padding: 8px; box-sizing: border-box;
}
.brand-logo-img { width: 100%; height: 100%; object-fit: contain; filter: brightness(0) invert(1); }

.form { display: flex; flex-direction: column; gap: 16px; }

.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: 12px; font-weight: 600; color: var(--text-2, #6b7280); }
.field input {
  height: 42px; padding: 0 14px;
  border: 1.5px solid var(--border, #e5e7eb); border-radius: 10px;
  font-size: 14px; color: var(--text-1); outline: none; background: var(--bg-surface, #fff);
  transition: border-color .15s;
}
.field input:focus { border-color: var(--accent, #6366f1); }
.field input.has-error { border-color: #ef4444; }

.err { font-size: 12px; color: #ef4444; margin: 0; }

.btn {
  width: 100%; height: 44px; border: none; border-radius: 12px;
  font-size: 14px; font-weight: 600; cursor: pointer; transition: opacity .15s;
}
.btn-primary { background: #18181b; color: #fff; }
.btn-primary:hover { opacity: .9; }
.btn-primary:disabled { opacity: .5; cursor: not-allowed; }

.switch { text-align: center; font-size: 13px; color: var(--text-3, #9ca3af); margin: 0; }
.switch a { color: var(--accent, #6366f1); text-decoration: none; font-weight: 500; }
.switch a:hover { text-decoration: underline; }

.success-box { text-align: center; padding: 20px 0; }
.success-icon { font-size: 48px; margin-bottom: 16px; }
.success-box h2 { font-size: 18px; font-weight: 600; color: var(--text-1); margin: 0 0 8px; }
.success-box p { font-size: 13px; color: var(--text-3, #9ca3af); margin: 0 0 24px; line-height: 1.6; }

.pw-wrap { position: relative; width: 100% }
.pw-wrap input { width: 100%; padding-right: 36px !important }
.pw-wrap { position: relative; width: 100% }
.pw-wrap input { width: 100%; padding-right: 36px !important }
.pw-toggle { position: absolute; right: 1px; top: 1px; bottom: 1px; width: 34px; background: none; border: none; color: #a1a1aa; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: color .15s }
.pw-toggle:hover { color: #71717a }
</style>
