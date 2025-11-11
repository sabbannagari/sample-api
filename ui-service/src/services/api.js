import axios from 'axios';

// API Base URLs
const LOGIN_API = 'http://localhost:8001';
const PRODUCT_API = 'http://localhost:8002';
const ORDER_API = 'http://localhost:8003';

// Get token from localStorage
const getToken = () => localStorage.getItem('token');

// Set token in localStorage
const setToken = (token) => localStorage.setItem('token', token);

// Remove token from localStorage
const removeToken = () => localStorage.removeItem('token');

// Create axios instances for each service
const loginAxios = axios.create({
  baseURL: LOGIN_API,
});

const productAxios = axios.create({
  baseURL: PRODUCT_API,
});

const orderAxios = axios.create({
  baseURL: ORDER_API,
});

// Add authorization header to product and order requests
[productAxios, orderAxios].forEach(instance => {
  instance.interceptors.request.use(
    (config) => {
      const token = getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );
});

// ==================== AUTH API ====================
export const authAPI = {
  login: async (username, password) => {
    const response = await loginAxios.post('/login/credentials', {
      username,
      password,
    });
    if (response.data.access_token) {
      setToken(response.data.access_token);
    }
    return response.data;
  },

  logout: async () => {
    const token = getToken();
    if (token) {
      try {
        await loginAxios.post('/logout', {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    removeToken();
  },

  getCurrentUser: async () => {
    const token = getToken();
    if (!token) return null;
    const response = await loginAxios.get('/me', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },
};

// ==================== PRODUCT API ====================
export const productAPI = {
  getAll: async (filters = {}) => {
    const response = await productAxios.get('/products', { params: filters });
    return response.data;
  },

  getById: async (id) => {
    const response = await productAxios.get(`/products/${id}`);
    return response.data;
  },

  create: async (product) => {
    const response = await productAxios.post('/products', product);
    return response.data;
  },

  update: async (id, product) => {
    const response = await productAxios.put(`/products/${id}`, product);
    return response.data;
  },

  delete: async (id) => {
    await productAxios.delete(`/products/${id}`);
  },

  updateStock: async (id, quantity) => {
    const response = await productAxios.patch(`/products/${id}/stock`, null, {
      params: { quantity }
    });
    return response.data;
  },

  getCategories: async () => {
    const response = await productAxios.get('/categories');
    return response.data;
  },
};

// ==================== ORDER API ====================
export const orderAPI = {
  getAll: async (filters = {}) => {
    const response = await orderAxios.get('/orders', { params: filters });
    return response.data;
  },

  getById: async (id) => {
    const response = await orderAxios.get(`/orders/${id}`);
    return response.data;
  },

  create: async (order) => {
    const response = await orderAxios.post('/orders', order);
    return response.data;
  },

  update: async (id, order) => {
    const response = await orderAxios.put(`/orders/${id}`, order);
    return response.data;
  },

  cancel: async (id) => {
    const response = await orderAxios.post(`/orders/${id}/cancel`);
    return response.data;
  },

  delete: async (id) => {
    await orderAxios.delete(`/orders/${id}`);
  },

  getUserSummary: async (userId) => {
    const response = await orderAxios.get(`/users/${userId}/orders/summary`);
    return response.data;
  },
};

export { getToken, setToken, removeToken };
