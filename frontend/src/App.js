import React, { useState, useRef } from "react";
import Editor from "@monaco-editor/react";
import ForceGraph3D from "react-force-graph-3d";
import * as THREE from "three";
import "./App.css";

function App() {

/* ============================= TEMPLATES ============================= */

const templates = {
  python: `# Python Template
def main():
    print("Hello Python")

if __name__ == "__main__":
    main()
`,
  c: `#include <stdio.h>
int main() {
    printf("Hello C\\n");
    return 0;
}`,
  cpp: `#include <iostream>
using namespace std;
int main() {
    cout << "Hello C++" << endl;
    return 0;
}`,
  java: `public class Main {
    public static void main(String[] args) {
        System.out.println("Hello Java");
    }
}`
};

/* ============================= STATE ============================= */

const [mode, setMode] = useState("analyze");
const [language, setLanguage] = useState("python");
const [code, setCode] = useState(templates.python);
const [codeB, setCodeB] = useState("");
const [userInput, setUserInput] = useState("");
const [result, setResult] = useState(null);
const [output, setOutput] = useState("");
const [comparisonResult, setComparisonResult] = useState(null);

const graphRef = useRef();

/* ============================= RUN ============================= */

const runCode = async () => {
  try {
    const res = await fetch("http://127.0.0.1:8000/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language, user_input: userInput })
    });

    const data = await res.json();

    let text = data.stderr
      ? "Error:\n" + data.stderr
      : data.stdout || "Program executed successfully (no output).";

    if (data.execution_time !== undefined) {
      text += `\n\n⏱ Execution Time: ${data.execution_time} sec`;
      text += `\n🧠 Memory Usage: ${data.memory_usage_kb} KB`;
      text += `\n📈 Runtime Hint: ${data.runtime_hint}`;
    }

    setOutput(text);
  } catch {
    setOutput("Backend connection failed.");
  }
};

/* ============================= ANALYZE ============================= */

const analyzeCode = async () => {
  if (language !== "python") {
    alert("Static analysis supported only for Python.");
    return;
  }

  const res = await fetch("http://127.0.0.1:8000/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, language })
  });

  const data = await res.json();
  setResult(data);
};

/* ============================= COMPARE ============================= */

const compareAlgorithms = async () => {
  const resA = await fetch("http://127.0.0.1:8000/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, language, user_input: userInput })
  });

  const resB = await fetch("http://127.0.0.1:8000/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: codeB, language, user_input: userInput })
  });

  const dataA = await resA.json();
  const dataB = await resB.json();

  setComparisonResult({ A: dataA, B: dataB });
};

/* ============================= CFG LOGIC ============================= */

const getNodeType = (label) => {
  const l = label.toLowerCase();
  if (l.includes("for") || l.includes("while")) return "loop";
  if (l.includes("if")) return "condition";
  if (l.includes("return")) return "return";
  if (l.includes("def")) return "function";
  return "default";
};

const getColor = (type) => {
  switch (type) {
    case "loop": return "#ff8800";
    case "condition": return "#ffd700";
    case "return": return "#00bfff";
    case "function": return "#bb86fc";
    default: return "#95a5a6";
  }
};

const buildStructuredNodes = () => {
  if (!result?.cfg) return [];
  return result.cfg.nodes.map((n, index) => ({
    id: n.id,
    name: n.label,
    lineno: n.lineno,
    type: getNodeType(n.label),
    x: 0,
    y: -index * 200,
    z: 0,
    fx: 0,
    fy: -index * 200,
    fz: 0
  }));
};

/* ============================= UI ============================= */

return (
<div style={containerStyle}>

<h1 style={headerStyle}>⚡ AlgoLens Neural AI Lab</h1>

<div style={modeSwitchStyle}>
  <button style={mode === "analyze" ? activeBtn : btn} onClick={()=>setMode("analyze")}>🧠 Analyze</button>
  <button style={mode === "compare" ? activeBtn : btn} onClick={()=>setMode("compare")}>⚔ Compare</button>
</div>

<select
  value={language}
  onChange={(e)=>{
    const selected = e.target.value;
    setLanguage(selected);
    setCode(templates[selected]);
    setResult(null);
  }}
  style={dropdownStyle}
>
  <option value="python">Python</option>
  <option value="c">C</option>
  <option value="cpp">C++</option>
  <option value="java">Java</option>
</select>

{/* ================= ANALYZE MODE ================= */}

{mode === "analyze" && (
<>
<div style={gridLayout}>
  <div>
    <Editor height="400px" language={language} theme="vs-dark" value={code} onChange={(v)=>setCode(v||"")} />
    <textarea placeholder="Enter input..." value={userInput} onChange={(e)=>setUserInput(e.target.value)} style={inputStyle}/>
  </div>

  <div style={terminalStyle}>
    <h3>🖥 Output</h3>
    {output}
  </div>
</div>

<div style={centerBtn}>
  <button style={analyzeBtn} onClick={analyzeCode}>Analyze</button>
  <button style={runBtn} onClick={runCode}>Run</button>
</div>

{/* ================= ANALYSIS CARDS ================= */}

{result && language === "python" && (
<>
<div style={cardStyle}><strong>Loop Depth:</strong> {result.loop_depth}</div>
<div style={cardStyle}><strong>Recursive Functions:</strong> {result.recursive_functions?.join(", ") || "None"}</div>
<div style={cardStyle}><strong>Estimated Complexity:</strong> {result.estimated_complexity}</div>
<div style={cardStyle}><strong>Cyclomatic Complexity:</strong> {result.cyclomatic_complexity}</div>
<div style={cardStyle}><strong>Quality Score:</strong> {result.quality_score} / 100</div>

<div style={cardStyle}>
  <h3>⚠ Issues</h3>
  {result.issues?.length > 0
    ? <ul>{result.issues.map((i,idx)=><li key={idx}>{i}</li>)}</ul>
    : <p>No major issues.</p>}
</div>

<div style={cardStyle}>
  <h3>💡 Suggestions</h3>
  {result.suggestions?.length > 0
    ? <ul>{result.suggestions.map((s,idx)=><li key={idx}>{s}</li>)}</ul>
    : <p>No suggestions.</p>}
</div>

{/* ================= STRUCTURED CFG ================= */}

<div style={{ height:"750px", marginTop:"40px" }}>
<ForceGraph3D
ref={graphRef}
cooldownTicks={0}
d3AlphaDecay={1}
d3VelocityDecay={1}
enableNodeDrag={false}
graphData={{ nodes: buildStructuredNodes(), links: result.cfg.edges }}
nodeThreeObject={(node)=>{
  const geo = new THREE.BoxGeometry(140, 40, 6);
  const mat = new THREE.MeshBasicMaterial({ color: getColor(node.type) });
  return new THREE.Mesh(geo, mat);
}}
linkColor={()=>"#00f0ff"}
linkWidth={4}
linkDirectionalArrowLength={8}
backgroundColor="#0b1020"
/>
</div>

</>
)}
</>
)}

{/* ================= COMPARE MODE ================= */}

{mode === "compare" && (
<>
<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"25px",marginTop:"40px"}}>
  <Editor height="350px" language={language} theme="vs-dark" value={code} onChange={(v)=>setCode(v||"")} />
  <Editor height="350px" language={language} theme="vs-dark" value={codeB} onChange={(v)=>setCodeB(v||"")} />
</div>

<div style={centerBtn}>
  <button style={runBtn} onClick={compareAlgorithms}>🚀 Run Battle</button>
</div>

{comparisonResult && (
<div style={battleCard}>
<h2>🏆 Battle Result</h2>

<p>⏱ A Time: {comparisonResult.A.execution_time ?? "N/A"} sec</p>
<p>⏱ B Time: {comparisonResult.B.execution_time ?? "N/A"} sec</p>
<p>🧠 A Memory: {comparisonResult.A.memory_usage_kb ?? "N/A"} KB</p>
<p>🧠 B Memory: {comparisonResult.B.memory_usage_kb ?? "N/A"} KB</p>

{(() => {
  const timeA = comparisonResult.A.execution_time;
  const timeB = comparisonResult.B.execution_time;

  if (timeA == null || timeB == null)
    return <h2 style={{color:"#ffaa00"}}>⚠ Comparison unavailable</h2>;

  const diff = Math.abs(timeA - timeB);
  const tolerance = 0.005;
  const percentDiff = ((diff / Math.max(timeA, timeB)) * 100).toFixed(2);

  if (diff < tolerance)
    return <>
      <h2 style={{color:"#00e6ff"}}>🤝 Tie (Almost Same Performance)</h2>
      <p>Performance Difference: {percentDiff}%</p>
    </>;

  const isAWinner = timeA < timeB;

  return <>
    <h2 style={{color:isAWinner ? "#00ff99" : "#ff4d4d"}}>
      {isAWinner ? "🚀 Algorithm A Wins" : "🚀 Algorithm B Wins"}
    </h2>
    <p>Performance Difference: {percentDiff}%</p>
  </>;
})()}

</div>
)}
</>
)}

</div>
);
}

/* ============================= STYLES ============================= */

const containerStyle={minHeight:"100vh",background:"radial-gradient(circle at top,#0f2027,#050b18 70%)",color:"white",padding:"40px",fontFamily:"JetBrains Mono"};
const headerStyle={textAlign:"center",fontSize:"42px",background:"linear-gradient(90deg,#00c6ff,#00ffcc)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"};
const modeSwitchStyle={textAlign:"center",margin:"25px 0"};
const btn={padding:"10px 20px",margin:"0 10px",borderRadius:"10px",background:"#111",color:"#aaa",border:"1px solid #444"};
const activeBtn={...btn,background:"linear-gradient(135deg,#00c6ff,#00ffcc)",color:"black"};
const dropdownStyle={padding:"10px",marginBottom:"20px",borderRadius:"8px",background:"#111",color:"white"};
const gridLayout={display:"grid",gridTemplateColumns:"2fr 1fr",gap:"20px"};
const inputStyle={width:"100%",marginTop:"15px",padding:"10px",borderRadius:"10px",background:"#111",color:"#00ffcc"};
const terminalStyle={background:"#000",color:"#00ff66",padding:"20px",borderRadius:"15px",whiteSpace:"pre-wrap"};
const centerBtn={textAlign:"center",marginTop:"20px"};
const analyzeBtn={padding:"12px 25px",marginRight:"10px",background:"linear-gradient(135deg,#00c6ff,#0072ff)",borderRadius:"12px",color:"white"};
const runBtn={padding:"12px 25px",background:"linear-gradient(135deg,#00ff99,#00cc66)",borderRadius:"12px",color:"black"};
const cardStyle={marginTop:"20px",padding:"20px",borderRadius:"15px",background:"rgba(255,255,255,0.05)"};
const battleCard={marginTop:"30px",padding:"30px",borderRadius:"20px",background:"rgba(255,255,255,0.07)",textAlign:"center"};

export default App;
