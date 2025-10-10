import React from 'react'
import { useState } from "react";
import ResumeScreeningForm from '../components/ResumeScreeningForm'
import ResumeTable from '../components/ResumeTable';

function Home() {
    const [tableData, setTableData] = useState([]);
    const handleResult = (result) => {
        console.log('Data received in Home.jsx', result);

        if (result && result) {
            setTableData([...result]);
        }
        
    };
    
    return (
        <div>
            <div className="left-sidenav">
                {/*  LOGO */}
                <div className="brand">
                    <a href="/" className="logo">
                        
                        <h2>RESUME SCREENING</h2> 
                    </a>
                </div>
                {/* end logo*/}

                <div className="menu-content h-100" data-simplebar>
                    <ul className="metismenu left-sidenav-menu">
                        
                        <li>
                            <a href="/"> <i data-feather="home" className="align-self-center menu-icon"></i><span>Dashboard</span><span className="menu-arrow"><i className="mdi mdi-chevron-right"></i></span></a>
                            <ul className="nav-second-level" aria-expanded="false">
                                <li className="nav-item"><a className="nav-link" href="/"><i className="ti-control-record"></i>Resume screening</a></li>
                                
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>

            <div className="page-wrapper">
        
            {/*  Page Content */}
            <div className="page-content">
                <div className="container-fluid">
                    {/*  Page-Title  */}
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
                                    </div>{/* end col */}
                                    
                                </div>{/* end row */}                                                              
                            </div>{/* end page-title-box */}
                        </div>{/* end col */}
                    </div>{/* end row */}
                    {/*  end page title end breadcrumb  */}
                    
                    
                    
                    <div className="row">
                    <div className="col-lg-12">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Optimised AI Resume screening by job descriptions</h4>
                                    <p className="text-muted mb-0">Ranking system </p>
                                </div>{/* end card-header */}
                                <div className="card-body">
                                    <ResumeScreeningForm onResult={handleResult}/>
                                </div>{/* end card-body */}
                            </div>{/* end card */}
                            
                        </div> {/*  end col  */}     
                        <div className="col-lg-12">
                            <ResumeTable data={tableData} />
                        </div> {/* end col */}                                                   
                    </div>{/* end row */}
                    
                </div>{/*  container  */}

                <footer className="footer text-center text-sm-left">
                    &copy; 2025 Anne <span className="d-none d-sm-inline-block float-right">Developed by <i className="mdi mdi-heart text-danger"></i> Anne Ezurike</span>
                </footer>{/* end footer */}
            </div>
            {/*  end page content  */}
        </div>
        {/*  end page-wrapper  */}
        </div>
    )
}

export default Home