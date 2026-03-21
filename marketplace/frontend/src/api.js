import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const login = (email, password) =>
  api.post('/auth/login', { email, password });

export const register = (data) =>
  api.post('/auth/register', data);

export const getMe = () => api.get('/auth/me');

// Marketplace Profiles
export const createProfile = (data) =>
  api.post('/marketplace/profiles', data);

export const getMyProfile = () =>
  api.get('/marketplace/profiles/me');

export const getProfile = (profileId) =>
  api.get(`/marketplace/profiles/${profileId}`);

export const updateProfile = (data) =>
  api.patch('/marketplace/profiles/me', data);

export const updateTypeData = (data) =>
  api.patch('/marketplace/profiles/me/type-data', data);

export const deleteProfile = () =>
  api.delete('/marketplace/profiles/me');

// Onboarding
export const startOnboarding = (profileType) =>
  api.post('/marketplace/onboarding/start', { profile_type: profileType });

export const saveOnboardingStep = (stepNumber, data) =>
  api.patch(`/marketplace/onboarding/step/${stepNumber}`, { data });

export const getOnboardingStatus = () =>
  api.get('/marketplace/onboarding/status');

// Documents
export const getUploadUrl = (data) =>
  api.post('/marketplace/profiles/me/documents/upload-url', data);

export const confirmUpload = (data) =>
  api.post('/marketplace/profiles/me/documents/confirm-upload', data);

export const listDocuments = () =>
  api.get('/marketplace/profiles/me/documents');

export const deleteDocument = (docId) =>
  api.delete(`/marketplace/profiles/me/documents/${docId}`);

// Visibility
export const getVisibility = () =>
  api.get('/marketplace/profiles/me/visibility');

export const updateVisibility = (data) =>
  api.patch('/marketplace/profiles/me/visibility', data);

// Discovery
export const discoverProfiles = (params = {}) =>
  api.get('/marketplace/discover', { params });

export default api;
