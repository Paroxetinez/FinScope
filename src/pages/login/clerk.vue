<script setup>
import { SignIn, SignUp, SignedIn, SignedOut, useUser, useClerk } from 'vue-clerk'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { user } = useUser()
const { clerk } = useClerk()
const loading = ref(true)

onMounted(() => {
  loading.value = false
  console.log('Current user:', user.value)
})

const handleSignOut = async () => {
  try {
    await clerk.signOut()
    router.push('/login')
  } catch (err) {
    console.error('Error signing out:', err)
  }
}
</script>

<template>
  <div class="clerk-container">
    <div v-if="loading" class="loading">
      Loading...
    </div>
    
    <SignedOut>
      <div class="auth-container">
        <h1>欢迎使用 FinScope</h1>
        <div class="tabs">
          <SignIn routing="path" path="/sign-in" />
          <SignUp routing="path" path="/sign-up" />
        </div>
      </div>
    </SignedOut>

    <SignedIn>
      <div class="user-container">
        <h2>欢迎回来, {{ user?.firstName || '用户' }}</h2>
        <div class="user-info">
          <img 
            v-if="user?.imageUrl" 
            :src="user.imageUrl" 
            alt="用户头像"
            class="avatar"
          >
          <p>{{ user?.emailAddresses[0] }}</p>
        </div>
        <n-button @click="handleSignOut" type="error">
          退出登录
        </n-button>
      </div>
    </SignedIn>
  </div>
</template>

<style scoped>
.clerk-container {
  width: 100%;
  max-width: 500px;
  margin: 2rem auto;
  padding: 1rem;
}

.auth-container {
  text-align: center;
}

.loading {
  text-align: center;
  padding: 2rem;
}

.user-container {
  text-align: center;
  padding: 1rem;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  margin: 1rem 0;
}

.user-info {
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

h1 {
  margin-bottom: 2rem;
  color: #333;
}

h2 {
  color: #666;
}
</style>