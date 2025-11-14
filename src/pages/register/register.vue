<template>
  <div class="container" style="margin-top: -200px;">
    <div class="row">
      <div class="col-md-4 offset-md-4">
        <div class="logo1">
          <!-- <img src="your-log1111111o111.png" alt="Logo" class="logo"> -->
          <h1 class="text-center">FinScope</h1>
          <p class="text-center">Your Customized Financial AI Search</p>
        </div>
        <form @submit.prevent="submitForm" class="register-form">
          <div class="form-group">
            <label for="username">Username</label>
            <input type="text" class="form-control" id="username" v-model="username" placeholder="Enter username">
          </div>
          <div class="form-group">
            <label for="email">Email address</label>
            <input type="email" class="form-control" id="email" v-model="email" placeholder="name@example.com">
            <div v-if="emailError" class="error-message">{{ emailError }}</div>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input type="password" class="form-control" id="password" v-model="password" placeholder="Password">
          </div>
          <div class="form-group">
            <label for="confirm-password">Confirm Password</label>
            <input type="password" class="form-control" id="confirm-password" v-model="confirmPassword"
              placeholder="Confirm Password">
            <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
          </div>
          <button type="submit" class="btn btn-primary" @click="submitFormcom()">Register</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { registerUser } from '@/service/api/register/register'; // Import the registerUser function
import router from '@/router'; // 直接导入 router 实例

export default {
  data () {
    return {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      submitting: false
    };
  },
  computed: {
    emailError () {
      if (!this.email) {
        return 'Email is required';
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.email)) {
        return 'Invalid email format';
      }
      return '';
    },
    passwordError () {
      if (this.password !== this.confirmPassword) {
        return 'Passwords do not match';
      }
      if (this.password.length < 8) {
        return 'Password must be at least 8 characters long';
      }
      return '';
    }
  },
  methods: {
    submitFormcom () {
      if (!this.username) {
        alert('Please fill in your username.');
        return false;
      }
      if (!this.email) {
        alert('Please fill in your email.');
        return false;
      }
      if (!this.password) {
        alert('Please fill in your password.');
        return false;
      }
      if (!this.confirmPassword) {
        alert('Please confirm your password.');
        return false;
      }
      registerUser({
        username: this.username,
        email: this.email,
        password: this.password,
      })
        .then((response) => {
          if (response.data.code != 200) {
            alert(response.data.message);
          } else {
            alert(response.data.message);
            router.push('/');
          }
        })
        .catch((error) => {
          console.error('Failed to register user:', error);
        });

    }
  }
};
</script>

<style scoped>
.logo1 {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.container {
  margin-top: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.logo {
  width: 100px;
  height: 100px;
  object-fit: cover;
}

.register-form {
  width: 300px;
  margin-top: 20px;
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-content: space-between;
  flex-wrap: nowrap;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;
}

.form-group {
  width: 200px;
  margin-bottom: 20px;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.error-message {
  color: red;
  font-size: 12px;
}
</style>