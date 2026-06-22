<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const account = ref('')
const password = ref('')
const showPw = ref(false)
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!account.value || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await authStore.login({ account: account.value, password: password.value })
    router.push('/admin')
  }
  catch (e: any) {
    error.value = e.message ?? '登录失败'
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="brand">
        <div class="brand-icon"><img src="/logo/logo.svg" alt="臻橙云盘" class="brand-logo-img" /></div>
        <h1>臻橙云盘</h1>
        <p class="brand-sub">欢迎回来，请登录你的账户</p>
      </div>

      <div class="form">
        <div class="field">
          <label>用户名 / 邮箱</label>
          <input
            v-model="account"
            type="text"
            placeholder="用户名或邮箱"
            :class="{ 'has-error': error }"
          />
        </div>
        <div class="field">
          <label>密码</label>
<div class="pw-wrap">
            <input
              v-model="password"
              :type="showPw ? 'text' : 'password'"
              placeholder="••••••••"
              :class="{ 'has-error': error }"
              @keyup.enter="handleLogin"
            />
            <button type="button" class="pw-toggle" tabindex="-1" @click="showPw = !showPw">
              <svg v-if="showPw" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
        </div>

        <p v-if="error" class="error-msg">
          <span class="error-icon">!</span>
          {{ error }}
        </p>

        <button class="btn-login" :disabled="loading" @click="handleLogin">
          <span v-if="loading" class="spinner" />
          <span>{{ loading ? '登录中...' : '登录' }}</span>
        </button>

        <p class="switch-link">还没有账户？<router-link to="/register">注册新账户</router-link></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -20%, var(--login-glow-1), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, var(--login-glow-2), transparent);
  transition: background 0.3s;
}

.login-card {
  width: 400px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 40px;
  box-shadow: var(--shadow);
  transition: background 0.3s, border-color 0.3s;
}

.brand {
  text-align: center;
  margin-bottom: 32px;
}

.brand-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--accent), var(--accent-end));
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  padding: 8px;
  box-sizing: border-box;
}
.brand-logo-img { width: 100%; height: 100%; object-fit: contain; filter: brightness(0) invert(1); }

.brand h1 {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-1);
}

.brand-sub {
  margin: 0;
  font-size: 14px;
  color: var(--text-3);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-2);
}

input {
  padding: 10px 14px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-1);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input::placeholder { color: var(--text-3); }

input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-muted);
}

input.has-error { border-color: #ef4444; }

.error-msg {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  font-size: 13px;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
}

.error-icon {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #ef4444;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-login {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px;
  margin-top: 4px;
  background: linear-gradient(135deg, var(--accent), var(--accent-end));
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
}

.btn-login:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.btn-login:active:not(:disabled) { transform: translateY(0); }
.btn-login:disabled { opacity: 0.5; cursor: not-allowed; }

.switch-link { text-align:center;margin-top:16px;font-size:13px;color:var(--text-3,#9ca3af) }
.switch-link a { color:var(--accent,#6366f1);text-decoration:none;font-weight:500 }
.switch-link a:hover { text-decoration:underline }

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.pw-wrap { position: relative; width: 100% }
.pw-wrap input { width: 100%; padding-right: 36px !important }
.pw-toggle { position: absolute; right: 1px; top: 1px; bottom: 1px; width: 34px; background: none; border: none; color: #a1a1aa; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: color .15s }
.pw-toggle:hover { color: #71717a }
</style>
