import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const getAllTechLeads = async () => {
  const token = localStorage.getItem("token");

  const response = await axios.get(`${API_URL}/users/getAllTechLeads`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const getProjects = async () => {
  const token = localStorage.getItem("token");

  const response = await axios.get(`${API_URL}/projects/getAll`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};
export const createProject = async (project) => {
  const token = localStorage.getItem("token");

  const response = await axios.post(
    `${API_URL}/projects/create`,
    project,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};

export const getProjectPullRequests = async (projectId) => {
  const token = localStorage.getItem("token");

  const response = await axios.get(
    `${API_URL}/projects/${projectId}/pull-requests`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};

export const deleteProject = async (projectId) => {
  const token = localStorage.getItem("token");

  await axios.delete(`${API_URL}/projects/${projectId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

export const getPRSummary = async (projectId) => {
  const token = localStorage.getItem("token");

  const response = await axios.get(
    `${API_URL}/projects/${projectId}/pull-requests/summary`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};

export const getProjectUsers = async (projectId) => {
  const token = localStorage.getItem("token");

  const response = await axios.get(
    `${API_URL}/projects/${projectId}/users`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};

// Remove user from project
export const removeUserFromProject = async (projectId, userId) => {
  const token = localStorage.getItem("token");

  await axios.delete(
    `${API_URL}/projects/${projectId}/users/${userId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
};

export const assignUserToProject = async (projectId, userId) => {
  const token = localStorage.getItem("token");

  await axios.post(
    `${API_URL}/projects/${projectId}/assign/${userId}`,
    {},
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
};
