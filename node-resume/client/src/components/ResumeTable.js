import React from 'react'
import TextComponent from "./TextComponent"

export default function ResumeTable({ data }) {
    console.log('in Table page', data);

    return (
        <div>
            <div className="card">
                <div className="card-header">
                    <h4 className="card-title">Ranking Results</h4>
                    <p className="text-muted mb-0">
                        Below is the ranking results
                    </p>
                </div>{/* end card-header */}
                {data.length > 0 && (
                    <div className="card-body">
                        <div className="table-responsive">

                            <table className="table table-striped mb-0">
                            <caption>TS(Total Score) | SS(Skills Score) | ExS(Experience) | EdS(Education) | GS(General - Job Description to Resume)</caption>
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>File </th>
                                        <th>TS(100)</th>
                                        <th>SS(40)</th>
                                        <th>ExS(30)</th>
                                        <th>EdS(20)</th>
                                        <th>GS(10)</th>
                                        <th>Education</th>
                                        <th>Skills</th>
                                        <th>Experience</th>
                                        <th style={{ width: "310px" }}>Explanation</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.map((item, index) => (
                                        <tr key={index}>
                                            <th scope="row">{index + 1}</th>
                                            <td>{item.filename}</td>
                                            <td>{item.ts}</td>
                                            <td>{item.ss}</td>
                                            <td>{item.ex}</td>
                                            <td>{item.ed}</td>
                                            <td>{item.ge}</td>
                                            <td>{item.education}</td>
                                            <td>{item.skills}<br/><h6>Relevant skills - {item.r_skills}</h6></td>
                                            <td>{item.experience !== 0 ? `${item.experience} years` : null}</td>
                                            <td><TextComponent text={item.explanation} /></td>
                                        </tr>
                                    ))}

                                </tbody>
                            </table>{/* end /table */}
                        </div>{/* end /tableresponsive */}
                    </div>)} {/* end card-body */}
            </div>{/* end card */}

        </div>
    )
}