// include the JWT token in API requests
import axios from 'axios';
import Auth from '@aws-amplify/auth';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Kong API Gateway endpoint
});

// Add a request interceptor to include the JWT token
api.interceptors.request.use(
  (config) => {
    try {
      // Get the current authenticated session from Amplify
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();
      
      // Add token to headers
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
      // Log the token for debugging purposes (optional)
      console.log('Adding auth token:', token.substring(0, 20) + '...');
    } catch (error) {
      // User is not authenticated, proceed without token
      console.log('User not authenticated', error);
       // Redirect to login if needed
      // window.location.href = '/login';
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;