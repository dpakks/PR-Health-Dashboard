import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const getUsers = async () => {
  const token = localStorage.getItem("token");

  const response = await axios.get(`${API_URL}/users/getAllTechLeads`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const createUser = async (userData) => {
  const token = localStorage.getItem("token");

  const response = await axios.post(
    `${API_URL}/users/createUser`,
    userData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};

export const deleteUser = async (id) => {
  const token = localStorage.getItem("token");

  const response = await axios.delete(
    `${API_URL}/users/${id}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};
