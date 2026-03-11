import { useEffect, useState } from "react";
import {
  getUsers,
  createUser,
  deleteUser,
  getUserSummary,
} from "../services/userService";
import { AddIcon, DeleteIcon } from "../icons/Icons";

function Users() {
  const [users, setUsers] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [summary, setSummary] = useState(null);
  const [errors, setErrors] = useState({});

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "TECH_LEAD",
  });

  const role = localStorage.getItem("role");

  useEffect(() => {
    fetchUsers();
    fetchSummary();
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

  const fetchSummary = async () => {
    try {
      const data = await getUserSummary();
      setSummary(data);
    } catch (error) {
      console.error("Failed to fetch user summary", error);
    }
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleString();
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    setErrors((prev) => ({
      ...prev,
      [name]: "",
    }));
  };

  const handleSubmit = async () => {
    const newErrors = {};

    if (!formData.name.trim()) newErrors.name = "This field is required";
    if (!formData.email.trim()) newErrors.email = "This field is required";
    if (!formData.password.trim()) newErrors.password = "This field is required";
    if (!formData.role) newErrors.role = "This field is required";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      await createUser(formData);
      setShowModal(false);
      setErrors({});
      setFormData({
        name: "",
        email: "",
        password: "",
        role: "TECH_LEAD",
      });
      fetchUsers();
      fetchSummary();
    } catch (error) {
      console.error("Failed to create user", error);
    }
  };

  const handleDeleteClick = (user) => {
    setSelectedUser(user);
    setDeleteModal(true);
  };

  const confirmDelete = async () => {
    try {
      await deleteUser(selectedUser.id);
      setDeleteModal(false);
      setSelectedUser(null);
      fetchUsers();
      fetchSummary();
    } catch (error) {
      console.error("Failed to delete user", error);
    }
  };

  const handleClear = () => {
    setFormData({
      name: "",
      email: "",
      password: "",
      role: "TECH_LEAD",
    });
    setErrors({});
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setErrors({});
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
          <button className="add-user-btn" onClick={() => setShowModal(true)}>
            <AddIcon />
            Add New User
          </button>
        )}
      </div>

      {summary && (
        <div className="user-summary-container">
          <div className="user-summary-card total-users-card">
            <h2>{summary.total_users}</h2>
            <p>Total Users</p>
          </div>

          <div className="user-summary-card tech-leads-card">
            <h2>{summary.total_tech_leads}</h2>
            <p>Total Tech Leads</p>
          </div>

          <div className="user-summary-card admins-card">
            <h2>{summary.total_admins}</h2>
            <p>Total Admins</p>
          </div>
        </div>
      )}

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
                      <DeleteIcon />
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {users.length === 0 && <p className="no-users">No users found</p>}

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
              className={errors.name ? "input-error" : ""}
            />
            {errors.name && <div className="field-error">{errors.name}</div>}

            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              className={errors.email ? "input-error" : ""}
            />
            {errors.email && <div className="field-error">{errors.email}</div>}

            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              className={errors.password ? "input-error" : ""}
            />
            {errors.password && (
              <div className="field-error">{errors.password}</div>
            )}

            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className={errors.role ? "input-error" : ""}
            >
              <option value="">Select Role</option>
              <option value="ADMIN">ADMIN</option>
              <option value="TECH_LEAD">TECH_LEAD</option>
            </select>
            {errors.role && <div className="field-error">{errors.role}</div>}

            <div className="modal-buttons">
              <button onClick={handleSubmit} className="submit-btn">
                Submit
              </button>

              <button onClick={handleClear} className="clear-btn">
                Clear
              </button>

              <button onClick={handleCloseModal} className="close-btn">
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