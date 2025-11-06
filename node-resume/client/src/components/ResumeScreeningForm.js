import { useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

export default function ResumeScreeningForm({ onResult }) {
  const [formData, setFormData] = useState({
    jobDescription: "",
    skills: "",
    education: "",
    experience: "",
    resumes: [],
  });

  const [resumeList, setResumeList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    setFormData({
      ...formData,
      resumes: files,
    });
    setResumeList(files);
  };

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    // Validation
    if (!formData.jobDescription || !formData.skills || !formData.education || !formData.experience) {
      setError("Please fill in all required fields");
      setLoading(false);
      return;
    }

    if (formData.resumes.length === 0) {
      setError("Please select at least one resume");
      setLoading(false);
      return;
    }

    const data = new FormData();
    data.append("jobDescription", formData.jobDescription);
    data.append("skills", formData.skills);
    data.append("education", formData.education);
    data.append("experience", formData.experience);
    formData.resumes.forEach((file) => {
      data.append("resumes", file);
    });

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: data,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const result = await response.json();

      if (onResult) {
        onResult(result);
      }
    } catch (err) {
      console.error("Error:", err);
      setError(err.message || "Failed to submit. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      <div className="row">
        <div className="col-md-12">
          <div className="form-group">
            <label htmlFor="job">Job Description *</label>
            <textarea
              className="form-control"
              rows="5"
              id="job"
              name="jobDescription"
              value={formData.jobDescription}
              onChange={handleChange}
              required
              disabled={loading}
            />
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-md-5">
          <div className="form-group">
            <label htmlFor="skills">Required Skills *</label>
            <textarea
              className="form-control"
              rows="5"
              id="skills"
              name="skills"
              value={formData.skills}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="e.g., JavaScript, React, Node.js"
            />
          </div>
        </div>
        <div className="col-md-7">
          <div className="form-group">
            <label htmlFor="education">Education/Qualifications *</label>
            <input
              className="form-control"
              type="text"
              id="education"
              name="education"
              value={formData.education}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="e.g., Bachelor's Degree in Computer Science"
            />
          </div>
          <div className="form-group">
            <label htmlFor="experience">Required Experience *</label>
            <input
              className="form-control"
              type="text"
              id="experience"
              name="experience"
              value={formData.experience}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="e.g., 3 years"
            />
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-md-12">
          <div className="custom-file mb-3">
            <input
              type="file"
              className="custom-file-input"
              name="resumes"
              onChange={handleFileChange}
              multiple
              id="customFile"
              accept=".pdf"
              disabled={loading}
              required
            />
            <label className="custom-file-label" htmlFor="customFile">
              {resumeList.length > 0 ? `${resumeList.length} file(s) selected` : 'Select resumes (PDF)'}
            </label>
          </div>
        </div>
        {resumeList.length > 0 && (
          <div className="col-lg-8">
            <ul className="list-group">
              {resumeList.map((file, index) => (
                <li key={index} className="list-group-item">
                  <i className="la la-angle-double-right text-info mr-2"></i>
                  {file.name}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      <div className="row mt-3">
        <div className="col-sm-12 text-right">
          <button
            type="submit"
            className="btn btn-primary px-4"
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Submit'}
          </button>
        </div>
      </div>
    </form>
  );
}
