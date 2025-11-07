import React from 'react';

const Layout = ({ children }) => {
  return (
    <div>
      <div className="left-sidenav">
        <div className="brand">
          <a href="/" className="logo">
            <h2>RESUME SCREENING</h2>
          </a>
        </div>

        <div className="menu-content h-100" data-simplebar>
          <ul className="metismenu left-sidenav-menu">
            <li>
              <a href="/">
                <i data-feather="home" className="align-self-center menu-icon"></i>
                <span>Dashboard</span>
                <span className="menu-arrow">
                  <i className="mdi mdi-chevron-right"></i>
                </span>
              </a>
              <ul className="nav-second-level">
                <li className="nav-item">
                  <a className="nav-link" href="/">
                    <i className="ti-control-record"></i>Resume screening
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>

      <div className="page-wrapper">
        <div className="page-content">
          <div className="container-fluid">
            {children}
          </div>

          <footer className="footer text-center text-sm-left">
            &copy; 2025 Anne{' '}
            <span className="d-none d-sm-inline-block float-right">
              Developed by <i className="mdi mdi-heart text-danger"></i> Anne Ezurike
            </span>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default Layout;
