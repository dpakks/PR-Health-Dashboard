import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getProjectPullRequests, deleteProject } from "../services/projectService";


function ProjectDashboard() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [prs, setPrs] = useState([]);
    const [headers, setHeaders] = useState([]);

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
            <div className="dashboard-header">
                <button className="delete-project-btn" onClick={handleDelete}>
                    🗑 Delete Project
                </button>
            </div>


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
        </div>
    );
}

export default ProjectDashboard;
