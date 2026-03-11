import { useEffect, useState } from "react";
import { getProjects, createProject } from "../services/projectService";
import { useNavigate } from "react-router-dom";

const COLORS = ["#60a5fa", "#fb7185", "#fbbf24", "#a855f7", "#34d399"];

function Projects() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [errors, setErrors] = useState({});
  const role = localStorage.getItem("role");

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

  const getInitials = (name) =>
    name
      .split(" ")
      .map((w) => w[0])
      .join("")
      .toUpperCase();

  const handleSubmit = async () => {
    const newErrors = {};

    if (!name.trim()) newErrors.name = "This field is required";
    if (!repoUrl.trim()) newErrors.repoUrl = "This field is required";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
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
      setErrors({});
      fetchProjects();
    } catch (error) {
      console.error("Project creation failed", error);
    }
  };

  const handleClear = () => {
    setName("");
    setRepoUrl("");
    setErrors({});
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setName("");
    setRepoUrl("");
    setErrors({});
  };

  return (
    <div className="projects-container">
      <h2 className="projects-title">Projects</h2>

      <div className="projects-grid">
        {projects.map((project, index) => (
          <div
            key={project.id}
            className="project-card"
            onClick={() => navigate(`/projects/${project.id}`)}
          >
            <div
              className="project-icon"
              style={{ background: COLORS[index % COLORS.length] }}
            >
              {getInitials(project.name)}
            </div>
            <p className="project-name">{project.name}</p>
          </div>
        ))}

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

      {role !== "ADMIN" && projects.length === 0 && (
        <p className="no-projects">No projects assigned for you</p>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Add Project</h3>

            <input
              type="text"
              placeholder="Project Name"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setErrors((prev) => ({ ...prev, name: "" }));
              }}
              className={errors.name ? "input-error" : ""}
            />
            {errors.name && <div className="field-error">{errors.name}</div>}

            <input
              type="text"
              placeholder="GitHub Repo URL"
              value={repoUrl}
              onChange={(e) => {
                setRepoUrl(e.target.value);
                setErrors((prev) => ({ ...prev, repoUrl: "" }));
              }}
              className={errors.repoUrl ? "input-error" : ""}
            />
            {errors.repoUrl && (
              <div className="field-error">{errors.repoUrl}</div>
            )}

            <div className="modal-actions">
              <button onClick={handleSubmit}>Submit</button>
              <button onClick={handleClear} className="secondary">
                Clear
              </button>
              <button onClick={handleCloseModal} className="danger">
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