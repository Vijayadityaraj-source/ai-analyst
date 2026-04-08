import * as XLSX from 'xlsx'
import type { ParsedFile, ColumnSchema, SheetRow, CellValue } from '../types/sheet'
import { inferType } from './inferType'

export function parseSheet(workbook: XLSX.WorkBook, sheetName: string): ParsedFile {
    const sheet = workbook.Sheets[sheetName] 
    const jsonData : SheetRow[] = XLSX.utils.sheet_to_json(sheet,{defval: null}); //{ defval: null } — this makes empty cells null instead of undefined, { raw: true} - keeps the original cell values as-is 
    const colNames = jsonData.length > 0 ? Object.keys(jsonData[0] as Object) : [];

    console.log(sheet)
    console.log(jsonData)
    console.log(colNames)

    const colData : ColumnSchema[] = colNames.map((col)=>{
        const colValues: CellValue[] = jsonData.map(row => {
            const val = row[col]
            // Strip Excel formulas — treat them as null
            if (typeof val === 'string' && val.startsWith('=')) return null
            return val
        })

        const sample: CellValue[] = [];
        for (const val of colValues) {
            if (val !== null && sample.length < 5) sample.push(val);
        }

        return {
            name : col,
            type : inferType(colValues),
            uniqueCount : [...new Set(colValues)].length,
            nullCount : colValues.filter(val=>val===null).length,
            sampleValues : sample
        }
    })

    const parsedFile : ParsedFile = {
        sheetName : sheetName,
        rowCount : jsonData.length,
        schema : colData,
        rows : jsonData
    }
    return parsedFile
}