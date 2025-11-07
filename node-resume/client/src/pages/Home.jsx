import React, { useState } from 'react';
import Layout from '../components/Layout';
import ResumeScreeningForm from '../components/ResumeScreeningForm';
import ResumeTable from '../components/ResumeTable';

function Home() {
  const [tableData, setTableData] = useState([]);

  const handleResult = (result) => {
    // Handle new API response format with results array
    if (result && result.results && Array.isArray(result.results)) {
      setTableData([...result.results]);
    } else if (result && Array.isArray(result)) {
      // Fallback for old format
      setTableData([...result]);
    }
  };

  return (
    <Layout>
      <div className="row">
        <div className="col-sm-12">
          <div className="page-title-box">
            <div className="row">
              <div className="col">
                <h4 className="page-title">Resume Screening System</h4>
                <ol className="breadcrumb">
                  <li className="breadcrumb-item"><a href="/">Home</a></li>
                  <li className="breadcrumb-item active">Dashboard</li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-lg-12">
          <div className="card">
            <div className="card-header">
              <h4 className="card-title">AI Resume Screening by Job Description</h4>
              <p className="text-muted mb-0">Automated candidate ranking system</p>
            </div>
            <div className="card-body">
              <ResumeScreeningForm onResult={handleResult} />
            </div>
          </div>
        </div>

        <div className="col-lg-12">
          <ResumeTable data={tableData} />
        </div>
      </div>
    </Layout>
  );
}

export default Home;
