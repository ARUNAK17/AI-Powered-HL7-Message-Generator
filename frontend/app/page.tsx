"use client";

import { FormEvent, useState } from "react";

type Validation = {
  valid: boolean;
  message_type?: string | null;
  errors: string[];
  warnings: string[];
  segments: {
    line: number;
    segment: string;
    field_count: number;
  }[];
};

type GenerateResponse = {
  hl7_message: string;
  validation: Validation;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [form, setForm] = useState({
    message_type: "ADT^A01",
    patient_id: "P10001",
    patient_name: "DOE^JOHN",
    date_of_birth: "19900115",
    sex: "M",
    admission_date: "20260928103000",
    hospital: "Demo General Hospital",
    doctor: "SMITH^JANE",
    diagnosis: "Pneumonia",
    observation: "Temperature 38.2 C"
  });

  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function updateField(name: string, value: string) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function generate(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(form)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Generation failed.");
      }

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <header className="header">
        <h1>AI-Powered HL7 Message Generator</h1>
        <p>
          Generate structured HL7 v2 ADT and ORU messages using OpenAI,
          then validate the generated segments before using them in testing.
        </p>
      </header>

      <div className="grid">
        <section className="card">
          <h2>Patient Input</h2>

          <form onSubmit={generate}>
            <div className="field">
              <label>Message Type</label>
              <select
                value={form.message_type}
                onChange={(e) =>
                  updateField("message_type", e.target.value)
                }
              >
                <option value="ADT^A01">ADT^A01 - Admission</option>
                <option value="ORU^R01">ORU^R01 - Observation Result</option>
              </select>
            </div>

            <div className="field">
              <label>Patient ID</label>
              <input
                value={form.patient_id}
                onChange={(e) => updateField("patient_id", e.target.value)}
                required
              />
            </div>

            <div className="field">
              <label>Patient Name</label>
              <input
                value={form.patient_name}
                onChange={(e) => updateField("patient_name", e.target.value)}
                required
              />
            </div>

            <div className="field">
              <label>Date of Birth</label>
              <input
                value={form.date_of_birth}
                onChange={(e) => updateField("date_of_birth", e.target.value)}
                required
              />
            </div>

            <div className="field">
              <label>Sex</label>
              <select
                value={form.sex}
                onChange={(e) => updateField("sex", e.target.value)}
              >
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="O">Other</option>
              </select>
            </div>

            <div className="field">
              <label>Admission / Event Date Time</label>
              <input
                value={form.admission_date}
                onChange={(e) =>
                  updateField("admission_date", e.target.value)
                }
                required
              />
            </div>

            <div className="field">
              <label>Hospital</label>
              <input
                value={form.hospital}
                onChange={(e) => updateField("hospital", e.target.value)}
                required
              />
            </div>

            <div className="field">
              <label>Doctor</label>
              <input
                value={form.doctor}
                onChange={(e) => updateField("doctor", e.target.value)}
                required
              />
            </div>

            <div className="field">
              <label>Diagnosis</label>
              <input
                value={form.diagnosis}
                onChange={(e) => updateField("diagnosis", e.target.value)}
                required
              />
            </div>

            <div className="field">
              <label>Observation</label>
              <textarea
                value={form.observation}
                onChange={(e) =>
                  updateField("observation", e.target.value)
                }
              />
            </div>

            <button className="button" disabled={loading}>
              {loading ? "Generating..." : "Generate HL7 Message"}
            </button>
          </form>
        </section>

        <section className="card">
          <h2>Generated HL7 Message</h2>

          {error && <div className="status invalid">{error}</div>}

          {!result && !error && (
            <p className="muted">
              Enter the patient details and generate a message.
            </p>
          )}

          {result && (
            <>
              <div
                className={`status ${
                  result.validation.valid ? "valid" : "invalid"
                }`}
              >
                {result.validation.valid
                  ? "✓ HL7 validation passed"
                  : "✕ HL7 validation failed"}
              </div>

              <pre className="message">{result.hl7_message}</pre>

              {result.validation.errors.length > 0 && (
                <>
                  <h3>Validation Errors</h3>
                  <ul className="validation-list error">
                    {result.validation.errors.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </>
              )}

              {result.validation.warnings.length > 0 && (
                <>
                  <h3>Warnings</h3>
                  <ul className="validation-list warning">
                    {result.validation.warnings.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </>
              )}

              <h3>Segment Summary</h3>

              <table className="segment-table">
                <thead>
                  <tr>
                    <th>Line</th>
                    <th>Segment</th>
                    <th>Fields</th>
                  </tr>
                </thead>
                <tbody>
                  {result.validation.segments.map((segment) => (
                    <tr key={`${segment.line}-${segment.segment}`}>
                      <td>{segment.line}</td>
                      <td>{segment.segment}</td>
                      <td>{segment.field_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
