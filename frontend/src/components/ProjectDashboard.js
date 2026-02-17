import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getProjectPullRequests, deleteProject, getPRSummary, getProjectUsers, removeUserFromProject, getAllTechLeads, assignUserToProject } from "../services/projectService";



function ProjectDashboard() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [prs, setPrs] = useState([]);
    const [headers, setHeaders] = useState([]);
    const [summary, setSummary] = useState(null);
    const [showOwnersModal, setShowOwnersModal] = useState(false);
    const [owners, setOwners] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [showRemoveConfirm, setShowRemoveConfirm] = useState(false);
    const [showAssignModal, setShowAssignModal] = useState(false);
    const [assignedUsers, setAssignedUsers] = useState([]);
    const [allTechLeads, setAllTechLeads] = useState([]);
    const [assignselectedUser, setAssignSelectedUser] = useState("");
    const role = localStorage.getItem("role");
    const isAdmin = role === "ADMIN";




    useEffect(() => {
        const fetchPRs = async () => {
            const data = await getProjectPullRequests(id);
            setPrs(data);

            if (data.length > 0) {
                const filteredHeaders = Object.keys(data[0]).filter(
                    (key) => key !== "id" && key !== "url"
                );
                setHeaders(filteredHeaders);
            }
        };

        const fetchSummary = async () => {
            try {
                const data = await getPRSummary(id);
                setSummary(data);
            } catch (error) {
                console.error("Failed to fetch summary", error);
            }
        };

        fetchSummary();


        fetchPRs();
    }, [id]);

    const handleDelete = async () => {
        const confirmDelete = window.confirm(
            "Are you sure you want to delete this project?"
        );

        if (!confirmDelete) return;

        try {
            await deleteProject(id);
            alert("Project deleted successfully");
            navigate("/projects");
        } catch (error) {
            console.error("Delete failed", error);
            alert("Failed to delete project");
        }
    };

    const fetchOwners = async () => {
        try {
            const data = await getProjectUsers(id);
            setOwners(data);
        } catch (error) {
            console.error("Failed to fetch project users", error);
        }
    };

    const fetchAssignData = async () => {
        try {
            const assigned = await getProjectUsers(id);
            const allUsers = await getAllTechLeads();

            setAssignedUsers(assigned);
            setAllTechLeads(allUsers);
        } catch (err) {
            console.error("Failed to fetch assignment data", err);
        }
    };

    const unassignedUsers = allTechLeads.filter(
        (user) => !assignedUsers.some((u) => u.id === user.id)
    );

    return (
        <div className="dashboard-container">
            {/* BACK BUTTON */}
            <button
                className="back-btn"
                onClick={() => navigate("/projects")}
            >
                ← Back
            </button>

            <h2 className="dashboard-title">Open Pull Requests</h2>
            {summary && (
                <div className="summary-container">
                    <div className="summary-card purple">
                        <h2>{summary.total_open_prs}</h2>
                        <p>Total Open PRs</p>
                    </div>

                    <div className="summary-card blue">
                        <h2>{summary.stale_prs}</h2>
                        <p>Stale PRs</p>
                    </div>

                    <div className="summary-card orange">
                        <h2>{summary.average_days_open}</h2>
                        <p>Average Days Open</p>
                    </div>

                    <div className="summary-card red">
                        <h2>{summary.oldest_pr_days}</h2>
                        <p>Oldest PR Days</p>
                    </div>
                </div>
            )}

            {isAdmin && (<div className="dashboard-header">
                <button
                    className="assign-btn"
                    onClick={() => {
                        fetchAssignData();
                        setShowAssignModal(true);
                    }}
                >
                    ➕ Assign Tech Lead
                </button>
                <button
                    className="view-owner-btn"
                    onClick={() => {
                        fetchOwners();
                        setShowOwnersModal(true);
                    }}
                >
                    👥 View Project Owners
                </button>
                <button className="delete-project-btn" onClick={handleDelete}>
                    🗑 Delete Project
                </button>
            </div>)}


            <table className="dashboard-table">
                <thead>
                    <tr>
                        {headers.map((header) => (
                            <th key={header}>
                                {header.replace("_", " ").toUpperCase()}
                            </th>
                        ))}
                    </tr>
                </thead>

                <tbody>
                    {prs.map((pr) => (
                        <tr key={pr.id}>
                            {headers.map((header) => (
                                <td key={header}>
                                    {header === "days_open" ? (
                                        <span
                                            className={`days-badge ${pr.days_open >= 7
                                                ? "danger"
                                                : "warning"
                                                }`}
                                        >
                                            {pr.days_open}
                                        </span>
                                    ) : (
                                        pr[header]
                                    )}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>

            {showOwnersModal && (
                <div className="modal-overlay">
                    <div className="modal large">
                        <h3>Project Owners</h3>

                        <table className="dashboard-table">
                            <thead>
                                <tr>
                                    <th>NAME</th>
                                    <th>EMAIL</th>
                                    <th>ROLE</th>
                                    <th>ACTIONS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {owners.map((user) => (
                                    <tr key={user.id}>
                                        <td>{user.name}</td>
                                        <td>{user.email}</td>
                                        <td>{user.role}</td>
                                        <td>
                                            <button
                                                className="danger-btn"
                                                onClick={() => {
                                                    setSelectedUser(user);
                                                    setShowRemoveConfirm(true);
                                                }}
                                            >
                                                Remove
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        <button
                            className="secondary-btn"
                            onClick={() => setShowOwnersModal(false)}
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}

            {showRemoveConfirm && (
                <div className="modal-overlay">
                    <div className="modal">
                        <h4>
                            Are you sure you want to remove{" "}
                            <strong>{selectedUser?.name}</strong>?
                        </h4>

                        <div className="modal-actions">
                            <button
                                className="danger-btn"
                                onClick={async () => {
                                    try {
                                        await removeUserFromProject(id, selectedUser.id);
                                        setShowRemoveConfirm(false);
                                        fetchOwners();
                                    } catch (err) {
                                        console.error("Failed to remove user", err);
                                    }
                                }}
                            >
                                Remove
                            </button>

                            <button
                                className="secondary-btn"
                                onClick={() => setShowRemoveConfirm(false)}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
            {showRemoveConfirm && (
                <div className="modal-overlay">
                    <div className="modal">
                        <h4>
                            Are you sure you want to remove{" "}
                            <strong>{selectedUser?.name}</strong>?
                        </h4>

                        <div className="modal-actions">
                            <button
                                className="danger-btn"
                                onClick={async () => {
                                    try {
                                        await removeUserFromProject(id, selectedUser.id);
                                        setShowRemoveConfirm(false);
                                        fetchOwners();
                                    } catch (err) {
                                        console.error("Failed to remove user", err);
                                    }
                                }}
                            >
                                Remove
                            </button>

                            <button
                                className="secondary-btn"
                                onClick={() => setShowRemoveConfirm(false)}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {showAssignModal && (
                <div className="modal-overlay">
                    <div className="modal large">
                        <h3>Assign Tech Lead</h3>

                        <select
                            value={assignselectedUser}
                            onChange={(e) => setAssignSelectedUser(e.target.value)}
                        >
                            <option value="">Select a user</option>
                            {unassignedUsers.map((user) => (
                                <option key={user.id} value={user.id}>
                                    {user.name} ({user.email})
                                </option>
                            ))}
                        </select>

                        <div className="modal-actions">
                            <button
                                onClick={async () => {
                                    if (!assignselectedUser) {
                                        alert("Please select a user");
                                        return;
                                    }

                                    await assignUserToProject(id, assignselectedUser);
                                    alert("User assigned successfully");
                                    setShowAssignModal(false);
                                    setAssignSelectedUser("");
                                }}
                            >
                                Assign
                            </button>

                            <button
                                className="secondary"
                                onClick={() => setShowAssignModal(false)}
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

export default ProjectDashboard;
