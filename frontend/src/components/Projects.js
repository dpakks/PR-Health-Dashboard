import React, { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";

export default function Projects() {
  const [role, setRole] = useState("");
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const decoded = jwtDecode(token);
    setRole(decoded.role);

    // TEMP MOCK DATA (replace with API later)
    if (decoded.role === "ADMIN") {
      setProjects([
        { id: 1, name: "Marketing" },
        { id: 2, name: "Feature lists" },
        { id: 3, name: "boardme development" },
        { id: 4, name: "UIDD development" },
      ]);
    } else {
      // Tech Lead example
      setProjects([]); // try empty & non-empty cases
    }
  }, []);

  return (
    <div className="projects-page">
      <h2 className="projects-title">Projects</h2>

      {projects.length === 0 && role !== "ADMIN" ? (
        <p className="no-projects">
          No projects assigned for you
        </p>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div key={project.id} className="project-card">
              <div className="project-avatar">
                {project.name[0].toUpperCase()}
              </div>
              <span className="project-name">{project.name}</span>
            </div>
          ))}

          {/* Add Project Card (ADMIN ONLY) */}
          {role === "ADMIN" && (
            <div className="project-card add-project">
              <div className="project-avatar add">+</div>
              <span className="project-name">Add a project</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
