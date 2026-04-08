import { useState } from "react";
import * as XLSX from "xlsx";
import "./App.css";
import { parseSheet } from "./utils/parseSheet";

function App() {
  const [data, setData] = useState<any>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = (event) => {
      const binaryStr = event.target?.result;
      if (!binaryStr) return;

      const workbook = XLSX.read(binaryStr, { type: "binary", cellDates: true});

      const sheetName = workbook.SheetNames[0];

      const parsed = parseSheet(workbook, sheetName);

      console.log("Parsed Sheet:", parsed);
      setData(parsed);
    };

    reader.readAsBinaryString(file);
  };

  return (
    <div style={{ padding: "40px" }}>
      <h2>Upload Excel File</h2>

      <input
        type="file"
        accept=".xlsx,.xls"
        onChange={handleFileUpload}
      />

      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export default App;