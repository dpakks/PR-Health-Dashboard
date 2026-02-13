import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

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
