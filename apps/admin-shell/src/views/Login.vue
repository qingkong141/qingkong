<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!email.value || !password.value) {
    error.value = '请填写邮箱和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await authStore.login({ email: email.value, password: password.value })
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
        <div class="brand-icon">Q</div>
        <h1>青空管理台</h1>
        <p class="brand-sub">欢迎回来，请登录你的账户</p>
      </div>

      <div class="form">
        <div class="field">
          <label>邮箱</label>
          <input
            v-model="email"
            type="email"
            placeholder="your@email.com"
            :class="{ 'has-error': error }"
          />
        </div>
        <div class="field">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            :class="{ 'has-error': error }"
            @keyup.enter="handleLogin"
          />
        </div>

        <p v-if="error" class="error-msg">
          <span class="error-icon">!</span>
          {{ error }}
        </p>

        <button class="btn-login" :disabled="loading" @click="handleLogin">
          <span v-if="loading" class="spinner" />
          <span>{{ loading ? '登录中...' : '登录' }}</span>
        </button>
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
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16px;
}

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

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
