import { useEffect, useState } from "react";
import { getProjects, createProject } from "../services/projectService";

const COLORS = ["#60a5fa", "#fb7185", "#fbbf24", "#a855f7", "#34d399"];

function Projects() {
  const [projects, setProjects] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const role = localStorage.getItem("role");

  // Fetch projects
  const fetchProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
    } catch (error) {
      console.error("Failed to fetch projects", error);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // Get initials
  const getInitials = (name) =>
    name
      .split(" ")
      .map((w) => w[0])
      .join("")
      .toUpperCase();

  // Submit project
  const handleSubmit = async () => {
    if (!name || !repoUrl) {
      alert("All fields are required");
      return;
    }

    try {
      await createProject({
        name,
        repo_url: repoUrl,
      });

      setShowModal(false);
      setName("");
      setRepoUrl("");
      fetchProjects(); // refresh
    } catch (error) {
      console.error("Project creation failed", error);
      alert("Failed to create project");
    }
  };

  // Clear form
  const handleClear = () => {
    setName("");
    setRepoUrl("");
  };

  return (
    <div className="projects-container">
      <h2 className="projects-title">Projects</h2>

      <div className="projects-grid">
        {projects.map((project, index) => (
          <div key={project.id} className="project-card">
            <div
              className="project-icon"
              style={{ background: COLORS[index % COLORS.length] }}
            >
              {getInitials(project.name)}
            </div>
            <p className="project-name">{project.name}</p>
          </div>
        ))}

        {/* ADMIN ONLY → ADD PROJECT */}
        {role === "ADMIN" && (
          <div
            className="project-card add-project"
            onClick={() => setShowModal(true)}
          >
            <div className="project-icon add-icon">+</div>
            <p className="project-name">Add a project</p>
          </div>
        )}
      </div>

      {/* TECH LEAD WITH NO PROJECTS */}
      {role !== "ADMIN" && projects.length === 0 && (
        <p className="no-projects">
          No projects assigned for you
        </p>
      )}

      {/* MODAL */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Add Project</h3>

            <input
              type="text"
              placeholder="Project Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />

            <input
              type="text"
              placeholder="GitHub Repo URL"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
            />

            <div className="modal-actions">
              <button onClick={handleSubmit}>Submit</button>
              <button onClick={handleClear} className="secondary">
                Clear
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="danger"
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

export default Projects;
