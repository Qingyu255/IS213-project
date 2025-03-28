// include the JWT token in API requests
import axios from 'axios';
import { Auth } from 'aws-amplify';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Kong API Gateway endpoint
});

// Add a request interceptor to include the JWT token
api.interceptors.request.use(
  async (config) => {
    try {
      // Get the current authenticated session from Amplify
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();
      
      // Add token to headers
      config.headers.Authorization = `Bearer ${token}`;
    } catch (error) {
      // User is not authenticated, proceed without token
      console.log('User not authenticated', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;