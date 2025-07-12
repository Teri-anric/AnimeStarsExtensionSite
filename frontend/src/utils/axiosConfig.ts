import axios from 'axios';

// Налаштовуємо axios interceptor для обробки 401 помилок
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен закінчився - очищаємо localStorage і перенаправляємо на login
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axios;