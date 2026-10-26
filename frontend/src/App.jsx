import { useEffect, useState } from "react";
import { api } from "./api";

const today = new Date().toISOString().slice(0, 10);
const emptyStudent = { student_id: "", name: "", department: "", academic_year: "" };
const emptyCourse = { course_id: "", course_name: "" };

function App() {
  const [students, setStudents] = useState([]);
  const [courses, setCourses] = useState([]);
  const [records, setRecords] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [student, setStudent] = useState(emptyStudent);
  const [course, setCourse] = useState(emptyCourse);
  const [attendance, setAttendance] = useState({ student_id: "", course_id: "", attendance_date: today, status: "Present" });
  const [filterDate, setFilterDate] = useState(today);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadData(date = filterDate) {
    setLoading(true);
    try {
      const [studentData, courseData, recordData, stats] = await Promise.all([
        api("/students"), api("/courses"), api(`/attendance?attendance_date=${date}`), api(`/dashboard?selected_date=${date}`)
      ]);
      setStudents(studentData); setCourses(courseData); setRecords(recordData); setDashboard(stats);
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  }
  useEffect(() => { loadData(); }, []);

  async function submit(path, body, reset, success) {
    setError(""); setMessage("");
    try { await api(path, { method: "POST", body: JSON.stringify(body) }); reset(); setMessage(success); await loadData(); }
    catch (e) { setError(e.message); }
  }

  return <main>
    <header><div><p className="eyebrow">COLLEGE ATTENDANCE</p><h1>Attendance dashboard</h1><p className="muted">Manage students, courses, and daily attendance in one place.</p></div></header>
    {(message || error) && <div className={error ? "alert error" : "alert success"}>{error || message}</div>}
    <section className="stats">
      {[
        ["Students", dashboard?.total_students ?? "—"], ["Courses", dashboard?.total_courses ?? "—"],
        ["Recorded today", dashboard?.records_for_date ?? "—"], ["Present / Absent", dashboard ? `${dashboard.present_count} / ${dashboard.absent_count}` : "—"]
      ].map(([label, value]) => <div className="stat" key={label}><span>{label}</span><strong>{value}</strong></div>)}
    </section>
    <section className="grid">
      <form className="card" onSubmit={(e) => { e.preventDefault(); submit("/students", student, () => setStudent(emptyStudent), "Student added successfully."); }}>
        <h2>Add student</h2><Field label="Student ID" value={student.student_id} onChange={(v) => setStudent({...student, student_id: v})} />
        <Field label="Name" value={student.name} onChange={(v) => setStudent({...student, name: v})} /><Field label="Department" value={student.department} onChange={(v) => setStudent({...student, department: v})} />
        <Field label="Academic year" value={student.academic_year} onChange={(v) => setStudent({...student, academic_year: v})} /><button>Add student</button>
      </form>
      <form className="card" onSubmit={(e) => { e.preventDefault(); submit("/courses", course, () => setCourse(emptyCourse), "Course added successfully."); }}>
        <h2>Add course</h2><Field label="Course ID" value={course.course_id} onChange={(v) => setCourse({...course, course_id: v})} /><Field label="Course name" value={course.course_name} onChange={(v) => setCourse({...course, course_name: v})} /><button>Add course</button>
      </form>
      <form className="card" onSubmit={(e) => { e.preventDefault(); submit("/attendance", {...attendance, student_id: Number(attendance.student_id), course_id: Number(attendance.course_id)}, () => setAttendance({...attendance, student_id: "", course_id: ""}), "Attendance saved successfully."); }}>
        <h2>Mark attendance</h2><Select label="Student" value={attendance.student_id} options={students.map(s => [s.id, `${s.student_id} — ${s.name}`])} onChange={(v) => setAttendance({...attendance, student_id: v})} />
        <Select label="Course" value={attendance.course_id} options={courses.map(c => [c.id, `${c.course_id} — ${c.course_name}`])} onChange={(v) => setAttendance({...attendance, course_id: v})} />
        <Field label="Date" type="date" value={attendance.attendance_date} onChange={(v) => setAttendance({...attendance, attendance_date: v})} />
        <Select label="Status" value={attendance.status} options={[["Present", "Present"], ["Absent", "Absent"]]} onChange={(v) => setAttendance({...attendance, status: v})} /><button>Save attendance</button>
      </form>
    </section>
    <section className="card records"><div className="section-heading"><div><h2>Attendance records</h2><p className="muted">Filter records by date.</p></div><input type="date" value={filterDate} onChange={(e) => { setFilterDate(e.target.value); loadData(e.target.value); }} /></div>
      {loading ? <p className="muted">Loading records…</p> : records.length === 0 ? <p className="empty">No attendance records for this date.</p> :
      <div className="table-wrap"><table><thead><tr><th>Date</th><th>Student</th><th>Course</th><th>Status</th></tr></thead><tbody>{records.map(r => <tr key={r.id}><td>{r.attendance_date}</td><td>{r.student.name}<small>{r.student.student_id}</small></td><td>{r.course.course_name}<small>{r.course.course_id}</small></td><td><span className={`badge ${r.status.toLowerCase()}`}>{r.status}</span></td></tr>)}</tbody></table></div>}
    </section>
  </main>;
}

function Field({ label, value, onChange, type = "text" }) { return <label>{label}<input required type={type} value={value} onChange={(e) => onChange(e.target.value)} /></label>; }
function Select({ label, value, options, onChange }) { return <label>{label}<select required value={value} onChange={(e) => onChange(e.target.value)}><option value="">Select {label.toLowerCase()}</option>{options.map(([id, name]) => <option value={id} key={id}>{name}</option>)}</select></label>; }
export default App;
