import { useState } from "react";

export default function ResumeScreeningForm({ onResult }) {
  const [formData, setFormData] = useState({
    jobDescription: "",
    skills: "",
    education: "",
    experience: "",
    resumes: [],
  });

  // State for selected resumes (files)
  const [resume_list, setResume_list] = useState([]);

  const handleFileChange = (event) => {
    setFormData({
      ...formData,
      resumes: [...event.target.files],
    });
    const files = event.target.files
    const fileList = Array.from(files); // Convert FileList to an array
    setResume_list(fileList); // Update state with the selected files
  };

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const data = new FormData();
    data.append("jobDescription", formData.jobDescription);
    data.append("skills", formData.skills);
    data.append("education", formData.education);
    data.append("experience", formData.experience);
    formData.resumes.forEach((file) => {
      data.append("resumes", file);
    });

    try {
      const response = await fetch("http://localhost:3001/upload", {
        method: "POST",
        body: data,
      });
      const result = await response.json();
      console.log("Success:", result);

      if (onResult) {
        onResult(result); // Pass data to Home.jsx
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <form className="" onSubmit={handleSubmit}>
      <div className="row">
        <div className="col-md-12">
          <div className="form-group">
            <label htmlFor="message">Job Description</label>
            <textarea className="form-control"
              rows="5" id="job"
              name="jobDescription"
              value={formData.jobDescription}
              onChange={handleChange} />
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-md-5">
          <div className="form-group">
            <label htmlFor="message">Required skills</label>
            <textarea className="form-control" rows="5"
              id="skills"
              name="skills"
              value={formData.skills}
              onChange={handleChange} />
          </div>
        </div>
        <div className="col-md-7">
          <div className="form-group">
          <label htmlFor="message">Education/Qualifications</label>
            <input className="form-control" type="text"
              id="education"
              name="education"
              value={formData.education}
              onChange={handleChange} />
          </div>
          <div className="form-group">
          <label htmlFor="message">Required Experience</label>
            <input className="form-control" type="text"
              id="experience"
              name="experience"
              value={formData.experience}
              onChange={handleChange} />
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-md-12">
          <div className="custom-file mb-3">
            <input type="file" className="custom-file-input" name="resumes" onChange={handleFileChange} multiple id="customFile" />
            <label className="custom-file-label" htmlFor="customFile">Select resumes (pdf)</label>
          </div>
        </div>
        {resume_list.length > 0 && (
          <div class="col-lg-8">
            <ul class="list-group l">
              {resume_list.map((file, index) => (
                <li key={index} class="list-group-item"><i class="la la-angle-double-right text-info mr-2"></i>{file.name} </li>
              ))}
            </ul>
          </div>)} {/*  end col */}
      </div>
      <div className="row">
        <div className="col-sm-12 text-right">
          <button type="submit" className="btn btn-primary px-4">Submit</button>
        </div>
      </div>
    </form>
  );
}
