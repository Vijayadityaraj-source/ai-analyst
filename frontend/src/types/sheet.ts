export type CellValue = string | number | Date | boolean | null
export type ColumnType = 'number' | 'string' | 'date' | 'boolean'
export type SheetRow = Record<string, CellValue>

export interface ColumnSchema {
  name: string
  type: ColumnType
  uniqueCount: number
  nullCount: number
  sampleValues: CellValue[]
}

export interface ParsedFile {
  sheetName: string
  rowCount: number
  schema: ColumnSchema[]
  rows: SheetRow[]
}

export interface SessionState {
  parsedFile: ParsedFile | null
  // chatHistory will go here in Phase 2
  // derivedLayers will go here in Phase 5
}