import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  Patient,
  PatientCreate,
  PatientUpdate,
  Document,
  DocumentCreate,
  DocumentUpdate,
  ChatRequest,
  ChatResponse,
  SearchRequest,
  SearchResponse,
} from './types';

// Server-side API configuration
const BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost';
const AUTH_PORT = process.env.VITE_AUTH_SERVICE_PORT || '8001';
const PATIENT_PORT = process.env.VITE_PATIENT_SERVICE_PORT || '8002';
const RAG_PORT = process.env.VITE_RAG_SERVICE_PORT || '8003';

const AUTH_API_URL = `${BASE_URL}:${AUTH_PORT}/api/v1`;
const PATIENT_API_URL = `${BASE_URL}:${PATIENT_PORT}/api/v1`;
const RAG_API_URL = `${BASE_URL}:${RAG_PORT}/api/v1`;

// Server-side fetch wrapper with error handling
async function fetchApi<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw {
      response: {
        status: response.status,
        statusText: response.statusText,
        data: error,
      },
    };
  }

  return response.json();
}

// Server-side API client
export const serverApi = {
  // Authentication Methods
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return fetchApi<AuthResponse>(`${AUTH_API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });
  },

  async register(userData: RegisterRequest): Promise<User> {
    return fetchApi<User>(`${AUTH_API_URL}/auth/register`, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  async getCurrentUser(token: string): Promise<User> {
    return fetchApi<User>(`${AUTH_API_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  async getUsers(token: string): Promise<User[]> {
    return fetchApi<User[]>(`${AUTH_API_URL}/users/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // Patient Methods
  async getPatients(token: string): Promise<Patient[]> {
    return fetchApi<Patient[]>(`${PATIENT_API_URL}/patients/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  async getPatient(id: number, token: string): Promise<Patient> {
    return fetchApi<Patient>(`${PATIENT_API_URL}/patients/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  async createPatient(patientData: PatientCreate, token: string): Promise<Patient> {
    return fetchApi<Patient>(`${PATIENT_API_URL}/patients/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(patientData),
    });
  },

  async updatePatient(
    id: number,
    patientData: PatientUpdate,
    token: string
  ): Promise<Patient> {
    return fetchApi<Patient>(`${PATIENT_API_URL}/patients/${id}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(patientData),
    });
  },

  async deletePatient(id: number, token: string): Promise<void> {
    await fetch(`${PATIENT_API_URL}/patients/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // Document Methods
  async getDocuments(token: string): Promise<Document[]> {
    return fetchApi<Document[]>(`${RAG_API_URL}/documents/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  async getDocument(id: number, token: string): Promise<Document> {
    return fetchApi<Document>(`${RAG_API_URL}/documents/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  async createDocument(
    documentData: DocumentCreate,
    token: string
  ): Promise<Document> {
    return fetchApi<Document>(`${RAG_API_URL}/documents/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(documentData),
    });
  },

  async updateDocument(
    id: number,
    documentData: DocumentUpdate,
    token: string
  ): Promise<Document> {
    return fetchApi<Document>(`${RAG_API_URL}/documents/${id}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(documentData),
    });
  },

  async deleteDocument(id: number, token: string): Promise<void> {
    await fetch(`${RAG_API_URL}/documents/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // Chat/RAG Methods
  async askQuestion(request: ChatRequest, token: string): Promise<ChatResponse> {
    return fetchApi<ChatResponse>(`${RAG_API_URL}/chat/ask`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(request),
    });
  },

  async searchDocuments(
    request: SearchRequest,
    token: string
  ): Promise<SearchResponse> {
    return fetchApi<SearchResponse>(`${RAG_API_URL}/search/documents`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(request),
    });
  },
};