import { useEffect, useState } from "react";
import { getUsers, createUser, deleteUser } from "../services/userService";

function Users() {
  const [users, setUsers] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "TECH_LEAD",
  });

  const role = localStorage.getItem("role");

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const data = await getUsers();
      setUsers(data);

      if (data.length > 0) {
        const filteredHeaders = Object.keys(data[0]).filter(
          (key) => key !== "id"
        );
        setHeaders(filteredHeaders);
      }
    } catch (error) {
      console.error("Failed to fetch users", error);
    }
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleString();
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    try {
      await createUser(formData);
      setShowModal(false);
      setFormData({
        name: "",
        email: "",
        password: "",
        role: "TECH_LEAD",
      });
      fetchUsers();
    } catch (error) {
      console.error("Failed to create user", error);
    }
  };

  const handleDeleteClick = (user) => {
    setSelectedUser(user);
    setDeleteModal(true);
  };

  const confirmDelete = async () => {
    await deleteUser(selectedUser.id);
    setDeleteModal(false);
    setSelectedUser(null);
    fetchUsers(); // refresh table
  };

  const handleClear = () => {
    setFormData({
      name: "",
      email: "",
      password: "",
      role: "TECH_LEAD",
    });
  };

  return (
    <div className="users-container">
      <div className="users-header">
        <h2 className="users-title">Users</h2>

        {role === "ADMIN" && (
          <button
            className="add-user-btn"
            onClick={() => setShowModal(true)}
          >
            + Add New User
          </button>
        )}
      </div>

      <div className="users-table-wrapper">
        <table className="users-table">
          <thead>
            <tr>
              {headers.map((header) => (
                <th key={header}>
                  {header.replace("_", " ").toUpperCase()}
                </th>
              ))}
              <th>ACTIONS</th>
            </tr>

          </thead>

          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                {headers.map((header) => (
                  <td key={header}>
                    {header === "created_at"
                      ? formatDate(user[header])
                      : user[header]}
                  </td>

                ))}
                <td>
                  {role === "ADMIN" && (
                    <span
                      className="delete-icon"
                      onClick={() => handleDeleteClick(user)}
                    >
                      🗑
                    </span>
                  )}
                </td>

              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {users.length === 0 && (
        <p className="no-users">No users found</p>
      )}

      {deleteModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Delete User</h3>
            <p>
              Are you sure you want to delete{" "}
              <strong>{selectedUser?.name}</strong>?
            </p>

            <div className="modal-buttons">
              <button className="submit-btn" onClick={confirmDelete}>
                Ok
              </button>

              <button
                className="close-btn"
                onClick={() => setDeleteModal(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Add New User</h3>

            <input
              type="text"
              name="name"
              placeholder="Name"
              value={formData.name}
              onChange={handleChange}
            />

            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
            />

            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
            />

            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
            >
              <option value="ADMIN">ADMIN</option>
              <option value="TECH_LEAD">TECH_LEAD</option>
            </select>

            <div className="modal-buttons">
              <button onClick={handleSubmit} className="submit-btn">
                Submit
              </button>

              <button onClick={handleClear} className="clear-btn">
                Clear
              </button>

              <button
                onClick={() => setShowModal(false)}
                className="close-btn"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Users;
